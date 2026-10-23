#!/usr/bin/env python3
"""Reconstroi uma tabela de imports sintetica a partir de dicas.

Entrada: JSON {"hints": {"0x401000": "kernel32.CreateFileA", ...}}.
Agrupa as entradas por DLL e, com a flag --idc, gera um script IDC com
MakeName para cada endereco (pronto para aplicar no disassembler).
Sem a flag, imprime o agrupamento em JSON.
"""

import argparse
import json
import re
import sys


def parse_address(key):
    """Aceita chaves "0x401000", decimais ("4198400") ou inteiros."""
    return int(str(key), 0)


def split_target(value):
    """Separa "dll.funcao" em (dll, funcao); sem ponto, dll = "unknown"."""
    text = str(value)
    if "." in text:
        dll, name = text.split(".", 1)
        return dll.strip() or "unknown", name.strip()
    return "unknown", text.strip()


def rebuild(hints):
    """Agrupa as dicas por DLL. Retorna {"imports": {dll: [{addr, name}]}}."""
    grouped = {}
    for key, value in hints.items():
        addr = parse_address(key)
        dll, name = split_target(value)
        dkey = dll.lower()
        grouped.setdefault(dkey, []).append({"addr": addr, "name": name})
    imports = {}
    for dll in sorted(grouped):
        entries = sorted(grouped[dll], key=lambda e: e["addr"])
        imports[dll] = [{"addr": "0x%x" % e["addr"], "name": e["name"]}
                        for e in entries]
    return {"imports": imports}


def idc_name(dll, name):
    """Nome valido para o MakeName: dll_funcao, so [A-Za-z0-9_]."""
    clean = re.sub(r"[^A-Za-z0-9_]", "_", "%s_%s" % (dll, name))
    if clean and clean[0].isdigit():
        clean = "_" + clean
    return clean or "_unnamed"


def generate_idc(rebuilt):
    """Gera o script IDC com um MakeName por endereco."""
    lines = [
        "// Tabela de imports reconstruida",
        "// gerado automaticamente",
        "",
        "static main() {",
        "    auto ea;",
    ]
    for dll in sorted(rebuilt["imports"]):
        lines.append("    // %s" % dll)
        for entry in rebuilt["imports"][dll]:
            addr = int(entry["addr"], 16)
            lines.append('    ea = 0x%08X; MakeName(ea, "%s");'
                         % (addr, idc_name(dll, entry["name"])))
    lines.append('    Message("imports nomeados\\n");')
    lines.append("}")
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entrada", help='JSON com {"hints": {...}}')
    parser.add_argument("--idc", action="store_true",
                        help="imprime script IDC em vez de JSON")
    args = parser.parse_args(argv)
    with open(args.entrada, encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, dict) and "hints" in payload:
        hints = payload["hints"]
    elif isinstance(payload, dict):
        hints = payload
    else:
        hints = {}
    rebuilt = rebuild(hints)
    if args.idc:
        sys.stdout.write(generate_idc(rebuilt))
    else:
        print(json.dumps(rebuilt, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
