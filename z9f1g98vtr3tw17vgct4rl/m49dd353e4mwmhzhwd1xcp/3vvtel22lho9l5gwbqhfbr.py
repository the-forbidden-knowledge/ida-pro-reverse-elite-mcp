#!/usr/bin/env python3
"""Verifica a cobertura do clone a partir do ledger de obrigacoes.

Entrada: JSON do ledger (lab 45) {"obrigacoes": [{comportamento, status}]}.
Saida: JSON {total, feitas, pendentes, cobertura_pct, gaps: [ids], por_comportamento}.
"""

import argparse
import json
import sys


def verify(ledger):
    obrigacoes = (ledger or {}).get("obrigacoes", [])
    total = len(obrigacoes)
    feitas = sum(1 for o in obrigacoes if o.get("status") == "feito")
    pendentes = total - feitas

    gaps = sorted({o.get("comportamento", "") for o in obrigacoes
                   if o.get("status") != "feito"})

    por_comp = {}
    for o in obrigacoes:
        bid = o.get("comportamento", "")
        e = por_comp.setdefault(bid, {"total": 0, "feitas": 0})
        e["total"] += 1
        if o.get("status") == "feito":
            e["feitas"] += 1

    cobertura = round(100.0 * feitas / total, 1) if total else 0.0
    return {
        "total": total,
        "feitas": feitas,
        "pendentes": pendentes,
        "cobertura_pct": cobertura,
        "gaps": gaps,
        "por_comportamento": por_comp,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Calcula cobertura do clone a partir do ledger.")
    ap.add_argument("--input", required=True, help="JSON do ledger (lab 45)")
    ap.add_argument("--output", default=None, help="arquivo de saida (padrao: stdout)")
    args = ap.parse_args(argv)

    with open(args.input, encoding="utf-8") as f:
        ledger = json.load(f)

    rel = verify(ledger)
    texto = json.dumps(rel, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(texto + "\n")
    else:
        sys.stdout.write(texto + "\n")


if __name__ == "__main__":
    main()
