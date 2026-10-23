#!/usr/bin/env python3
"""Ledger de fidelidade: Androsim-diff + cobertura por formato.

Compara métodos do original vs. clone (identical/similar/new/deleted)
e mantém um ledger de verificações por formato — a base numérica do
veredito de clonagem.
"""

import argparse
import json
import sys


def diff_methods(original: list, clone: list) -> dict:
    """Diff método-a-método. Cada método: {nome, assinatura, tamanho}."""
    mapa_o = {m["nome"]: m for m in original}
    mapa_c = {m["nome"]: m for m in clone}
    identical, similar, new, deleted = [], [], [], []
    for nome, mo in mapa_o.items():
        mc = mapa_c.get(nome)
        if mc is None:
            deleted.append(nome)
        elif mc["assinatura"] == mo["assinatura"] and mc["tamanho"] == mo["tamanho"]:
            identical.append(nome)
        else:
            similar.append(nome)
    for nome in mapa_c:
        if nome not in mapa_o:
            new.append(nome)
    return {"identical": identical, "similar": similar,
            "new": new, "deleted": deleted}


def fidelity_score(diff: dict, total_original: int) -> float:
    """Escore 0–100: identical vale 1, similar vale 0.5."""
    if total_original <= 0:
        return 100.0
    pontos = len(diff["identical"]) + 0.5 * len(diff["similar"])
    return round(100.0 * pontos / total_original, 1)


def ledger_entry(formato: str, alvo: str, verificacoes: list) -> dict:
    """Uma entrada do ledger: verificações = [{nome, passou, detalhe}]."""
    ok = sum(1 for v in verificacoes if v["passou"])
    return {
        "formato": formato,
        "alvo": alvo,
        "verificacoes": verificacoes,
        "passaram": ok,
        "total": len(verificacoes),
    }


def build_ledger(entradas: list) -> dict:
    """Consolida entradas num ledger com totais."""
    tot_ok = sum(e["passaram"] for e in entradas)
    tot = sum(e["total"] for e in entradas)
    return {"entradas": entradas, "verificacoes_ok": tot_ok,
            "verificacoes_total": tot}


def ledger_score(ledger: dict) -> float:
    """Percentual de verificações que passaram no ledger."""
    tot = ledger["verificacoes_total"]
    if tot <= 0:
        return 100.0
    return round(100.0 * ledger["verificacoes_ok"] / tot, 1)


def to_json(ledger: dict) -> str:
    return json.dumps(ledger, indent=2, ensure_ascii=False)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Ledger de fidelidade multi-formato.")
    ap.add_argument("ledger", help="JSON com a lista de entradas")
    args = ap.parse_args(argv)
    with open(args.ledger, encoding="utf-8") as f:
        entradas = json.load(f)
    ledger = build_ledger(entradas)
    print(to_json(ledger))
    print("score: %.1f%%" % ledger_score(ledger))
    return 0


if __name__ == "__main__":
    sys.exit(main())
