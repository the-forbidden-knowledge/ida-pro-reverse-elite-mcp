#!/usr/bin/env python3
"""Liga comportamentos -> evidencias -> funcoes (mapa de rastreabilidade).

Entradas (JSON):
  --behaviors  spec do lab 43 {"comportamentos": [{id, ...}]}
  --evidences  {"evidencias": [{id, funcao, descricao, comportamento}]}
Saida: JSON {"mapa": {BEH-id: {funcoes, evidencias}}, "sem_evidencia": [ids]}.
"""

import argparse
import json
import sys


def build_map(comportamentos, evidencias):
    mapa = {}
    for c in comportamentos or []:
        bid = c.get("id")
        mapa[bid] = {"descricao": c.get("descricao", ""),
                     "funcoes": [], "evidencias": []}
    sem_evidencia = []
    for e in evidencias or []:
        bid = e.get("comportamento")
        if bid in mapa:
            if e.get("funcao") and e["funcao"] not in mapa[bid]["funcoes"]:
                mapa[bid]["funcoes"].append(e["funcao"])
            mapa[bid]["evidencias"].append({
                "id": e.get("id"),
                "descricao": e.get("descricao", ""),
                "funcao": e.get("funcao", ""),
            })
        # evidencias cujo comportamento nao existe na spec sao ignoradas
    # comportamentos sem nenhuma evidencia
    sem_evidencia = [bid for bid, v in mapa.items() if not v["evidencias"]]
    return {"mapa": mapa, "sem_evidencia": sem_evidencia}


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Monta mapa de rastreabilidade comportamento->evidencia->funcao.")
    ap.add_argument("--behaviors", required=True, help="JSON da spec (lab 43)")
    ap.add_argument("--evidences", required=True, help="JSON de evidencias")
    ap.add_argument("--output", default=None, help="arquivo de saida (padrao: stdout)")
    args = ap.parse_args(argv)

    with open(args.behaviors, encoding="utf-8") as f:
        spec = json.load(f)
    with open(args.evidences, encoding="utf-8") as f:
        evs = json.load(f)

    rel = build_map(spec.get("comportamentos"), evs.get("evidencias"))
    texto = json.dumps(rel, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(texto + "\n")
    else:
        sys.stdout.write(texto + "\n")


if __name__ == "__main__":
    main()
