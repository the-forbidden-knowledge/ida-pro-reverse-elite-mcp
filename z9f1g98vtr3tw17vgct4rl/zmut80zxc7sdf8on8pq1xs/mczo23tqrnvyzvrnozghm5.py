#!/usr/bin/env python3
"""Decodifica o name mangling do Swift: `_TtC13Nome11Classe` → `Nome.Classe`.

Suporta o mangling clássico (`_T`): classes (`tC`), structs (`tV`),
enums (`tO`) e protocolos (`tP`), com identificadores prefixados pelo
comprimento em bytes. Símbolos fora do padrão passam intactos.
"""

import argparse
import json
import sys

KIND_NAMES = {"C": "classe", "V": "struct", "O": "enum", "P": "protocolo"}


def _parse_identifiers(texto: str, pos: int):
    """Lê sequência `<len><nome><len><nome>...`; devolve (lista, nova_pos)."""
    nomes = []
    while pos < len(texto):
        ini = pos
        while pos < len(texto) and texto[pos].isdigit():
            pos += 1
        if pos == ini:
            break
        tamanho = int(texto[ini:pos])
        nome = texto[pos:pos + tamanho]
        if len(nome) != tamanho:
            return None, ini  # truncado: inválido
        nomes.append(nome)
        pos += tamanho
    return nomes, pos


def demangle(simbolo: str) -> str:
    """Decodifica um símbolo Swift; devolve o original se não for válido."""
    corpo = None
    kind = None
    if simbolo.startswith("_Tt") and len(simbolo) > 3 and simbolo[3] in KIND_NAMES:
        corpo, kind = simbolo[4:], simbolo[3]
    elif simbolo.startswith("$s"):
        # Mangling novo ($s): tenta o mesmo formato após o prefixo.
        resto = simbolo[2:]
        if resto and resto[0] in "CVOP":
            corpo, kind = resto[1:], resto[0]
    if corpo is None:
        return simbolo
    nomes, pos = _parse_identifiers(corpo, 0)
    if nomes is None or pos != len(corpo) or len(nomes) < 2:
        return simbolo
    return ".".join(nomes)


def is_swift_mangled(simbolo: str) -> bool:
    """Diz se o símbolo parece mangling Swift decodificável."""
    return demangle(simbolo) != simbolo


def kind_of(simbolo: str):
    """Devolve o tipo da entidade (classe/struct/enum/protocolo) ou None."""
    if simbolo.startswith("_Tt") and len(simbolo) > 3:
        return KIND_NAMES.get(simbolo[3])
    if simbolo.startswith("$s") and len(simbolo) > 2:
        return KIND_NAMES.get(simbolo[2])
    return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Decodifica name mangling Swift.")
    ap.add_argument("simbolos", nargs="*", help="símbolos (ou stdin)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    simbolos = args.simbolos or [l.strip() for l in sys.stdin if l.strip()]
    resultado = [{"simbolo": s, "decodificado": demangle(s), "kind": kind_of(s)}
                 for s in simbolos]
    if args.json:
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
    else:
        for r in resultado:
            print("%s -> %s" % (r["simbolo"], r["decodificado"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
