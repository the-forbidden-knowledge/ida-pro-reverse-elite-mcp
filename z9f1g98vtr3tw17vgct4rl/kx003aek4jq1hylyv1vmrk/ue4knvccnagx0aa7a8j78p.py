#!/usr/bin/env python3
"""Compara comportamento original vs clone e aponta divergencias.

Entradas: dois JSONs de spec (lab 43) {"comportamentos": [{id, descricao, ...}]}.
Saida: JSON {faltando, extras, divergentes, resumo}.
  faltando:    ids/descricoes no original ausentes no clone
  extras:      no clone ausentes no original
  divergentes: mesmo id, pre_condicoes ou efeitos diferentes
"""

import argparse
import json
import sys


def norm(s):
    return " ".join(str(s or "").strip().lower().split())


def index(spec):
    return {c.get("id"): c for c in (spec or {}).get("comportamentos", [])}


def diff(original, clone):
    idx_o = index(original)
    idx_c = index(clone)

    # casa por id; se o id nao existir, tenta casar por descricao normalizada
    desc_c = {norm(c.get("descricao")): cid for cid, c in idx_c.items()}

    faltando, extras, divergentes = [], [], []
    usados_c = set()

    for bid, co in sorted(idx_o.items()):
        cc = idx_c.get(bid)
        if cc is None:
            cc = idx_c.get(desc_c.get(norm(co.get("descricao"))))
        if cc is None:
            faltando.append({"id": bid, "descricao": co.get("descricao", "")})
            continue
        usados_c.add(cc.get("id"))
        mud = {}
        for campo in ("descricao", "pre_condicoes", "efeitos"):
            if norm(co.get(campo)) != norm(cc.get(campo)):
                mud[campo] = {"original": co.get(campo, ""),
                              "clone": cc.get(campo, "")}
        if mud:
            divergentes.append({"id": bid, "mudancas": mud})

    for cid, cc in sorted(idx_c.items()):
        if cid not in usados_c:
            extras.append({"id": cid, "descricao": cc.get("descricao", "")})

    return {
        "faltando": faltando,
        "extras": extras,
        "divergentes": divergentes,
        "resumo": {
            "total_original": len(idx_o),
            "total_clone": len(idx_c),
            "faltando": len(faltando),
            "extras": len(extras),
            "divergentes": len(divergentes),
        },
    }


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Compara specs de comportamento original vs clone.")
    ap.add_argument("--original", required=True, help="JSON da spec original")
    ap.add_argument("--clone", required=True, help="JSON da spec do clone")
    ap.add_argument("--output", default=None, help="arquivo de saida (padrao: stdout)")
    args = ap.parse_args(argv)

    with open(args.original, encoding="utf-8") as f:
        original = json.load(f)
    with open(args.clone, encoding="utf-8") as f:
        clone = json.load(f)

    rel = diff(original, clone)
    texto = json.dumps(rel, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(texto + "\n")
    else:
        sys.stdout.write(texto + "\n")


if __name__ == "__main__":
    main()
