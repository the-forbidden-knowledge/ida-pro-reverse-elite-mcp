#!/usr/bin/env python3
"""Resolução recursiva de DT_NEEDED.

O `ldd` lista só dependências diretas — as transitivas ficam ocultas
(ex.: libnss, necessária em runtime mas ausente do DT_NEEDED). Este lab
resolve a árvore completa em cascata e detecta dependências ocultas
vistas em runtime mas fora da closure estática.
"""

import argparse
import json
import sys


def naive_ldd(libdb, raiz):
    """Imita o ldd: só as dependências diretas."""
    return sorted(libdb.get(raiz, {}).get("needed", []))


def resolve_recursive(libdb, raiz):
    """BFS com proteção contra ciclos: todas as transitivas, ordem estável."""
    vistas = set()
    fila = [raiz]
    ordem = []
    while fila:
        atual = fila.pop(0)
        for dep in libdb.get(atual, {}).get("needed", []):
            if dep not in vistas:
                vistas.add(dep)
                ordem.append(dep)
                fila.append(dep)
    return ordem


def find_hidden(libdb, raiz, vistas_runtime):
    """Dependências vistas em runtime fora da closure estática (armadilha)."""
    closure = set(resolve_recursive(libdb, raiz))
    return sorted(d for d in vistas_runtime if d not in closure)


def closure_report(libdb, raiz, vistas_runtime=None):
    """Relatório comparativo: ingênuo x recursivo x ocultas."""
    diretas = naive_ldd(libdb, raiz)
    completas = resolve_recursive(libdb, raiz)
    ocultas = find_hidden(libdb, raiz, vistas_runtime or [])
    return {
        "raiz": raiz,
        "diretas": diretas,
        "completas": completas,
        "ocultas_runtime": ocultas,
        "ldd_mente": sorted(set(completas) - set(diretas)),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Resolução recursiva de DT_NEEDED")
    ap.add_argument("db", help="JSON: {lib: {needed: [...]}}")
    ap.add_argument("raiz", help="biblioteca/binário raiz")
    ap.add_argument("--runtime", help="JSON com lista de libs vistas em runtime")
    ap.add_argument("-o", "--saida", help="grava JSON neste arquivo")
    args = ap.parse_args(argv)
    with open(args.db, encoding="utf-8") as f:
        libdb = json.load(f)
    vistas = []
    if args.runtime:
        with open(args.runtime, encoding="utf-8") as f:
            vistas = json.load(f)
    resultado = closure_report(libdb, args.raiz, vistas)
    texto = json.dumps(resultado, indent=2, ensure_ascii=False)
    if args.saida:
        with open(args.saida, "w", encoding="utf-8") as f:
            f.write(texto)
    else:
        print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
