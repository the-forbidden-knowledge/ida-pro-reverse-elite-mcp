#!/usr/bin/env python3
"""Monta jail mínima (chroot) a partir de lista de dependências.

Disciplina agressiva: diretórios 0o111 (só atravessar), bibliotecas 0o555,
configs 0o444. Segredos reais (ex.: shadow) nunca entram na jail.
"""

import argparse
import json
import os
import stat
import sys

MODE_DIR = 0o111
MODE_LIB = 0o555
MODE_CONFIG = 0o444

PROIBIDOS = {"shadow", "gshadow", "master.passwd"}


def _seguro(rel):
    return rel and not rel.startswith("/") and ".." not in rel.split("/")


def plan_jail(deps):
    """Gera o manifesto: [(relpath, kind, mode)]."""
    manifesto = []
    vistos = set()

    def add(rel, kind, mode):
        if rel in vistos or not _seguro(rel):
            return
        base = os.path.basename(rel)
        if base in PROIBIDOS:
            return
        vistos.add(rel)
        manifesto.append({"path": rel, "kind": kind, "mode": oct(mode)})

    for dep in deps:
        caminho = dep.get("caminho", "")
        if os.path.basename(caminho) in PROIBIDOS:
            continue
        tipo = dep.get("tipo", "arquivo")
        rel = caminho.lstrip("/")
        partes = rel.split("/")[:-1]
        acum = ""
        for p in partes:
            acum = p if not acum else acum + "/" + p
            add(acum, "dir", MODE_DIR)
        if tipo == "biblioteca":
            add(rel, "lib", MODE_LIB)
        elif tipo == "dispositivo":
            add(rel, "device", MODE_LIB)
        else:
            add(rel, "config", MODE_CONFIG)
    return manifesto


def build_jail(raiz, manifesto):
    """Cria a árvore (placeholders vazios) com os modos do manifesto."""
    for item in manifesto:
        alvo = os.path.join(raiz, item["path"])
        if item["kind"] == "dir":
            os.makedirs(alvo, exist_ok=True)
            os.chmod(alvo, int(item["mode"], 8))
        else:
            os.makedirs(os.path.dirname(alvo), exist_ok=True)
            with open(alvo, "wb"):
                pass
            os.chmod(alvo, int(item["mode"], 8))


def verify_jail(raiz, manifesto):
    """Confere existência e modos; retorna lista de problemas."""
    problemas = []
    for item in manifesto:
        alvo = os.path.join(raiz, item["path"])
        if not os.path.lexists(alvo):
            problemas.append({"path": item["path"], "erro": "ausente"})
            continue
        modo = stat.S_IMODE(os.lstat(alvo).st_mode)
        if modo != int(item["mode"], 8):
            problemas.append({"path": item["path"], "erro": "modo",
                              "esperado": item["mode"], "atual": oct(modo)})
    return problemas


def main(argv=None):
    ap = argparse.ArgumentParser(description="Monta jail mínima chroot")
    ap.add_argument("deps", help="JSON com lista de dependências")
    ap.add_argument("destino", help="diretório raiz da jail")
    ap.add_argument("--manifesto", help="grava o manifesto JSON aqui")
    args = ap.parse_args(argv)
    with open(args.deps, encoding="utf-8") as f:
        deps = json.load(f)
    if isinstance(deps, dict):
        deps = deps.get("dependencias", [])
    manifesto = plan_jail(deps)
    build_jail(args.destino, manifesto)
    problemas = verify_jail(args.destino, manifesto)
    resultado = {"manifesto": manifesto, "problemas": problemas,
                 "ok": not problemas}
    texto = json.dumps(resultado, indent=2, ensure_ascii=False)
    if args.manifesto:
        with open(args.manifesto, "w", encoding="utf-8") as f:
            f.write(texto)
    else:
        print(texto)
    return 0 if resultado["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
