#!/usr/bin/env python3
"""Transforma comportamentos observados (lista livre) em spec estruturada.

Entrada: arquivo texto, um comportamento por linha:
    descricao
    descricao ;; pre-condicao ;; efeito
  Linhas vazias e iniciadas por # sao ignoradas.
Saida: JSON {"comportamentos": [{id, descricao, pre_condicoes, efeitos}]}.
"""

import argparse
import json
import sys


def parse_spec(linhas):
    """Converte linhas livres em lista de comportamentos estruturados."""
    comportamentos = []
    n = 0
    for bruta in linhas:
        linha = bruta.strip()
        if not linha or linha.startswith("#"):
            continue
        n += 1
        partes = [p.strip() for p in linha.split(";;")]
        descricao = partes[0]
        pre = partes[1] if len(partes) > 1 else ""
        efeitos = partes[2] if len(partes) > 2 else ""
        comportamentos.append({
            "id": "BEH-%03d" % n,
            "descricao": descricao,
            "pre_condicoes": pre,
            "efeitos": efeitos,
        })
    return comportamentos


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Estrutura comportamentos observados em spec JSON.")
    ap.add_argument("--input", required=True, help="arquivo texto de comportamentos")
    ap.add_argument("--output", default=None, help="arquivo de saida (padrao: stdout)")
    args = ap.parse_args(argv)

    with open(args.input, encoding="utf-8") as f:
        comportamentos = parse_spec(f.readlines())

    texto = json.dumps({"comportamentos": comportamentos},
                       indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(texto + "\n")
    else:
        sys.stdout.write(texto + "\n")


if __name__ == "__main__":
    main()
