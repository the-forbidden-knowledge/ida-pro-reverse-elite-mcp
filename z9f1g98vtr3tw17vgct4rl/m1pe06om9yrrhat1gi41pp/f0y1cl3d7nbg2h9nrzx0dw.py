#!/usr/bin/env python3
"""Verifica a paridade do clone contra a spec original de comportamentos.

Entrada: spec JSON do lab 43 do ORIGINAL e spec JSON do CLONE
         (mesmo formato {"comportamentos": [{id, descricao, ...}]}),
         mais artefatos (arquivos ou diretorios) para hash SHA-256.
Saida: relatorio de paridade {cobertos, faltando, extras,
       cobertura_pct, artefatos, veredito}. O veredito e "CLONADO 100%"
       somente quando nao ha faltando nem extras.
"""

import argparse
import hashlib
import json
import os
import re
import sys


def normaliza(texto):
    """Minusculas, espacos colapsados: base da comparacao."""
    return re.sub(r"\s+", " ", (texto or "").strip().lower())


def compara(original, clone):
    """Retorna (cobertos, faltando, extras) por descricao normalizada."""
    orig = {normaliza(c.get("descricao")): c for c in original or []}
    clon = {normaliza(c.get("descricao")): c for c in clone or []}
    cobertos, faltando, extras = [], [], []
    for chave, c in orig.items():
        if chave in clon:
            cobertos.append({"id": c.get("id"),
                             "descricao": c.get("descricao")})
        else:
            faltando.append({"id": c.get("id"),
                             "descricao": c.get("descricao")})
    for chave, c in clon.items():
        if chave not in orig:
            extras.append({"id": c.get("id"),
                           "descricao": c.get("descricao")})
    return cobertos, faltando, extras


def sha256_arquivo(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(65536), b""):
            h.update(bloco)
    return h.hexdigest()


def coleta_artefatos(caminhos):
    """Arquivos recebem hash direto; diretorios sao varridos recursivamente."""
    arquivos = []
    for c in caminhos or []:
        if os.path.isdir(c):
            for raiz, _dirs, nomes in os.walk(c):
                for n in sorted(nomes):
                    arquivos.append(os.path.join(raiz, n))
        elif os.path.isfile(c):
            arquivos.append(c)
    return [{"arquivo": a, "sha256": sha256_arquivo(a)}
            for a in sorted(arquivos)]


def veredito(faltando, extras):
    if not faltando and not extras:
        return "CLONADO 100%"
    partes = []
    if faltando:
        partes.append("GAPS: %d comportamento(s) nao implementado(s)"
                      % len(faltando))
    if extras:
        partes.append("DIVERGENCIAS: %d comportamento(s) extra(s) no clone"
                      % len(extras))
    return " | ".join(partes)


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Verifica paridade do clone contra a spec original.")
    ap.add_argument("--original", required=True,
                    help="spec JSON original (lab 43)")
    ap.add_argument("--clone", required=True,
                    help="spec JSON do clone (lab 43)")
    ap.add_argument("--artefatos", nargs="*", default=[],
                    help="arquivos/diretorios para hash SHA-256")
    ap.add_argument("--output", default=None,
                    help="JSON de saida (padrao: stdout)")
    args = ap.parse_args(argv)

    with open(args.original, encoding="utf-8") as f:
        spec_orig = json.load(f).get("comportamentos", [])
    with open(args.clone, encoding="utf-8") as f:
        spec_clone = json.load(f).get("comportamentos", [])

    cobertos, faltando, extras = compara(spec_orig, spec_clone)
    pct = (100.0 * len(cobertos) / len(spec_orig)) if spec_orig else 100.0
    relatorio = {
        "cobertos": cobertos,
        "faltando": faltando,
        "extras": extras,
        "cobertura_pct": round(pct, 2),
        "total_original": len(spec_orig),
        "artefatos": coleta_artefatos(args.artefatos),
        "veredito": veredito(faltando, extras),
    }
    texto = json.dumps(relatorio, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(texto)
    else:
        sys.stdout.write(texto)


if __name__ == "__main__":
    main()
