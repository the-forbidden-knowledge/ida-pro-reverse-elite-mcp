#!/usr/bin/env python3
"""Consolida os achados da fase de bypass num relatorio JSON unico.

Entradas (todas opcionais, JSON):
  --inventory saida do inventario de defesas  {"defesas": [...], "total": N}
  --patches   saida do plano de patch       {"patches": [...]}
  --tls       saida do parse TLS            {"tls_presente": bool, ...}
Saida: JSON com as tres secoes + resumo.
"""

import argparse
import json
import sys


def load_json(path):
    if not path:
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_report(inventory, patches, tls):
    defesas = (inventory or {}).get("defesas", [])
    lista_patches = (patches or {}).get("patches", [])
    tls_info = tls or {}

    por_categoria = {}
    for d in defesas:
        por_categoria.setdefault(d.get("categoria", "outros"), []).append(d.get("api"))

    tipos_patch = {}
    for p in lista_patches:
        tipos_patch[p.get("tipo", "manual")] = tipos_patch.get(p.get("tipo", "manual"), 0) + 1

    return {
        "fase": "bypass",
        "defesas": {
            "inventario": defesas,
            "total": len(defesas),
            "por_categoria": por_categoria,
        },
        "patches": {
            "plano": lista_patches,
            "total": len(lista_patches),
            "por_tipo": tipos_patch,
        },
        "tls": {
            "presente": bool(tls_info.get("tls_presente")),
            "callbacks": tls_info.get("total_callbacks", 0),
        },
        "resumo": {
            "defesas_encontradas": len(defesas),
            "patches_planejados": len(lista_patches),
            "patches_manuais": tipos_patch.get("manual", 0),
            "tls_presente": bool(tls_info.get("tls_presente")),
        },
    }


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Consolida achados da fase de bypass em JSON unico.")
    ap.add_argument("--inventory", default=None, help="JSON do inventario de defesas")
    ap.add_argument("--patches", default=None, help="JSON do plano de patch")
    ap.add_argument("--tls", default=None, help="JSON do parse TLS")
    ap.add_argument("--output", default=None, help="arquivo de saida (padrao: stdout)")
    args = ap.parse_args(argv)

    rel = build_report(load_json(args.inventory), load_json(args.patches),
                       load_json(args.tls))
    texto = json.dumps(rel, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(texto + "\n")
    else:
        sys.stdout.write(texto + "\n")


if __name__ == "__main__":
    main()
