#!/usr/bin/env python3
"""Known-plaintext: deriva chave XOR repetida a partir de fragmento conhecido.

Somente stdlib. Dado um fragmento de texto conhecido (ex.: "http"),
testa comprimentos de chave de 1 a N e offsets, exige consistencia da
chave derivada e pontua a decodificacao completa por legibilidade.
"""
import argparse
import json
import sys


def english_score(data):
    if not data:
        return 0.0
    good = 0
    for b in data:
        if b == 32:
            good += 3
        elif 97 <= b <= 122 or 65 <= b <= 90:
            good += 2
        elif b in b".,;:!?'-\"\n\r\t()[]0123456789":
            good += 1
        elif 32 <= b < 127:
            good += 0
        else:
            good -= 5
    return good / len(data)


def derive_key(data, plain, key_len, offset):
    """Deriva chave de key_len bytes alinhando `plain` em `offset`.

    Retorna None se inconsistente OU se algum slot da chave nao for
    coberto pelo fragmento (fragmento precisa ter ao menos key_len bytes).
    """
    key = {}
    for i, p in enumerate(plain):
        pos = offset + i
        if pos >= len(data):
            return None
        kb = data[pos] ^ p
        slot = pos % key_len
        if slot in key and key[slot] != kb:
            return None
        key[slot] = kb
    if len(key) != key_len:
        return None
    return bytes(key[s] for s in range(key_len))


def repeating_xor(data, key):
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def recover(data, plain, max_key=16):
    best = None
    for key_len in range(1, max_key + 1):
        for offset in range(len(data)):
            key = derive_key(data, plain, key_len, offset)
            if key is None:
                continue
            decoded = repeating_xor(data, key)
            score = english_score(decoded)
            if best is None or score > best[0]:
                best = (score, key, key_len, offset)
    if best is None:
        return {"key_hex": None, "key_length": None, "offset": None, "score": 0.0}
    score, key, key_len, offset = best
    ascii_key = key.decode("ascii") if all(32 <= b < 127 for b in key) else None
    return {
        "key_hex": key.hex(),
        "key_ascii": ascii_key,
        "key_length": key_len,
        "offset": offset,
        "score": round(score, 3),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Recupera chave XOR repetida via known-plaintext."
    )
    ap.add_argument("input", help="arquivo binario de entrada")
    ap.add_argument("--plaintext", "-p", required=True,
                    help="fragmento conhecido (ex.: http)")
    ap.add_argument("--max-key", type=int, default=16,
                    help="comprimento maximo da chave")
    ap.add_argument("--decode", help="grava arquivo decodificado neste caminho")
    ap.add_argument("--output", "-o", help="arquivo de saida JSON")
    args = ap.parse_args(argv)

    with open(args.input, "rb") as f:
        data = f.read()
    result = recover(data, args.plaintext.encode("latin-1"), max_key=args.max_key)

    if args.decode and result["key_hex"]:
        key = bytes.fromhex(result["key_hex"])
        with open(args.decode, "wb") as f:
            f.write(repeating_xor(data, key))
        result["decoded_to"] = args.decode

    out = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
