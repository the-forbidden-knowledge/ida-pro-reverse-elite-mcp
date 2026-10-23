#!/usr/bin/env python3
"""Ledger de obrigacoes de reconstrucao: o que o clone deve reproduzir.

Entrada: JSON do mapa de rastreabilidade (lab 44).
  --concluidas BEH-001,BEH-002  marca obrigacoes como "feito".
Saida: JSON {"obrigacoes": [{comportamento, evidencia, status, notas}]}.
Status: "pendente" | "feito".
"""

import argparse
import json
import sys

PENDENTE = "pendente"
FEITO = "feito"


def build_ledger(mapa, concluidas=()):
    """Monta o ledger a partir do mapa {BEH: {funcoes, evidencias}}."""
    feitas = set(concluidas or ())
    obrigacoes = []
    for bid in sorted(mapa or {}):
        info = mapa[bid]
        evs = info.get("evidencias", [])
        if evs:
            for e in evs:
                obrigacoes.append({
                    "comportamento": bid,
                    "evidencia": e.get("id", ""),
                    "descricao_evidencia": e.get("descricao", ""),
                    "funcao": e.get("funcao", ""),
                    "status": FEITO if bid in feitas else PENDENTE,
                    "notas": "",
                })
        else:
            obrigacoes.append({
                "comportamento": bid,
                "evidencia": "",
                "descricao_evidencia": "sem evidencia vinculada",
                "funcao": "",
                "status": FEITO if bid in feitas else PENDENTE,
                "notas": "investigar origem do comportamento",
            })
    return {"obrigacoes": obrigacoes}


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Gera ledger de obrigacoes de reconstrucao.")
    ap.add_argument("--input", required=True, help="JSON do mapa (lab 44)")
    ap.add_argument("--concluidas", default="",
                    help="ids concluidos, separados por virgula (ex.: BEH-001,BEH-002)")
    ap.add_argument("--output", default=None, help="arquivo de saida (padrao: stdout)")
    args = ap.parse_args(argv)

    with open(args.input, encoding="utf-8") as f:
        data = json.load(f)
    concluidas = [c.strip() for c in args.concluidas.split(",") if c.strip()]

    ledger = build_ledger(data.get("mapa"), concluidas)
    texto = json.dumps(ledger, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(texto + "\n")
    else:
        sys.stdout.write(texto + "\n")


if __name__ == "__main__":
    main()
