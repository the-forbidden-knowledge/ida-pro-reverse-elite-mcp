#!/usr/bin/env python3
"""Veredito BAROQUE: `CLONADO 100%` estendido multi-formato + SHAs.

Consome o ledger de fidelidade (lab 92), calcula a cobertura por
formato e emite o veredito final com os SHA-256 do alvo e do clone
como prova.
"""

import argparse
import json
import sys


def verdict(ledger: dict, sha_alvo: str, sha_clone: str) -> dict:
    """Calcula o veredito a partir do ledger."""
    total = ledger.get("verificacoes_total", 0)
    ok = ledger.get("verificacoes_ok", 0)
    cobertura = round(100.0 * ok / total, 1) if total > 0 else 100.0
    divergencias = []
    formatos = []
    for entrada in ledger.get("entradas", []):
        formatos.append(entrada.get("formato", "?"))
        for v in entrada.get("verificacoes", []):
            if not v.get("passou"):
                divergencias.append("%s/%s" % (entrada.get("alvo", "?"), v.get("nome", "?")))
    if cobertura == 100.0 and not divergencias:
        texto = "CLONADO 100%"
    elif cobertura >= 80.0:
        texto = "PARCIAL"
    else:
        texto = "DIVERGENTE"
    return {
        "veredito": texto,
        "cobertura": cobertura,
        "formatos": sorted(set(formatos)),
        "verificacoes": "%d/%d" % (ok, total),
        "divergencias": divergencias,
        "sha256_alvo": sha_alvo,
        "sha256_clone": sha_clone,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Veredito BAROQUE multi-formato.")
    ap.add_argument("ledger", help="JSON do ledger de fidelidade")
    ap.add_argument("--sha-alvo", required=True, help="SHA-256 do alvo")
    ap.add_argument("--sha-clone", required=True, help="SHA-256 do clone")
    args = ap.parse_args(argv)
    with open(args.ledger, encoding="utf-8") as f:
        ledger = json.load(f)
    resultado = verdict(ledger, args.sha_alvo, args.sha_clone)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
    return 0 if resultado["veredito"] == "CLONADO 100%" else 2


if __name__ == "__main__":
    sys.exit(main())
