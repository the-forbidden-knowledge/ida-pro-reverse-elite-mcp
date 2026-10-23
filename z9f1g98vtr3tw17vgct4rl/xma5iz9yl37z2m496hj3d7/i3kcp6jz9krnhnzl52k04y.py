#!/usr/bin/env python3
"""Lab 10 — strings-navigate: da string até as funções que a usam.

Somente stdlib. Dada uma exportação em JSON
{functions: [{name, addr, size, ...}],
 strings: [{text, addr, xrefs: [endereços]}]}
e o texto de uma string, segue os xrefs até as funções cujos intervalos
de endereço contêm cada referência — os pontos de entrada que usam a string.
"""

import argparse
import json
import sys


def navigate(text, export):
    """Encontra as funções que referenciam a string.

    Retorna {string, usos: [{funcao, via}]} onde "via" é o endereço
    da referência em hexadecimal.
    """
    funcoes = export.get("functions", [])
    usos = []
    for s in export.get("strings", []):
        if s.get("text") != text:
            continue
        for xref in s.get("xrefs", []):
            for f in funcoes:
                inicio = f.get("addr", 0)
                fim = inicio + f.get("size", 0)
                if inicio <= xref < fim:
                    usos.append(
                        {"funcao": f["name"], "via": "0x%X" % xref}
                    )
                    break
    return {"string": text, "usos": usos}


def load_export(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Segue xrefs de uma string até as funções que a usam."
    )
    parser.add_argument("exportacao", help="JSON de exportação")
    parser.add_argument("--string", required=True, help="texto da string")
    parser.add_argument(
        "-o", "--saida", help="grava o JSON neste arquivo (padrão: stdout)"
    )
    args = parser.parse_args(argv)
    export = load_export(args.exportacao)
    resultado = navigate(args.string, export)
    texto = json.dumps(resultado, indent=2, ensure_ascii=False)
    if args.saida:
        with open(args.saida, "w", encoding="utf-8") as f:
            f.write(texto + "\n")
    else:
        print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
