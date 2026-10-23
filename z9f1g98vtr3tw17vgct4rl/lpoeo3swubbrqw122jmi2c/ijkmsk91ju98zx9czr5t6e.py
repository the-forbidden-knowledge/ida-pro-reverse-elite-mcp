#!/usr/bin/env python3
"""Detecta padrao de hook via trampolim: ReadProcessMemory -> VirtualProtect
-> WriteProcessMemory (ler original, afrouxar protecao, aplicar patch).

Somente stdlib. Entrada: JSON {"imports": {dll: [funcoes]}, "calls": [[origem, destino]]}.
"""
import argparse
import json
import sys

CHAIN = ["readprocessmemory", "virtualprotect", "writeprocessmemory"]


def clean(name):
    n = name.lower()
    if n.endswith("ex"):
        n = n[:-2]
    if n[-1:] in ("a", "w") and len(n) > 4:
        n = n[:-1]
    return n


def detect(data):
    imports = data.get("imports", {})
    all_imports = {clean(f) for funcs in imports.values() for f in funcs}
    matched = [c for c in CHAIN if c in all_imports]
    missing = [c for c in CHAIN if c not in all_imports]

    in_order = None
    calls = data.get("calls", [])
    if calls:
        seq = []
        for _, dst in calls:
            d = clean(dst)
            if d in CHAIN and (not seq or seq[-1] != d):
                seq.append(d)
        idx = 0
        for d in seq:
            if idx < len(CHAIN) and d == CHAIN[idx]:
                idx += 1
        in_order = idx == len(CHAIN)

    detected = not missing and (in_order is not False)
    return {
        "detected": detected,
        "technique": "hook via trampolim (backup + patch)",
        "matched": matched,
        "missing": missing,
        "in_order": in_order,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Detecta padrao de hook via trampolim."
    )
    ap.add_argument("input", help="JSON com imports e calls")
    ap.add_argument("--output", "-o", help="arquivo de saida JSON")
    args = ap.parse_args(argv)

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)
    result = detect(data)
    out = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
