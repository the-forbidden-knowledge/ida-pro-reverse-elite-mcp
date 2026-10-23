#!/usr/bin/env python3
"""Gera esqueleto Python do clone a partir da spec de comportamentos.

Entrada: spec JSON do lab 43 {"comportamentos": [{id, descricao,
         pre_condicoes, efeitos}]} e, opcional, o mapa do lab 44
         {"mapa": {BEH-id: {funcoes, evidencias}}}.
Saida: arquivo .py com uma funcao stub por comportamento; a docstring
       carrega descricao, pre-condicoes, efeitos e evidencias, e o corpo
       traz TODOs apontando o que implementar.
"""

import argparse
import json
import re
import sys


def slug(texto, limite=40):
    """Converte descricao livre em identificador snake_case."""
    t = texto.lower()
    t = re.sub(r"[^a-z0-9]+", "_", t)
    t = t.strip("_")
    t = t[:limite].rstrip("_")
    return t or "sem_nome"


def nome_funcao(bid, descricao, usados):
    """Monta nome unico: beh_001_descricao (resolve colisoes)."""
    base = "%s_%s" % (bid.lower().replace("-", "_"), slug(descricao))
    nome = base
    n = 2
    while nome in usados:
        nome = "%s_%d" % (base, n)
        n += 1
    usados.add(nome)
    return nome


def gera_stub(comportamento, vinculo):
    """Monta o texto de uma funcao stub."""
    bid = comportamento.get("id", "BEH-???")
    descricao = comportamento.get("descricao", "")
    pre = (comportamento.get("pre_condicoes") or "").strip()
    efeitos = (comportamento.get("efeitos") or "").strip()

    linhas = []
    linhas.append('    """%s.' % descricao)
    linhas.append("")
    if pre:
        linhas.append("    Pre-condicoes: %s" % pre)
    if efeitos:
        linhas.append("    Efeitos: %s" % efeitos)
    if pre or efeitos:
        linhas.append("")
    if vinculo:
        evs = vinculo.get("evidencias", [])
        fns = vinculo.get("funcoes", [])
        if evs:
            linhas.append("    Evidencias:")
            for e in evs:
                linhas.append("      - %s [%s]: %s" % (
                    e.get("id", "?"), e.get("funcao", "?"),
                    e.get("descricao", "")))
        if fns:
            linhas.append("    Funcoes de referencia: %s" % ", ".join(fns))
        linhas.append("")
    linhas.append('    """')

    nome = vinculo.get("_nome") if vinculo else None
    linhas.insert(0, "def %s():" % nome)
    if vinculo and vinculo.get("evidencias"):
        linhas.append("    # TODO: implementar a partir das evidencias acima")
    else:
        linhas.append("    # TODO: sem evidencia vinculada - investigar antes")
    if vinculo and vinculo.get("funcoes"):
        linhas.append("    # TODO: funcoes de referencia: %s"
                     % ", ".join(vinculo["funcoes"]))
    linhas.append('    raise NotImplementedError("%s: pendente")' % bid)
    return "\n".join(linhas)


def gera_esqueleto(comportamentos, mapa):
    """Gera o modulo .py completo."""
    usados = set()
    blocos = []
    for c in comportamentos or []:
        bid = c.get("id", "")
        vinc = dict((mapa or {}).get(bid, {}))
        vinc["_nome"] = nome_funcao(bid, c.get("descricao", ""), usados)
        blocos.append(gera_stub(c, vinc))
    cabecalho = (
        '"""Esqueleto do clone gerado a partir da spec de comportamentos.\n'
        '\n'
        'Cada funcao corresponde a um comportamento observado. Implemente o\n'
        'corpo a partir das evidencias listadas na docstring.\n'
        '"""\n'
    )
    return cabecalho + "\n\n\n".join(blocos) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Gera esqueleto Python do clone a partir da spec.")
    ap.add_argument("--spec", required=True,
                    help="spec JSON do lab 43")
    ap.add_argument("--map", default=None,
                    help="mapa JSON do lab 44 (opcional)")
    ap.add_argument("--output", default=None,
                    help="arquivo .py de saida (padrao: stdout)")
    args = ap.parse_args(argv)

    with open(args.spec, encoding="utf-8") as f:
        spec = json.load(f)
    mapa = {}
    if args.map:
        with open(args.map, encoding="utf-8") as f:
            mapa = json.load(f).get("mapa", {})

    texto = gera_esqueleto(spec.get("comportamentos", []), mapa)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(texto)
    else:
        sys.stdout.write(texto)


if __name__ == "__main__":
    main()
