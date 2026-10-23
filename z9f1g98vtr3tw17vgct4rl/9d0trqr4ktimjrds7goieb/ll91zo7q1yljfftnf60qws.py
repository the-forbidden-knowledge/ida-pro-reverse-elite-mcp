#!/usr/bin/env python3
"""Lab 09 — xref-trace: cadeia de chamadores até uma API-alvo.

Somente stdlib. Dada uma exportação em JSON
{functions: [{name, calls: [...]}, ...]} e uma API-alvo, reconstrói o grafo
de chamadas e enumera todos os caminhos das funções raiz (que ninguém
chama) até o alvo — a cadeia de xrefs que leva à chamada.
"""

import argparse
import json
import sys


def trace(api, functions):
    """Enumera caminhos das raízes até a API-alvo.

    Retorna {alvo, cadeias: [[raiz, ..., alvo], ...]}.
    """
    calls = {f["name"]: list(f.get("calls", [])) for f in functions}
    chamados = set()
    for cs in calls.values():
        chamados.update(cs)
    raizes = [n for n in calls if n not in chamados]
    cadeias = []

    def dfs(no, alvo, caminho, visitados):
        if no == alvo:
            cadeias.append(caminho + [no])
            return
        for prox in calls.get(no, []):
            if prox not in visitados:
                dfs(prox, alvo, caminho + [no], visitados | {prox})

    for r in raizes:
        dfs(r, api, [], {r})
    return {"alvo": api, "cadeias": cadeias}


def load_export(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Lista cadeias de chamadores até uma API-alvo."
    )
    parser.add_argument("exportacao", help="JSON de exportação das funções")
    parser.add_argument("--api", required=True, help="API-alvo (ex.: CreateFileW)")
    parser.add_argument(
        "-o", "--saida", help="grava o JSON neste arquivo (padrão: stdout)"
    )
    args = parser.parse_args(argv)
    export = load_export(args.exportacao)
    resultado = trace(args.api, export.get("functions", []))
    texto = json.dumps(resultado, indent=2, ensure_ascii=False)
    if args.saida:
        with open(args.saida, "w", encoding="utf-8") as f:
            f.write(texto + "\n")
    else:
        print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
