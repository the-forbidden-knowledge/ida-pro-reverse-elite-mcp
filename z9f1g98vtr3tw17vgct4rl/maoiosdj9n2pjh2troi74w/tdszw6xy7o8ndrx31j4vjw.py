#!/usr/bin/env python3
"""Brute-force de XOR de 1 byte com pontuacao por legibilidade.

Somente stdlib. Testa as 256 chaves possiveis, pontua cada decodificacao
pela distribuicao de caracteres do ingles e devolve as melhores.
"""
import argparse
import json
import sys


def english_score(data):
    """Pontua bytes decodificados: maior = mais parecido com texto em ingles."""
    if not data:
        return 0.0
    good = 0
    for b in data:
        if b == 32:                      # espaco
            good += 3
        elif 97 <= b <= 122:             # a-z
            good += 2
        elif 65 <= b <= 90:              # A-Z
            good += 2
        elif b in b".,;:!?'-\"\n\r\t()[]0123456789":
            good += 1
        elif 32 <= b < 127:
            good += 0
        else:
            good -= 5
    return good / len(data)


def xor_decode(data, key):
    return bytes(b ^ key for b in data)


def search(data, top=5, preview=120):
    scored = []
    for key in range(256):
        decoded = xor_decode(data, key)
        scored.append((english_score(decoded), key, decoded))
    scored.sort(key=lambda t: t[0], reverse=True)
    results = []
    for score, key, decoded in scored[:top]:
        raw = decoded[:preview]
        text = "".join(chr(b) if 32 <= b < 127 else "." for b in raw)
        results.append({
            "key": key,
            "key_hex": "0x%02x" % key,
            "score": round(score, 3),
            "preview": text,
        })
    return {"results": results, "best_key": results[0]["key"] if results else None}


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Brute-force XOR 1 byte e ranqueia por legibilidade."
    )
    ap.add_argument("input", help="arquivo binario de entrada")
    ap.add_argument("--top", type=int, default=5, help="quantas chaves listar")
    ap.add_argument("--preview", type=int, default=120,
                    help="bytes de preview decodificado")
    ap.add_argument("--output", "-o", help="arquivo de saida JSON")
    args = ap.parse_args(argv)

    with open(args.input, "rb") as f:
        data = f.read()
    result = search(data, top=args.top, preview=args.preview)
    out = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
