#!/usr/bin/env python3
"""Mapa automount: wildcard + bind mounts + macro &.

Um único mapa serve N sandboxes idênticas: wildcard `*` casa qualquer chave,
múltiplos mounts executam em ordem, bind mounts locais usam prefixo `:`,
e a macro `&` substitui o nome casado.
"""

import argparse
import json
import re
import sys

RE_ENTRY = re.compile(r"^(?P<key>\*|\S+)\s+(?P<body>.+)$")


def parse_map(texto):
    """Parse do mapa. Cada entrada: key_pattern + lista de mounts."""
    entradas = []
    logicas = []
    for linha in texto.splitlines():
        s = linha.strip()
        if not s or s.startswith("#"):
            continue
        if s.endswith("\\"):
            logicas.append(s[:-1].rstrip())
            continue
        if logicas:
            logicas.append(s)
            s = " ".join(logicas)
            logicas = []
        m = RE_ENTRY.match(s)
        if not m:
            continue
        entradas.append({"key": m.group("key"), "mounts": _parse_mounts(m.group("body"))})
    return entradas


def _parse_mounts(body):
    """Divide o corpo em mounts: '/' <path> <fonte> ... (múltiplos, em ordem)."""
    mounts = []
    # cada mount começa com um path absoluto
    partes = re.split(r"\s+(?=/)", body.strip())
    for p in partes:
        toks = p.split()
        if len(toks) >= 2:
            mounts.append({"path": toks[0], "source": toks[1],
                           "bind": toks[1].startswith(":")})
    return mounts


def resolve(entrada, chave):
    """Expande a macro & e retorna os mounts resolvidos em ordem."""
    if entrada["key"] != "*" and entrada["key"] != chave:
        return None
    resolvidos = []
    for mnt in entrada["mounts"]:
        src = mnt["source"].replace("&", chave)
        path = mnt["path"].replace("&", chave)
        resolvidos.append({"path": path, "source": src, "bind": mnt["bind"],
                           "caveat": ("bind não aceita opções próprias; "
                                      "herda as do FS original") if mnt["bind"] else None})
    return resolvidos


def sandbox_for(entradas, chave):
    """Layout do sandbox para a chave (ex.: usuário)."""
    for ent in entradas:
        r = resolve(ent, chave)
        if r is not None:
            return {"key": chave, "mounts": r}
    return {"key": chave, "mounts": [], "erro": "sem entrada casada"}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Resolve mapa automount")
    ap.add_argument("mapa", help="arquivo do mapa")
    ap.add_argument("chave", help="chave a resolver (ex.: usuário)")
    ap.add_argument("-o", "--saida", help="grava JSON neste arquivo")
    args = ap.parse_args(argv)
    with open(args.mapa, encoding="utf-8") as f:
        entradas = parse_map(f.read())
    resultado = sandbox_for(entradas, args.chave)
    texto = json.dumps(resultado, indent=2, ensure_ascii=False)
    if args.saida:
        with open(args.saida, "w", encoding="utf-8") as f:
            f.write(texto)
    else:
        print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
