#!/usr/bin/env python3
"""Lab 02 — strings-extract: extrai strings ASCII e UTF-16LE com offset.

Somente stdlib. Percorre os bytes do arquivo procurando sequências de
caracteres imprimíveis (ASCII) ou pares byte-nulo (UTF-16LE).
"""

import argparse
import json
import sys


def _extrair_ascii(data, min_len):
    achadas = []
    atual = bytearray()
    inicio = 0
    for i, b in enumerate(data):
        if 0x20 <= b <= 0x7E:
            if not atual:
                inicio = i
            atual.append(b)
        else:
            if len(atual) >= min_len:
                achadas.append(
                    {
                        "offset": inicio,
                        "encoding": "ascii",
                        "text": atual.decode("ascii"),
                    }
                )
            atual = bytearray()
    if len(atual) >= min_len:
        achadas.append(
            {"offset": inicio, "encoding": "ascii", "text": atual.decode("ascii")}
        )
    return achadas


def _extrair_utf16le(data, min_len):
    achadas = []
    i, n = 0, len(data)
    while i + 1 < n:
        if data[i + 1] == 0 and 0x20 <= data[i] <= 0x7E:
            inicio = i
            chars = []
            while i + 1 < n and data[i + 1] == 0 and 0x20 <= data[i] <= 0x7E:
                chars.append(chr(data[i]))
                i += 2
            if len(chars) >= min_len:
                achadas.append(
                    {
                        "offset": inicio,
                        "encoding": "utf-16le",
                        "text": "".join(chars),
                    }
                )
        else:
            i += 1
    return achadas


def extract_strings(path, min_len=4, encoding="both"):
    """Extrai strings de um arquivo.

    encoding: "ascii", "utf16" ou "both". Retorna lista de
    {offset, encoding, text} ordenada por offset.
    """
    with open(path, "rb") as f:
        data = f.read()
    resultado = []
    if encoding in ("ascii", "both"):
        resultado.extend(_extrair_ascii(data, min_len))
    if encoding in ("utf16", "both"):
        resultado.extend(_extrair_utf16le(data, min_len))
    resultado.sort(key=lambda s: s["offset"])
    return resultado


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Extrai strings ASCII e UTF-16LE de um arquivo."
    )
    parser.add_argument("arquivo", help="caminho do arquivo a analisar")
    parser.add_argument(
        "--min-len", type=int, default=4, help="tamanho mínimo (padrão: 4)"
    )
    parser.add_argument(
        "--encoding",
        choices=["ascii", "utf16", "both"],
        default="both",
        help="codificação a extrair (padrão: both)",
    )
    parser.add_argument(
        "-o", "--saida", help="grava o JSON neste arquivo (padrão: stdout)"
    )
    args = parser.parse_args(argv)
    resultado = extract_strings(args.arquivo, args.min_len, args.encoding)
    texto = json.dumps(resultado, indent=2, ensure_ascii=False)
    if args.saida:
        with open(args.saida, "w", encoding="utf-8") as f:
            f.write(texto + "\n")
    else:
        print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
