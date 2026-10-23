#!/usr/bin/env python3
"""Emula loops simples de decode (XOR/ADD/SUB/ROL/ROR) descritos em mini-DSL JSON.

Somente stdlib. A DSL e um JSON {"ops": [...]} onde cada op tem:
  op:     "xor" | "add" | "sub" | "rol" | "ror"
  key:    inteiro (byte da chave ou contagem de rotacao)
  start:  offset inicial (padrao 0)
  length: bytes a processar (padrao: ate o fim)
As operacoes sao aplicadas em sequencia sobre uma copia dos bytes.
"""
import argparse
import json
import sys


def rol_byte(b, n):
    n %= 8
    return ((b << n) | (b >> (8 - n))) & 0xFF if n else b


def ror_byte(b, n):
    n %= 8
    return ((b >> n) | (b << (8 - n))) & 0xFF if n else b


def apply_op(data, op):
    name = op["op"].lower()
    key = int(op["key"]) & 0xFF
    start = int(op.get("start", 0))
    end = start + int(op.get("length", len(data) - start))
    end = min(end, len(data))
    out = bytearray(data)
    for i in range(start, end):
        b = out[i]
        if name == "xor":
            out[i] = b ^ key
        elif name == "add":
            out[i] = (b + key) & 0xFF
        elif name == "sub":
            out[i] = (b - key) & 0xFF
        elif name == "rol":
            out[i] = rol_byte(b, key)
        elif name == "ror":
            out[i] = ror_byte(b, key)
        else:
            raise ValueError("operacao desconhecida: %r" % (op["op"],))
    return bytes(out)


def emulate(data, dsl):
    for op in dsl.get("ops", []):
        data = apply_op(data, op)
    return data


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Emula loop de decode descrito em mini-DSL JSON."
    )
    ap.add_argument("input", help="arquivo binario de entrada")
    ap.add_argument("dsl", help="JSON com a lista de operacoes")
    ap.add_argument("--output", "-o", required=True,
                    help="arquivo binario de saida decodificado")
    args = ap.parse_args(argv)

    with open(args.input, "rb") as f:
        data = f.read()
    with open(args.dsl, "r", encoding="utf-8") as f:
        dsl = json.load(f)
    with open(args.output, "wb") as f:
        f.write(emulate(data, dsl))
    print("decodificado %d bytes -> %s" % (len(data), args.output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
