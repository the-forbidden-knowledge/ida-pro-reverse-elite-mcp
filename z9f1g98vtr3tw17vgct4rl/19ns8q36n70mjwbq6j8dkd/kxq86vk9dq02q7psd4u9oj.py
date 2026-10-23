#!/usr/bin/env python3
"""Gera script IDC que rotula enderecos com nomes de API.

Entrada: JSON {"labels": {"0x401000": "CreateRemoteThread", ...}}
         (enderecos aceitos como "0x...", decimal em texto ou inteiro).
Saida: texto IDC com set_name() para cada endereco, ordenado por endereco.
"""

import argparse
import json
import sys


def parse_addr(value):
    """Normaliza um endereco (hex str, dec str ou int) para inteiro."""
    if isinstance(value, int):
        return value
    s = str(value).strip()
    if s.lower().startswith("0x"):
        return int(s, 16)
    return int(s)


def generate_idc(labels):
    """Monta o script IDC a partir do mapa {endereco: nome}."""
    items = sorted(labels.items(), key=lambda kv: parse_addr(kv[0]))
    lines = ["#include <idc.idc>", "", "static main() {"]
    for addr, name in items:
        ea = parse_addr(addr)
        safe = str(name).replace('"', "'")
        lines.append('    set_name(0x%X, "%s");' % (ea, safe))
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Gera script IDC rotulando enderecos com nomes de API.")
    ap.add_argument("--input", required=True,
                    help="JSON com o mapa {endereco: nome_api} (ou {'labels': {...}})")
    ap.add_argument("--output", default=None,
                    help="arquivo .idc de saida (padrao: stdout)")
    args = ap.parse_args(argv)

    with open(args.input, encoding="utf-8") as f:
        data = json.load(f)
    labels = data.get("labels", data)
    if not isinstance(labels, dict) or not labels:
        raise SystemExit("erro: nenhum rotulo encontrado no JSON de entrada")

    script = generate_idc(labels)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(script)
    else:
        sys.stdout.write(script)


if __name__ == "__main__":
    main()
