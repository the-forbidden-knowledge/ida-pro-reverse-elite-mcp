#!/usr/bin/env python3
"""Relatorio final CLONAR: consolida as 8 fases do 9pd1ao2s9soicz7ndhxu9e.

Entrada: --manifest JSON {"triagem": "caminho", "leitura": "caminho",
  "unpack": ..., "desobfuscacao": ..., "injecao": ..., "memoria": ...,
  "bypass": ..., "reconstrucao": ...} (caminhos opcionais).
Saida: JSON (padrao) ou Markdown (--format md) com o resumo de cada fase.
"""

import argparse
import datetime
import json
import os
import sys

FASES = ["triagem", "leitura", "unpack", "desobfuscacao",
         "injecao", "memoria", "bypass", "reconstrucao"]


def resumir_fase(dados):
    """Extrai um resumo curto do JSON de uma fase."""
    if not isinstance(dados, dict):
        return {"itens": 0}
    if "resumo" in dados and isinstance(dados["resumo"], dict):
        return dict(dados["resumo"])
    return {"chaves": sorted(dados.keys())[:8], "total_chaves": len(dados)}


def build_report(manifest):
    fases = {}
    for fase in FASES:
        caminho = (manifest or {}).get(fase)
        if caminho and os.path.exists(caminho):
            try:
                with open(caminho, encoding="utf-8") as f:
                    dados = json.load(f)
                fases[fase] = {"arquivo": caminho, "status": "ok",
                               "resumo": resumir_fase(dados)}
            except (json.JSONDecodeError, OSError) as e:
                fases[fase] = {"arquivo": caminho, "status": "erro",
                               "detalhe": str(e)}
        else:
            fases[fase] = {"arquivo": caminho, "status": "nao-executada"}

    executadas = sum(1 for f in fases.values() if f["status"] == "ok")
    return {
        "relatorio": "CLONAR",
        "gerado_em": datetime.datetime.now().isoformat(timespec="seconds"),
        "fases": fases,
        "resumo": {
            "fases_executadas": executadas,
            "fases_totais": len(FASES),
            "fases_pendentes": [f for f in FASES if fases[f]["status"] != "ok"],
        },
    }


def to_markdown(rel):
    linhas = ["# Relatorio CLONAR", "",
               "Gerado em: %s" % rel["gerado_em"], "",
               "## Fases", ""]
    for fase in FASES:
        f = rel["fases"][fase]
        linhas.append("### %s — %s" % (fase, f["status"]))
        if f["status"] == "ok":
            linhas.append("")
            linhas.append("Arquivo: `%s`" % f["arquivo"])
            linhas.append("")
            linhas.append("```json")
            linhas.append(json.dumps(f["resumo"], indent=2, ensure_ascii=False))
            linhas.append("```")
            linhas.append("")
    r = rel["resumo"]
    linhas.append("## Resumo")
    linhas.append("")
    linhas.append("Fases executadas: %d/%d" % (r["fases_executadas"], r["fases_totais"]))
    if r["fases_pendentes"]:
        linhas.append("Pendentes: %s" % ", ".join(r["fases_pendentes"]))
    linhas.append("")
    return "\n".join(linhas)


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Relatorio final consolidando as 8 fases do 9pd1ao2s9soicz7ndhxu9e.")
    ap.add_argument("--manifest", required=True,
                    help="JSON mapeando fase -> arquivo de saida")
    ap.add_argument("--format", choices=["json", "md"], default="json",
                    help="formato de saida (padrao: json)")
    ap.add_argument("--output", default=None, help="arquivo de saida (padrao: stdout)")
    args = ap.parse_args(argv)

    with open(args.manifest, encoding="utf-8") as f:
        manifest = json.load(f)

    rel = build_report(manifest)
    texto = to_markdown(rel) if args.format == "md" else \
        json.dumps(rel, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(texto + "\n")
    else:
        sys.stdout.write(texto + "\n")


if __name__ == "__main__":
    main()
