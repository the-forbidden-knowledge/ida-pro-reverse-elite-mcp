#!/usr/bin/env python3
"""Relatório consolidado de app mobile.

Junta as saídas dos labs da fase mobile (pipeline, diff, scoring,
framework, vazamentos) num relatório único do app.
"""

import argparse
import json
import sys


def gerar(dados):
    """dados: dict com chaves opcionais pipeline/diff/mobsf/hibrido/vazamentos."""
    secoes = {}
    if "pipeline" in dados:
        p = dados["pipeline"]
        secoes["pipeline"] = {
            "assinado": p.get("assinado"),
            "alinhado": p.get("alinhado"),
        }
    if "diff" in dados:
        secoes["fidelidade"] = {"score": dados["diff"].get("fidelity_score")}
    if "mobsf" in dados:
        m = dados["mobsf"]
        secoes["seguranca"] = {"score": m.get("score"), "nivel": m.get("nivel")}
    if "hibrido" in dados:
        secoes["framework"] = dados["hibrido"].get("framework")
    if "vazamentos" in dados:
        secoes["vazamentos_log"] = len(dados["vazamentos"])
    return {
        "app": dados.get("app", "desconhecido"),
        "secoes": secoes,
        "total_secoes": len(secoes),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Relatório consolidado mobile")
    args = ap.parse_args(argv)
    _ = args
    demo = {
        "app": "com.exemplo.app",
        "pipeline": {"assinado": True, "alinhado": True},
        "diff": {"fidelity_score": 97.5},
        "mobsf": {"score": 84, "nivel": "alto"},
        "hibrido": {"framework": "nativo"},
        "vazamentos": [{"linha": 3}],
    }
    json.dump(gerar(demo), sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
