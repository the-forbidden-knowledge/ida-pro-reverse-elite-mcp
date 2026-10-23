#!/usr/bin/env python3
"""Gera um plano de anotacoes em IDC (para IDA) a partir de um JSON.

Somente biblioteca padrao. Le um JSON
{functions: [{addr, name}], comments: [{addr, text}]} e imprime um script IDC
com linhas MakeName(0xADDR, "nome"); e MakeComm(0xADDR, "comentario");.
"""

import argparse
import json


def _escape(text):
    """Escapa aspas e barras para string C do IDC."""
    return str(text).replace("\\", "\\\\").replace('"', '\\"')


def _addr(value):
    if isinstance(value, int):
        return "0x%X" % value
    text = str(value).strip()
    if text.lower().startswith("0x"):
        return "0x" + text[2:].upper()
    return "0x%X" % int(text, 0)


def generate(functions, comments):
    """Retorna o script IDC como texto."""
    lines = ["// Plano de anotacoes gerado automaticamente",
             "#include <idc.idc>", "",
             "static main()", "{"]

    for fn in functions or []:
        lines.append('    MakeName(%s, "%s");'
                     % (_addr(fn["addr"]), _escape(fn["name"])))

    for cm in comments or []:
        lines.append('    MakeComm(%s, "%s");'
                     % (_addr(cm["addr"]), _escape(cm["text"])))

    lines += ["}"]
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Gera script IDC de anotacoes (MakeName/MakeComm)."
    )
    parser.add_argument("input",
                        help="Arquivo JSON {functions: [...], comments: [...]}.")
    args = parser.parse_args(argv)
    with open(args.input, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    print(generate(data.get("functions", []), data.get("comments", [])), end="")


if __name__ == "__main__":
    main()
