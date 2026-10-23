#!/usr/bin/env python3
"""Instrumentação por method swizzling (Objective-C).

Troca as implementações de dois métodos na tabela da classe — a
técnica de hooking do runtime Obj-C, base de instrumentação do motor.
"""

import argparse
import json
import sys


def swizzle(tabela, a, b):
    """Troca as implementações de a e b. Retorna nova tabela + log."""
    if a not in tabela:
        raise KeyError("metodo desconhecido: " + a)
    if b not in tabela:
        raise KeyError("metodo desconhecido: " + b)
    nova = dict(tabela)
    nova[a], nova[b] = nova[b], nova[a]
    return {"tabela": nova, "trocados": [a, b]}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Swizzling de métodos Obj-C")
    args = ap.parse_args(argv)
    _ = args
    demo = {"login": "impl_login", "login_hook": "impl_hook"}
    json.dump(swizzle(demo, "login", "login_hook"), sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
