#!/usr/bin/env python3
"""Lab 03 — pe-inspect: parse de cabeçalhos PE via struct.

Somente stdlib. Lê: assinatura MZ, e_lfanew, assinatura PE, cabeçalho COFF
(Machine, NumberOfSections, TimeDateStamp) e a tabela de seções
(nome, tamanho virtual, endereço virtual, tamanho bruto, características).
"""

import argparse
import json
import struct
import sys

NOMES_MACHINE = {
    0x014C: "i386",
    0x8664: "x86-64",
    0x01C0: "ARM",
    0xAA64: "ARM64",
    0x0200: "IA64",
}


def parse_pe(data):
    """Faz o parse dos cabeçalhos de um PE a partir dos bytes.

    Retorna dict {machine, machine_name, number_of_sections, timestamp,
    sections: [{name, vsize, vaddr, rawsize, rawptr, characteristics}]}.
    """
    if len(data) < 64 or data[0:2] != b"MZ":
        raise ValueError("assinatura MZ não encontrada")
    (e_lfanew,) = struct.unpack_from("<I", data, 0x3C)
    if data[e_lfanew : e_lfanew + 4] != b"PE\0\0":
        raise ValueError("assinatura PE não encontrada")
    coff = e_lfanew + 4
    (
        machine,
        num_sections,
        timestamp,
        _ptr_sym,
        _num_sym,
        opt_size,
        _chars,
    ) = struct.unpack_from("<HHIIIHH", data, coff)
    secoes = []
    base = coff + 20 + opt_size
    for i in range(num_sections):
        off = base + i * 40
        bruto = data[off : off + 40]
        if len(bruto) < 40:
            raise ValueError("tabela de seções truncada")
        nome = bruto[0:8].split(b"\x00")[0].decode("ascii", "replace")
        vsize, vaddr, rawsize, rawptr = struct.unpack_from("<IIII", bruto, 8)
        (characteristics,) = struct.unpack_from("<I", bruto, 36)
        secoes.append(
            {
                "name": nome,
                "vsize": vsize,
                "vaddr": vaddr,
                "rawsize": rawsize,
                "rawptr": rawptr,
                "characteristics": characteristics,
            }
        )
    return {
        "machine": machine,
        "machine_name": NOMES_MACHINE.get(machine, "desconhecida"),
        "number_of_sections": num_sections,
        "timestamp": timestamp,
        "sections": secoes,
    }


def inspect_pe(path):
    """Faz o parse do PE a partir de um caminho de arquivo."""
    with open(path, "rb") as f:
        data = f.read()
    return parse_pe(data)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Inspeciona cabeçalhos de um executável PE."
    )
    parser.add_argument("arquivo", help="caminho do arquivo PE")
    parser.add_argument(
        "-o", "--saida", help="grava o JSON neste arquivo (padrão: stdout)"
    )
    args = parser.parse_args(argv)
    resultado = inspect_pe(args.arquivo)
    texto = json.dumps(resultado, indent=2)
    if args.saida:
        with open(args.saida, "w", encoding="utf-8") as f:
            f.write(texto + "\n")
    else:
        print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
