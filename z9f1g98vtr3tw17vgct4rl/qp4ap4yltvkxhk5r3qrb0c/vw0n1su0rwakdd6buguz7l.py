#!/usr/bin/env python3
"""Detecta process hollowing: CreateProcess* com CREATE_SUSPENDED (0x4)
+ WriteProcessMemory/SetThreadContext no fluxo.

Somente stdlib. Entrada: JSON {"apis": [...], "flags": [{"value": int,
"name": str, "context": str}]}.
"""
import argparse
import json
import sys

SUSPENDED = 0x4


def clean(name):
    n = name.lower()
    if n.endswith("ex"):
        n = n[:-2]
    if n[-1:] in ("a", "w") and len(n) > 4:
        n = n[:-1]
    return n


def detect(data):
    apis = {clean(a) for a in data.get("apis", [])}
    flags = data.get("flags", [])

    indicators = []

    has_create = any(a.startswith("createprocess") for a in apis)
    if has_create:
        indicators.append("CreateProcess* importado")

    suspended = False
    for f in flags:
        try:
            value = int(f.get("value", -1))
        except (TypeError, ValueError):
            continue
        name = str(f.get("name", "")).upper()
        ctx = str(f.get("context", "")).lower()
        if value == SUSPENDED and ("SUSPEND" in name or "createprocess" in ctx):
            suspended = True
            indicators.append("flag CREATE_SUSPENDED (0x4) referenciada em %s" %
                              (f.get("context") or f.get("name")))
            break

    has_write = "writeprocessmemory" in apis or "ntwritevirtualmemory" in apis
    if has_write:
        indicators.append("WriteProcessMemory no fluxo")
    has_unmap = "ntunmapviewofsection" in apis or "zwunmapviewofsection" in apis
    if has_unmap:
        indicators.append("NtUnmapViewOfSection no fluxo")
    has_setctx = "setthreadcontext" in apis
    if has_setctx:
        indicators.append("SetThreadContext no fluxo")
    has_resume = "resumethread" in apis
    if has_resume:
        indicators.append("ResumeThread no fluxo")

    detected = has_create and suspended and (has_write or has_unmap)
    return {
        "detected": detected,
        "technique": "process hollowing",
        "indicators": indicators,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Detecta process hollowing."
    )
    ap.add_argument("input", help="JSON com apis e flags")
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
