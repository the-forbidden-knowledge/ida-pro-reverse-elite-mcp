#!/usr/bin/env python3
"""Valida a integridade estrutural de um dump como PE.

Checa: magic MZ, assinatura PE, alinhamento das secoes (VirtualAddress
multiplo de SectionAlignment; SizeOfRawData e PointerToRawData multiplos de
FileAlignment), secoes dentro dos limites do arquivo e entry point dentro de
alguma secao. Imprime JSON com a lista de problemas encontrados.
"""

import argparse
import json
import struct
import sys


def _u16(buf, off):
    return struct.unpack_from("<H", buf, off)[0]


def _u32(buf, off):
    return struct.unpack_from("<I", buf, off)[0]


def validate(path):
    """Valida o arquivo e retorna {"ok": bool, "issues": [str]}."""
    with open(path, "rb") as handle:
        buf = handle.read()
    if len(buf) < 64 or buf[0:2] != b"MZ":
        return {"ok": False, "issues": ["magic MZ ausente ou arquivo truncado"]}
    e_lfanew = _u32(buf, 0x3C)
    if e_lfanew + 4 > len(buf) or buf[e_lfanew:e_lfanew + 4] != b"PE\x00\x00":
        return {"ok": False, "issues": ["assinatura PE ausente ou e_lfanew invalido"]}
    coff = e_lfanew + 4
    n_sections = _u16(buf, coff + 2)
    opt_size = _u16(buf, coff + 16)
    opt = coff + 20
    if opt + 2 > len(buf):
        return {"ok": False, "issues": ["optional header fora do arquivo"]}
    magic = _u16(buf, opt)
    if magic not in (0x10B, 0x20B):
        return {"ok": False, "issues": ["magic do optional header desconhecido"]}
    entry_point = _u32(buf, opt + 16)
    section_alignment = _u32(buf, opt + 32)
    file_alignment = _u32(buf, opt + 36)
    issues = []
    if section_alignment == 0 or file_alignment == 0:
        issues.append("SectionAlignment/FileAlignment com valor zero")
        section_alignment = section_alignment or 0x1000
        file_alignment = file_alignment or 0x200
    sh = opt + opt_size
    ep_inside = False
    for i in range(n_sections):
        base = sh + i * 40
        if base + 40 > len(buf):
            issues.append("tabela de secoes truncada na secao %d" % i)
            break
        name = buf[base:base + 8].split(b"\x00")[0].decode("ascii", "replace")
        vsize = _u32(buf, base + 8)
        vaddr = _u32(buf, base + 12)
        raw_size = _u32(buf, base + 16)
        raw_ptr = _u32(buf, base + 20)
        if vaddr % section_alignment != 0:
            issues.append(
                "secao '%s': VirtualAddress 0x%x nao e multiplo de "
                "SectionAlignment 0x%x" % (name, vaddr, section_alignment))
        if raw_size and raw_size % file_alignment != 0:
            issues.append(
                "secao '%s': SizeOfRawData 0x%x nao e multiplo de "
                "FileAlignment 0x%x" % (name, raw_size, file_alignment))
        if raw_ptr and raw_ptr % file_alignment != 0:
            issues.append(
                "secao '%s': PointerToRawData 0x%x nao e multiplo de "
                "FileAlignment 0x%x" % (name, raw_ptr, file_alignment))
        if raw_ptr + raw_size > len(buf):
            issues.append(
                "secao '%s': dados crus [0x%x, 0x%x) fora do arquivo "
                "(%d bytes)" % (name, raw_ptr, raw_ptr + raw_size, len(buf)))
        span = max(vsize, raw_size)
        if vaddr <= entry_point < vaddr + span:
            ep_inside = True
    if not ep_inside:
        issues.append("entry point 0x%x fora de todas as secoes" % entry_point)
    return {"ok": not issues, "issues": issues}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("arquivo", help="dump/arquivo a validar")
    args = parser.parse_args(argv)
    print(json.dumps(validate(args.arquivo), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
