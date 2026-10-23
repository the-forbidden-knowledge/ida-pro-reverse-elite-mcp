#!/usr/bin/env python3
"""Consolida os achados da fase de memoria num relatorio JSON unico.

Entradas (todas opcionais, JSON):
  --rwx   saida do varredor de regioes RWX  {"suspect_regions": [...]}
  --hooks saida do detector de prologos   {"patched": [...]}
  --idc   script IDC gerado (conta rotulos set_name)
Saida: JSON com as tres secoes + resumo de contagens.
"""

import argparse
import json
import os
import re
import sys


def load_json(path):
    if not path:
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def count_idc_labels(path):
    """Conta chamadas set_name() num arquivo .idc."""
    if not path or not os.path.exists(path):
        return 0
    with open(path, encoding="utf-8") as f:
        corpo = f.read()
    return len(re.findall(r"set_name\s*\(", corpo))


def build_report(rwx, hooks, idc_path):
    regioes = (rwx or {}).get("suspect_regions", [])
    if isinstance(regioes, dict):
        regioes = list(regioes.values())
    patch = (hooks or {}).get("patched", [])
    if isinstance(patch, dict):
        patch = list(patch.values())

    rel = {
        "fase": "memoria",
        "rwx": {
            "regioes_suspeitas": regioes,
            "total": len(regioes),
        },
        "hooks": {
            "prologos_patcheados": patch,
            "total": len(patch),
        },
        "idc": {
            "arquivo": idc_path,
            "rotulos": count_idc_labels(idc_path),
        },
        "resumo": {
            "regioes_rwx": len(regioes),
            "prologos_patcheados": len(patch),
            "rotulos_idc": count_idc_labels(idc_path),
        },
    }
    return rel


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Consolida achados da fase de memoria em JSON unico.")
    ap.add_argument("--rwx", default=None, help="JSON do varredor RWX")
    ap.add_argument("--hooks", default=None, help="JSON do detector de prologos")
    ap.add_argument("--idc", default=None, help="script .idc gerado")
    ap.add_argument("--output", default=None, help="arquivo de saida (padrao: stdout)")
    args = ap.parse_args(argv)

    rel = build_report(load_json(args.rwx), load_json(args.hooks), args.idc)
    texto = json.dumps(rel, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(texto + "\n")
    else:
        sys.stdout.write(texto + "\n")


if __name__ == "__main__":
    main()
