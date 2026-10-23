#!/usr/bin/env python3
"""Detecta padroes de intencao maliciosa a partir de listas de APIs importadas.

Somente biblioteca padrao. Le um JSON {apis: [nomes]} e imprime na saida
o JSON {patterns: [{apis: [...], intent: str}]} com os grupos de APIs cujos
nomes aparecem na entrada (comparacao insensivel a caixa).
"""

import argparse
import json
import sys

# Tabela embutida: grupo de APIs -> intencao.
PATTERNS = [
    (["RegOpenKeyEx", "RegSetValueEx"], "persistencia-registro"),
    (["OpenProcess", "VirtualAllocEx", "WriteProcessMemory", "CreateRemoteThread"],
     "injecao-processo"),
    (["socket", "connect", "send", "recv"], "comunicacao-rede"),
    (["CreateFile", "WriteFile"], "escrita-arquivo"),
    (["IsDebuggerPresent", "GetTickCount"], "anti-analise"),
    (["CryptEncrypt", "CryptDecrypt"], "criptografia"),
]


def detect(apis):
    """Retorna a lista de padroes cujos nomes de APIs aparecem em `apis`."""
    seen = {str(a).strip().lower() for a in (apis or [])}
    found = []
    for group, intent in PATTERNS:
        if all(name.lower() in seen for name in group):
            found.append({"apis": list(group), "intent": intent})
    return {"patterns": found}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Detecta padroes de intencao a partir de APIs importadas."
    )
    parser.add_argument("input", help="Arquivo JSON de entrada {apis: [...]}.")
    args = parser.parse_args(argv)
    with open(args.input, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    print(json.dumps(detect(data.get("apis", [])), indent=2))


if __name__ == "__main__":
    main()
