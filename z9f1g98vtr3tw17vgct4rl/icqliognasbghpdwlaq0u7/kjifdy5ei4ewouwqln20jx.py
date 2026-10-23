#!/usr/bin/env python3
"""Lab 11 — library-filter: separa código-autor de código-biblioteca.

Somente stdlib. Dada uma lista de funções e padrões (regex) de biblioteca
— prefixos de compilador, thunks, namespaces da STL etc. — classifica cada
função como "biblioteca" ou "autor". Focar no código-autor economiza a
maior parte do tempo de leitura.
"""

import argparse
import json
import re
import sys


def classify(functions, patterns):
    """Classifica funções em biblioteca vs. autor.

    functions: lista de nomes ou de dicts com "name".
    patterns: lista de regex; qualquer match => biblioteca.
    Retorna {biblioteca: [...], autor: [...]}.
    """
    compilados = [re.compile(p) for p in patterns]
    biblioteca, autor = [], []
    for f in functions:
        nome = f["name"] if isinstance(f, dict) else f
        if any(p.search(nome) for p in compilados):
            biblioteca.append(nome)
        else:
            autor.append(nome)
    return {"biblioteca": biblioteca, "autor": autor}


def load_export(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Separa funções de biblioteca das funções do autor."
    )
    parser.add_argument("exportacao", help="JSON com a lista de funções")
    parser.add_argument(
        "--pattern",
        action="append",
        default=[],
        help="regex de biblioteca (pode repetir)",
    )
    parser.add_argument(
        "-o", "--saida", help="grava o JSON neste arquivo (padrão: stdout)"
    )
    args = parser.parse_args(argv)
    export = load_export(args.exportacao)
    funcoes = export.get("functions", [])
    padroes = list(export.get("library_patterns", [])) + args.pattern
    resultado = classify(funcoes, padroes)
    texto = json.dumps(resultado, indent=2, ensure_ascii=False)
    if args.saida:
        with open(args.saida, "w", encoding="utf-8") as f:
            f.write(texto + "\n")
    else:
        print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
