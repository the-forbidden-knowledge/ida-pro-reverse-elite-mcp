#!/usr/bin/env python3
"""Parse de Mach-O universal ("fat"): magic 0xcafebabe + thinning por cputype.

Um binário "fat" empacota um Mach-O por arquitetura. Este lab lê o
cabeçalho fat (big-endian), lista as arquiteturas e extrai ("thinning")
o slice da arquitetura pedida.
"""

import argparse
import json
import struct
import sys

FAT_MAGIC = 0xCAFEBABE
FAT_CIGAM = 0xBEBAFECA  # little-endian variant (não suportado aqui)

FAT_HEADER = struct.Struct(">II")
FAT_ARCH = struct.Struct(">IIIII")

CPU_TYPES = {
    0x00000007: "i386",
    0x01000007: "x86_64",
    0x0000000C: "arm",
    0x0100000C: "arm64",
}


class MachOError(ValueError):
    """Binário inválido ou não suportado."""


def parse_fat(data: bytes) -> dict:
    """Faz o parse do cabeçalho fat. Levanta MachOError."""
    if len(data) < FAT_HEADER.size:
        raise MachOError("arquivo menor que o cabeçalho fat")
    (magic, nfat_arch) = FAT_HEADER.unpack_from(data, 0)
    if magic == FAT_CIGAM:
        raise MachOError("variante little-endian (CIGAM) não suportada")
    if magic != FAT_MAGIC:
        raise MachOError("magic inválido: 0x%08x (não é Mach-O fat)" % magic)
    archs = []
    for i in range(nfat_arch):
        off = FAT_HEADER.size + i * FAT_ARCH.size
        if off + FAT_ARCH.size > len(data):
            raise MachOError("entrada fat %d fora do arquivo" % i)
        (cputype, cpusubtype, offset, size, align) = FAT_ARCH.unpack_from(data, off)
        if offset + size > len(data):
            raise MachOError("slice %d fora do arquivo" % i)
        archs.append({
            "indice": i,
            "cputype": cputype,
            "cputype_nome": CPU_TYPES.get(cputype, "desconhecido(0x%08x)" % cputype),
            "cpusubtype": cpusubtype,
            "offset": offset,
            "tamanho": size,
            "alinhamento": 2 ** align,
        })
    return {"formato": "Mach-O fat", "magic": "0xcafebabe", "arquiteturas": archs}


def thin(data: bytes, cputype: int) -> bytes:
    """Extrai o slice da arquitetura pedida (thinning). Levanta MachOError."""
    parsed = parse_fat(data)
    for arch in parsed["arquiteturas"]:
        if arch["cputype"] == cputype:
            return data[arch["offset"]:arch["offset"] + arch["tamanho"]]
    raise MachOError("arquitetura 0x%08x não encontrada no fat" % cputype)


def cpu_name(cputype: int) -> str:
    """Nome amigável do cputype."""
    return CPU_TYPES.get(cputype, "desconhecido(0x%08x)" % cputype)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Parse de Mach-O fat + thinning.")
    ap.add_argument("arquivo", help="binário Mach-O universal")
    ap.add_argument("--thin", metavar="CPUTYPE",
                    help="extrai o slice (ex.: 0x0100000c para arm64)")
    ap.add_argument("--saida", help="arquivo de saída do slice")
    args = ap.parse_args(argv)
    with open(args.arquivo, "rb") as f:
        data = f.read()
    try:
        if args.thin:
            cputype = int(args.thin, 0)
            fatia = thin(data, cputype)
            if args.saida:
                with open(args.saida, "wb") as f:
                    f.write(fatia)
            print("slice %s: %d bytes" % (cpu_name(cputype), len(fatia)))
        else:
            parsed = parse_fat(data)
            print(json.dumps(parsed, indent=2, ensure_ascii=False))
    except MachOError as exc:
        print("erro: %s" % exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
