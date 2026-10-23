#!/usr/bin/env python3
"""Oráculo de dependências via log strace.

Analisa um log do strace e extrai as dependências de runtime de um binário
black-box: o último ENOENT costuma ser o fatal. Cada falha revela uma
dependência ausente (open/openat -> arquivo/dispositivo/config;
execve -> binário ausente).
"""

import argparse
import json
import re
import sys

# openat(AT_FDCWD, "/caminho", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
RE_CALL = re.compile(
    r"^(?P<pid>\d+)\s+(?P<syscall>\w+)\((?P<args>.*)\)\s+=\s+(?P<ret>-?\d+|0x[0-9a-f]+)"
    r"(?:\s+(?P<errno>[A-Z]+)(?:\s+\(.*\))?)?"
)
RE_STR = re.compile(r'"((?:[^"\\]|\\.)*)"')
RE_EXIT = re.compile(r"^(?:\d+\s+)?(?:exit_group|exit)\(")


def parse_strace(texto):
    """Extrai eventos do log. Cada evento: pid, syscall, caminho, retorno, errno."""
    eventos = []
    for linha in texto.splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("+++"):
            continue
        if RE_EXIT.match(linha):
            eventos.append({"tipo": "exit", "linha": linha})
            continue
        m = RE_CALL.match(linha)
        if not m:
            continue
        d = m.groupdict()
        strs = RE_STR.findall(d["args"])
        caminho = strs[0] if strs else None
        eventos.append({
            "tipo": "call",
            "pid": d["pid"],
            "syscall": d["syscall"],
            "caminho": caminho,
            "ret": d["ret"],
            "errno": d.get("errno"),
        })
    return eventos


def enoents_fatais(eventos, janela=40):
    """Coleta os ENOENTs na janela final antes do exit (o último costuma ser fatal)."""
    idx_exit = None
    for i, ev in enumerate(eventos):
        if ev["tipo"] == "exit":
            idx_exit = i
    fim = idx_exit if idx_exit is not None else len(eventos)
    inicio = max(0, fim - janela)
    return [ev for ev in eventos[inicio:fim]
            if ev["tipo"] == "call" and ev["errno"] == "ENOENT" and ev["caminho"]]


def classificar(evento):
    """Classifica a dependência: arquivo, biblioteca, dispositivo ou binário."""
    caminho = evento["caminho"]
    sc = evento["syscall"]
    if sc == "execve":
        return {"tipo": "binario", "caminho": caminho}
    if caminho.startswith("/dev/"):
        return {"tipo": "dispositivo", "caminho": caminho}
    if caminho.endswith(".so") or ".so." in caminho or "/lib" in caminho or "/lib64" in caminho:
        return {"tipo": "biblioteca", "caminho": caminho}
    return {"tipo": "arquivo", "caminho": caminho}


def oraculo_dependencias(texto, janela=40):
    """Pipeline completo: parse -> ENOENTs fatais -> lista de dependências única."""
    eventos = parse_strace(texto)
    fatais = enoents_fatais(eventos, janela=janela)
    vistas = set()
    dependencias = []
    for ev in fatais:
        dep = classificar(ev)
        chave = (dep["tipo"], dep["caminho"])
        if chave not in vistas:
            vistas.add(chave)
            dependencias.append(dep)
    fatal = dependencias[-1] if dependencias else None
    return {"dependencias": dependencias, "fatal": fatal,
            "total_enoent": len(fatais)}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Oráculo de dependências via strace")
    ap.add_argument("log", help="arquivo de log do strace")
    ap.add_argument("--janela", type=int, default=40,
                    help="linhas finais antes do exit (padrão: 40)")
    ap.add_argument("-o", "--saida", help="grava JSON neste arquivo")
    args = ap.parse_args(argv)
    with open(args.log, encoding="utf-8", errors="replace") as f:
        resultado = oraculo_dependencias(f.read(), janela=args.janela)
    texto = json.dumps(resultado, indent=2, ensure_ascii=False)
    if args.saida:
        with open(args.saida, "w", encoding="utf-8") as f:
            f.write(texto)
    else:
        print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
