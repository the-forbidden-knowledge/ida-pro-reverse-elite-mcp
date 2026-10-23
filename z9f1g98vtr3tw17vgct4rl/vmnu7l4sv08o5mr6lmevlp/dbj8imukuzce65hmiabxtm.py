#!/usr/bin/env python3
"""Varre regioes de memoria e lista as suspeitas: RWX com codigo ou MZ.

Somente stdlib. Entrada: JSON {"regions": [{"base": "0x...", "size": int,
"protect": "RWX", "has_mz": bool, "has_code": bool}]}.
"""
import argparse
import json
import sys


def scan(regions):
    suspicious = []
    for r in regions:
        protect = str(r.get("protect", "")).upper()
        has_mz = bool(r.get("has_mz", False))
        has_code = bool(r.get("has_code", False))
        if "W" in protect and "X" in protect and (has_mz or has_code):
            score = 3 + (2 if has_mz else 0) + (2 if has_code else 0)
            suspicious.append({
                "base": r.get("base"),
                "size": r.get("size"),
                "protect": protect,
                "has_mz": has_mz,
                "has_code": has_code,
                "score": score,
            })
    suspicious.sort(key=lambda s: s["score"], reverse=True)
    return {"suspicious": suspicious, "count": len(suspicious),
            "total_regions": len(regions)}


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Acha regioes RWX suspeitas na memoria."
    )
    ap.add_argument("input", help="JSON com as regioes de memoria")
    ap.add_argument("--output", "-o", help="arquivo de saida JSON")
    args = ap.parse_args(argv)

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)
    result = scan(data.get("regions", []))
    out = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
