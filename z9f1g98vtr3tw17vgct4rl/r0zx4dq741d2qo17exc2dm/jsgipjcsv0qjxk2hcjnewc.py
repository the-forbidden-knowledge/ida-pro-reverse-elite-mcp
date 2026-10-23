#!/usr/bin/env python3
"""Decodifica stack strings: dwords little-endian empilhados -> texto ASCII.

Somente stdlib. Simula a tecla R sobre sequencias de MOVs: le o arquivo em
blocos de 4 bytes (little-endian), extrai os caracteres imprimiveis de cada
bloco e concatena blocos vizinhos em strings.
"""
import argparse
import json
import sys


def decode_dwords(data, min_len=4):
    strings = []
    current = bytearray()
    current_off = None
    usable = len(data) - (len(data) % 4)
    for i in range(0, usable, 4):
        chunk = data[i:i + 4]
        chars = bytes(b for b in chunk if b != 0)
        if chars and all(32 <= b < 127 for b in chars):
            if current_off is None:
                current_off = i
            current += chars
        else:
            if len(current) >= min_len:
                strings.append({
                    "offset": current_off,
                    "offset_hex": "0x%x" % current_off,
                    "string": current.decode("ascii"),
                })
            current = bytearray()
            current_off = None
    if len(current) >= min_len:
        strings.append({
            "offset": current_off,
            "offset_hex": "0x%x" % current_off,
            "string": current.decode("ascii"),
        })
    return strings


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Decodifica stack strings (dwords -> ASCII)."
    )
    ap.add_argument("input", help="arquivo binario de entrada")
    ap.add_argument("--min-len", type=int, default=4,
                    help="tamanho minimo da string")
    ap.add_argument("--output", "-o", help="arquivo de saida JSON")
    args = ap.parse_args(argv)

    with open(args.input, "rb") as f:
        data = f.read()
    result = {"strings": decode_dwords(data, min_len=args.min_len),
              "count": 0}
    result["count"] = len(result["strings"])
    out = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
