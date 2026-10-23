#!/usr/bin/env python3
"""Lab 12 — symbolic-constants: resolve constantes simbólicas conhecidas.

Somente stdlib. Varre um dump de disassembly (texto) procurando valores
imediatos em hexadecimal (0x... ou sufixo "h" estilo MASM) e traduz os
conhecidos para nomes simbólicos: chaves de registro, códigos de status,
flags de memória/processo etc.
"""

import argparse
import json
import re
import sys

CONSTANTES = {
    0x80000000: "HKEY_CLASSES_ROOT / GENERIC_READ",
    0x80000001: "HKEY_CURRENT_USER",
    0x80000002: "HKEY_LOCAL_MACHINE",
    0x80000003: "HKEY_USERS",
    0x80000004: "HKEY_PERFORMANCE_DATA",
    0x80000005: "HKEY_CURRENT_CONFIG",
    0xC0000005: "STATUS_ACCESS_VIOLATION",
    0xC0000008: "STATUS_INVALID_HANDLE",
    0x00000004: "CREATE_SUSPENDED",
    0x00000040: "PAGE_EXECUTE_READWRITE",
    0x00001000: "MEM_COMMIT",
    0x00002000: "MEM_RESERVE",
    0x00003000: "MEM_COMMIT|MEM_RESERVE",
    0xFFFFFFFF: "INVALID_HANDLE_VALUE (-1)",
}

RE_HEX = re.compile(r"0[xX]([0-9a-fA-F]+)")
RE_MASM = re.compile(r"\b([0-9a-fA-F]{2,})[hH]\b")


def resolve_dump(text):
    """Resolve constantes conhecidas linha a linha.

    Retorna lista de {linha, texto, valor, nome}.
    """
    achados = []
    for n, linha in enumerate(text.splitlines(), start=1):
        vistos = set()
        for m in RE_HEX.finditer(linha):
            valor = int(m.group(1), 16)
            if valor in CONSTANTES and valor not in vistos:
                vistos.add(valor)
                achados.append(
                    {
                        "linha": n,
                        "texto": linha.strip(),
                        "valor": "0x%X" % valor,
                        "nome": CONSTANTES[valor],
                    }
                )
        for m in RE_MASM.finditer(linha):
            valor = int(m.group(1), 16)
            if valor in CONSTANTES and valor not in vistos:
                vistos.add(valor)
                achados.append(
                    {
                        "linha": n,
                        "texto": linha.strip(),
                        "valor": "0x%X" % valor,
                        "nome": CONSTANTES[valor],
                    }
                )
    return achados


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Resolve constantes simbólicas num dump de disassembly."
    )
    parser.add_argument("arquivo", help="arquivo texto com o disassembly")
    parser.add_argument(
        "-o", "--saida", help="grava o JSON neste arquivo (padrão: stdout)"
    )
    args = parser.parse_args(argv)
    with open(args.arquivo, encoding="utf-8", errors="replace") as f:
        texto = f.read()
    resultado = resolve_dump(texto)
    saida = json.dumps(resultado, indent=2, ensure_ascii=False)
    if args.saida:
        with open(args.saida, "w", encoding="utf-8") as f:
            f.write(saida + "\n")
    else:
        print(saida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
