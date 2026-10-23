#!/usr/bin/env python3
"""Rastreio de fluxo de dados para tras (backward slice) sobre uma global.

Somente biblioteca padrao. Le um JSON {writes: [...], reads: [...]} que
simula um rastreio de escrita numa global, recebe --target com o endereco da
escrita-alvo e caminha para tras coletando as instrucoes de comparacao e
atribuicao anteriores que a influenciam, ate chegar a origem.
"""

import argparse
import json

OPS = ("write", "read", "compare", "assign")


def _norm(rec):
    addr = rec.get("addr")
    op = str(rec.get("op", "")).lower()
    return {
        "addr": addr,
        "op": op if op in OPS else "write",
        "target": rec.get("target", ""),
        "value": rec.get("value", ""),
    }


def trace(records, target_addr):
    """Constroi a cadeia de influencia para tras a partir de target_addr."""
    recs = [_norm(r) for r in records]
    by_addr = {r["addr"]: r for r in recs}
    if target_addr not in by_addr:
        return {"chain": []}

    start = by_addr[target_addr]
    tainted = {start["target"]}  # variaveis que alimentam a escrita-alvo
    if start["value"]:
        tainted.add(start["value"])  # origem imediata da escrita-alvo
    chain = [start]

    # Procura predecessores: varre enderecos decrescentes ate a origem.
    for r in sorted(recs, key=lambda x: x["addr"], reverse=True):
        if r["addr"] >= target_addr or r["addr"] == start["addr"]:
            continue
        influences = r["target"] in tainted
        guards = (r["op"] == "compare"
                  and (r["target"] in tainted or r["value"] in tainted))
        if influences or guards:
            chain.append(r)
            # Propaga o taint para a fonte da atribuicao.
            if r["op"] in ("write", "assign") and r["value"]:
                tainted.add(r["value"])

    chain.sort(key=lambda x: x["addr"])
    out = []
    for r in chain:
        out.append({
            "addr": r["addr"],
            "op": r["op"],
            "detail": "%s <- %s" % (r["target"], r["value"]),
        })
    return {"chain": out}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Backward slice sobre um rastreio de escrita."
    )
    parser.add_argument("input", help="Arquivo JSON {writes: [...], reads: [...]}.")
    parser.add_argument("--target", type=lambda s: int(s, 0), required=True,
                        help="Endereco da escrita-alvo (ex.: 0x401000).")
    args = parser.parse_args(argv)
    with open(args.input, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    records = list(data.get("writes", [])) + list(data.get("reads", []))
    print(json.dumps(trace(records, args.target), indent=2))


if __name__ == "__main__":
    main()
