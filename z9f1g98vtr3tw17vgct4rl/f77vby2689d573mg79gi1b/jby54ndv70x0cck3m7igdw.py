#!/usr/bin/env python3
"""Eliminação de código morto em grafo de chamadas smali.

A partir dos pontos de entrada, marca todos os métodos alcançáveis;
o resto é código morto e pode ser podado (estilo Simplify).
"""

import argparse
import json
import sys


def metodos_alcancaveis(grafo, entradas):
    """Busca em profundidade a partir das entradas."""
    vistos = set()
    pilha = list(entradas)
    while pilha:
        m = pilha.pop()
        if m in vistos:
            continue
        vistos.add(m)
        pilha.extend(grafo.get(m, ()))
    return vistos


def podar(grafo, entradas):
    """Retorna vivos, mortos e contagem de removidos."""
    vivos = metodos_alcancaveis(grafo, entradas)
    mortos = sorted(m for m in grafo if m not in vivos)
    return {
        "vivos": sorted(vivos),
        "mortos": mortos,
        "removidos": len(mortos),
        "total": len(grafo),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Poda código morto do grafo smali")
    args = ap.parse_args(argv)
    _ = args
    demo = {
        "onCreate": ["init", "run"],
        "init": ["helper"],
        "run": [],
        "helper": [],
        "morto1": ["morto2"],
        "morto2": [],
    }
    json.dump(podar(demo, ["onCreate"]), sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
