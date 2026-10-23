#!/usr/bin/env python3
"""Benchmark agentes-vs-IDA (simulado, honesto).

Compara o tempo do pipeline de agentes do BAROQUE DIGITAL contra uma
baseline do fluxo manual no IDA, por tarefa. Os números de entrada são
SIMULADOS/estimados — servem para exercitar a metodologia; a medição
real exige instrumentar ambos os lados (ver README).
"""

import argparse
import json
import sys


def benchmark(tarefas: list) -> dict:
    """Calcula speedups por tarefa e totais.

    Cada tarefa: {nome, ida_segundos, baroque_segundos}.
    """
    linhas = []
    tot_ida = 0.0
    tot_baroque = 0.0
    for t in tarefas:
        ida = float(t["ida_segundos"])
        bar = float(t["baroque_segundos"])
        if bar <= 0:
            raise ValueError("tempo do baroque deve ser > 0 em '%s'" % t["nome"])
        speedup = round(ida / bar, 1)
        linhas.append({"tarefa": t["nome"], "ida_segundos": ida,
                        "baroque_segundos": bar, "speedup": speedup})
        tot_ida += ida
        tot_baroque += bar
    return {
        "tarefas": linhas,
        "total_ida": round(tot_ida, 1),
        "total_baroque": round(tot_baroque, 1),
        "speedup_total": round(tot_ida / tot_baroque, 1) if tot_baroque > 0 else 0.0,
        "simulado": True,
    }


def format_table(resultado: dict) -> str:
    """Tabela texto do benchmark."""
    linhas = ["%-28s %12s %12s %8s" % ("tarefa", "ida (s)", "baroque (s)", "speedup"),
             "-" * 64]
    for t in resultado["tarefas"]:
        linhas.append("%-28s %12.1f %12.1f %8.1fx" % (
            t["tarefa"][:28], t["ida_segundos"], t["baroque_segundos"], t["speedup"]))
    linhas.append("-" * 64)
    linhas.append("%-28s %12.1f %12.1f %8.1fx" % (
        "TOTAL", resultado["total_ida"], resultado["total_baroque"],
        resultado["speedup_total"]))
    return "\n".join(linhas)


def tarefas_padrao() -> list:
    """Cenário simulado padrão (estimativas, não medições reais)."""
    return [
        {"nome": "triagem de binário", "ida_segundos": 900, "baroque_segundos": 12},
        {"nome": "inventário de imports", "ida_segundos": 300, "baroque_segundos": 3},
        {"nome": "xrefs de uma API", "ida_segundos": 600, "baroque_segundos": 8},
        {"nome": "renomear 50 funções", "ida_segundos": 1800, "baroque_segundos": 20},
        {"nome": "relatório de clonagem", "ida_segundos": 1200, "baroque_segundos": 15},
    ]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Benchmark agentes-vs-IDA (simulado).")
    ap.add_argument("--tarefas", help="JSON com a lista de tarefas")
    args = ap.parse_args(argv)
    if args.tarefas:
        with open(args.tarefas, encoding="utf-8") as f:
            tarefas = json.load(f)
    else:
        tarefas = tarefas_padrao()
    resultado = benchmark(tarefas)
    print(format_table(resultado))
    print("\nNOTA: números simulados — metodologia de medição real no README.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
