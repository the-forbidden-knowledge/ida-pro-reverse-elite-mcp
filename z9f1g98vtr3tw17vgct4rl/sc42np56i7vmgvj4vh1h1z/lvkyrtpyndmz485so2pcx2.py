#!/usr/bin/env python3
"""REPL de exploração runtime mobile (estilo Objection).

Simula os comandos `android hooking watch class` e `memory list
modules` sobre um estado sintético do app — exploração dinâmica
sem escrever JavaScript à mão.
"""

import argparse
import json
import sys


def executar(comando, estado):
    """Executa um comando do REPL sobre o estado do app."""
    p = comando.strip().split()
    if (
        len(p) >= 5
        and p[0] == "android"
        and p[1] == "hooking"
        and p[2] == "watch"
        and p[3] == "class"
    ):
        cls = p[4]
        metodos = estado.get("classes", {}).get(cls)
        if metodos is None:
            return {"erro": "classe nao encontrada: " + cls}
        return {"classe": cls, "metodos_observados": metodos}
    if p == ["memory", "list", "modules"]:
        return {"modulos": estado.get("modulos", [])}
    return {"erro": "comando desconhecido"}


def main(argv=None):
    ap = argparse.ArgumentParser(description="REPL de exploração runtime")
    ap.add_argument("comando", nargs="?", default="memory list modules")
    args = ap.parse_args(argv)
    estado = {
        "classes": {"com.exemplo.Login": ["autenticar", "sair"]},
        "modulos": [
            {"nome": "libapp.so", "base": "0x7f001000"},
            {"nome": "libssl.so", "base": "0x7f002000"},
        ],
    }
    json.dump(executar(args.comando, estado), sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
