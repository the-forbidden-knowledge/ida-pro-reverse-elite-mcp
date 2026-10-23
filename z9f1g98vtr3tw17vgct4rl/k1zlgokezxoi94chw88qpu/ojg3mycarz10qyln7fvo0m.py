#!/usr/bin/env python3
"""Compara relatorios de triagem (binario empacotado x dump) e avalia o unpacking.

Somente stdlib. Entrada: dois JSONs de triagem com os campos
avg_entropy, imports, sections e size.
"""
import argparse
import json
import sys


def load_report(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compare(before, after):
    reasons = []
    score = 0

    e_before = float(before.get("avg_entropy", 0.0))
    e_after = float(after.get("avg_entropy", 0.0))
    e_drop = e_before - e_after
    if e_drop >= 1.0:
        reasons.append("entropia caiu %.2f (empacotado alta -> dump normal)" % e_drop)
        score += 2
    elif e_drop >= 0.3:
        reasons.append("entropia caiu pouco (%.2f)" % e_drop)
        score += 1

    i_before = int(before.get("imports", 0))
    i_after = int(after.get("imports", 0))
    if i_after >= i_before * 3 and (i_after - i_before) >= 20:
        reasons.append("imports saltaram de %d para %d" % (i_before, i_after))
        score += 2
    elif i_after > i_before:
        reasons.append("imports cresceram (%d -> %d)" % (i_before, i_after))
        score += 1

    s_before = int(before.get("sections", 0))
    s_after = int(after.get("sections", 0))
    if s_after > s_before:
        reasons.append("secoes aumentaram (%d -> %d)" % (s_before, s_after))
        score += 1

    z_before = int(before.get("size", 0))
    z_after = int(after.get("size", 0))
    if z_after > z_before:
        reasons.append("tamanho cresceu (%d -> %d bytes)" % (z_before, z_after))
        score += 1

    return {
        "unpacked": score >= 3,
        "score": score,
        "metrics": {
            "entropy_drop": round(e_drop, 3),
            "imports_before": i_before,
            "imports_after": i_after,
            "sections_before": s_before,
            "sections_after": s_after,
            "size_before": z_before,
            "size_after": z_after,
        },
        "reasons": reasons,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Compara triagem empacotado x dump e avalia o unpacking."
    )
    ap.add_argument("before", help="JSON de triagem do binario empacotado")
    ap.add_argument("after", help="JSON de triagem do dump")
    ap.add_argument("--output", "-o", help="arquivo de saida JSON")
    args = ap.parse_args(argv)

    result = compare(load_report(args.before), load_report(args.after))
    out = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
