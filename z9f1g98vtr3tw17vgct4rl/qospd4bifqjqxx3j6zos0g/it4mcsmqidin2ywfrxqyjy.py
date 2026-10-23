#!/usr/bin/env python3
"""Detecta prologo de funcao patcheado: JMP no inicio indica hook inline.

Somente stdlib. Entrada: JSON {"functions": [{"name": str, "addr": str,
"bytes": "hex dos primeiros bytes"}]}. Reconhece:
  E9 xx xx xx xx  -> jmp rel32
  EB xx           -> jmp rel8
  68 xx xx xx xx  -> push imm32 (push/ret)
  FF 25 ..        -> jmp [mem] (indireto)
"""
import argparse
import json
import sys


def classify_prologue(raw):
    if len(raw) >= 5 and raw[0] == 0xE9:
        return "jmp rel32"
    if len(raw) >= 2 and raw[0] == 0xEB:
        return "jmp rel8"
    if len(raw) >= 5 and raw[0] == 0x68:
        return "push imm32 (push/ret)"
    if len(raw) >= 6 and raw[0] == 0xFF and raw[1] == 0x25:
        return "jmp [mem] indireto"
    return None


def scan(functions):
    hooked = []
    clean = 0
    for fn in functions:
        try:
            raw = bytes.fromhex(fn.get("bytes", ""))
        except ValueError:
            raw = b""
        patch = classify_prologue(raw)
        if patch:
            hooked.append({
                "name": fn.get("name"),
                "addr": fn.get("addr"),
                "patch": patch,
            })
        else:
            clean += 1
    return {"hooked": hooked, "hooked_count": len(hooked),
            "clean_count": clean}


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Detecta prologos patcheados (hook inline)."
    )
    ap.add_argument("input", help="JSON com funcoes e bytes iniciais")
    ap.add_argument("--output", "-o", help="arquivo de saida JSON")
    args = ap.parse_args(argv)

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)
    result = scan(data.get("functions", []))
    out = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
