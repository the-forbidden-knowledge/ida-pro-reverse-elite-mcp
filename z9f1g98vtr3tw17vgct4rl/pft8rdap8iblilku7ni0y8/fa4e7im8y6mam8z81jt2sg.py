#!/usr/bin/env python3
"""Inventario de defesas anti-analise a partir dos imports (e mnemonicos).

Entrada: JSON {"dll.dll": ["Api1", "Api2"]} (formato do inventario de imports)
         + opcional --disasm com texto de disassembly (procura mnemonicos).
Saida: JSON {"defesas": [{api, categoria, origem}], "por_categoria": {...}, "total": N}.
"""

import argparse
import json
import re
import sys

# api -> categoria (comparacao case-insensitive)
DEFESAS = {
    # deteccao de debugger
    "isdebuggerpresent": "deteccao-debugger",
    "checkremotedebuggerpresent": "deteccao-debugger",
    "ntqueryinformationprocess": "deteccao-debugger",
    "zwqueryinformationprocess": "deteccao-debugger",
    "outputdebugstringa": "deteccao-debugger",
    "outputdebugstringw": "deteccao-debugger",
    "debugbreak": "deteccao-debugger",
    "isprocessorfeaturepresent": "deteccao-debugger",
    "debugactiveprocess": "deteccao-debugger",
    # temporizacao (anti-emulacao)
    "gettickcount": "temporizacao",
    "gettickcount64": "temporizacao",
    "queryperformancecounter": "temporizacao",
    "timegettime": "temporizacao",
    "getlocaltime": "temporizacao",
    "getsystemtime": "temporizacao",
    "getsystemtimeasfiletime": "temporizacao",
    "sleep": "temporizacao",
    "ntqueryperformancounter": "temporizacao",
    # anti-sandbox (interacao humana / ambiente)
    "getcursorpos": "anti-sandbox",
    "getforegroundwindow": "anti-sandbox",
    "findwindowa": "anti-sandbox",
    "findwindoww": "anti-sandbox",
    "findwindowexa": "anti-sandbox",
    "getusernamea": "anti-sandbox",
    "getusernamew": "anti-sandbox",
    "getcomputernamea": "anti-sandbox",
    "globalmemorystatusex": "anti-sandbox",
    "createtoolhelp32snapshot": "anti-sandbox",
    "process32firstw": "anti-sandbox",
    "process32nextw": "anti-sandbox",
    "enumprocesses": "anti-sandbox",
    "getnumberofprocessors": "anti-sandbox",
    # anti-vm (checagem de ambiente virtual)
    "regopenkeyexa": "anti-vm",
    "regopenkeyexw": "anti-vm",
    "regqueryvalueexa": "anti-vm",
    "getadaptersinfo": "anti-vm",
}

# mnemonico/padrao no disassembly -> categoria
MNEMONICOS = {
    r"\brdtsc\b": "temporizacao",
    r"\bcpuid\b": "anti-vm",
    r"\bint\s+3\b": "deteccao-debugger",
    r"\bint3\b": "deteccao-debugger",
    r"\bin\s+eax\s*,\s*dx\b": "anti-vm",  # backdoor de comunicacao vmware
    r"\bvmware\b": "anti-vm",
    r"\bvbox\b": "anti-vm",
}


def scan_imports(imports):
    """Varre {dll: [apis]} e devolve achados."""
    achados = []
    vistos = set()
    for dll, apis in (imports or {}).items():
        for api in apis or []:
            chave = str(api).lower()
            if chave in DEFESAS and chave not in vistos:
                vistos.add(chave)
                achados.append({
                    "api": str(api),
                    "categoria": DEFESAS[chave],
                    "origem": "imports",
                    "dll": str(dll),
                })
    return achados


def scan_disasm(texto):
    """Procura mnemonicos anti-analise no texto de disassembly."""
    achados = []
    if not texto:
        return achados
    baixo = texto.lower()
    for padrao, categoria in MNEMONICOS.items():
        for m in re.finditer(padrao, baixo):
            achados.append({
                "api": m.group(0).strip(),
                "categoria": categoria,
                "origem": "disasm",
            })
    return achados


def build_inventory(imports, disasm_text=None):
    achados = scan_imports(imports) + scan_disasm(disasm_text)
    por_categoria = {}
    for a in achados:
        por_categoria.setdefault(a["categoria"], []).append(a["api"])
    return {
        "defesas": achados,
        "por_categoria": por_categoria,
        "total": len(achados),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Inventaria defesas anti-analise nos imports/disassembly.")
    ap.add_argument("--input", required=True,
                    help="JSON de imports {dll: [apis]}")
    ap.add_argument("--disasm", default=None,
                    help="texto de disassembly (busca mnemonicos)")
    ap.add_argument("--output", default=None,
                    help="arquivo de saida (padrao: stdout)")
    args = ap.parse_args(argv)

    with open(args.input, encoding="utf-8") as f:
        data = json.load(f)
    imports = data.get("imports", data)

    disasm_text = None
    if args.disasm:
        with open(args.disasm, encoding="utf-8") as f:
            disasm_text = f.read()

    inv = build_inventory(imports, disasm_text)
    texto = json.dumps(inv, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(texto + "\n")
    else:
        sys.stdout.write(texto + "\n")


if __name__ == "__main__":
    main()
