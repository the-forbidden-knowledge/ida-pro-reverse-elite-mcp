#!/usr/bin/env python3
"""Desofuscação de nomes ProGuard/R8 por heurística.

Nomes ofuscados (a, b, zzb...) viram nomes legíveis derivados da
assinatura: tipo de retorno para métodos, tipo do campo para fields.
"""

import argparse
import json
import re
import sys

_OFUSCADO = re.compile(r"^[A-Za-z]{1,2}$|^zz\w*$")


def eh_ofuscado(nome):
    """True se o nome parece saída de ofuscador."""
    return bool(_OFUSCADO.match(nome))


def _retorno(sig):
    return sig.split(")")[-1]


def base_para(sig, kind):
    """Nome-base legível a partir da assinatura."""
    ret = _retorno(sig)
    if kind == "field":
        mapa = {
            "Z": "flag",
            "I": "count",
            "J": "total",
            "Ljava/lang/String;": "text",
        }
        return mapa.get(ret, "field")
    mapa = {
        "V": "run",
        "Z": "is",
        "I": "getInt",
        "J": "getLong",
        "Ljava/lang/String;": "getString",
    }
    return mapa.get(ret, "getObj")


def deobfuscar(membros):
    """membros: [{kind, name, sig}] -> [(antigo, novo)], sem colisões."""
    usados = set()
    cont = {}
    saida = []
    for m in membros:
        nome = m["name"]
        if not eh_ofuscado(nome):
            usados.add(nome)
            saida.append((nome, nome))
            continue
        base = base_para(m["sig"], m["kind"])
        n = cont.get(base, 0)
        novo = base if n == 0 else "%s_%d" % (base, n)
        while novo in usados:
            n += 1
            novo = "%s_%d" % (base, n)
        cont[base] = n + 1
        usados.add(novo)
        saida.append((nome, novo))
    return saida


def main(argv=None):
    ap = argparse.ArgumentParser(description="Desofusca nomes ProGuard/R8")
    args = ap.parse_args(argv)
    _ = args
    demo = [
        {"kind": "method", "name": "a", "sig": "()Ljava/lang/String;"},
        {"kind": "method", "name": "b", "sig": "()Ljava/lang/String;"},
        {"kind": "method", "name": "onCreate", "sig": "(Landroid/os/Bundle;)V"},
        {"kind": "field", "name": "c", "sig": "I"},
    ]
    json.dump(
        [{"antigo": a, "novo": n} for a, n in deobfuscar(demo)],
        sys.stdout,
        ensure_ascii=False,
        indent=2,
    )
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
