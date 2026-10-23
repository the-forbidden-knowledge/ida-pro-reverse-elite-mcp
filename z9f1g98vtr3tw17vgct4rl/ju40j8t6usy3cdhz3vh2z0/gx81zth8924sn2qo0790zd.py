#!/usr/bin/env python3
"""Diff método-a-método entre dois apps (estilo Androsim).

Classifica cada método em identical / similar / new / deleted e emite
o fidelity score do clone: o veredito numérico da clonagem.
"""

import argparse
import json
import sys


def comparar(antigo, novo):
    """antigo/novo: {metodo: hash_do_corpo} -> classificação + score."""
    chaves = set(antigo) | set(novo)
    rel = {"identical": [], "similar": [], "new": [], "deleted": []}
    for k in sorted(chaves):
        if k in antigo and k in novo:
            rel["identical" if antigo[k] == novo[k] else "similar"].append(k)
        elif k in novo:
            rel["new"].append(k)
        else:
            rel["deleted"].append(k)
    total = sum(len(v) for v in rel.values())
    if total:
        score = (len(rel["identical"]) + 0.5 * len(rel["similar"])) / total * 100
    else:
        score = 100.0
    rel["fidelity_score"] = round(score, 1)
    return rel


def main(argv=None):
    ap = argparse.ArgumentParser(description="Diff de fidelidade entre apps")
    args = ap.parse_args(argv)
    _ = args
    antigo = {"a": "h1", "b": "h2", "c": "h3"}
    novo = {"a": "h1", "b": "hX", "d": "h4"}
    json.dump(comparar(antigo, novo), sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
