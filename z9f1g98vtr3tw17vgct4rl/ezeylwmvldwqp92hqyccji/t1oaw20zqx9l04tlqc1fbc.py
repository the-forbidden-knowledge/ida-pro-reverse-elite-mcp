#!/usr/bin/env python3
"""Despejo de Mach-O descriptografado (estilo dumpdecrypted).

Simula a mecânica: o binário carrega criptografado (cryptid=1) e o
loader o descriptografa em runtime; o despejo copia as regiões __TEXT
já limpas e zera o cryptid. Sem isso não existe análise estática.
"""

import argparse
import json
import struct
import sys

FORMATO = "<4sIII"  # magic, cryptoff, cryptsize, cryptid
TAMANHO = struct.calcsize(FORMATO)
MAGIC = b"\xfe\xed\xfa\xce"


def despejar(dados):
    """Retorna o binário com a região criptografada despejada limpa."""
    if len(dados) < TAMANHO:
        raise ValueError("binário curto demais para o cabeçalho")
    magic, off, size, cid = struct.unpack_from(FORMATO, dados, 0)
    if magic != MAGIC:
        raise ValueError("magic inválido: não é Mach-O")
    if cid == 0:
        return {"despejado": False, "dados": dados}
    if off + size > len(dados):
        raise ValueError("região criptografada fora do binário")
    corpo = bytearray(dados)
    for i in range(size):
        corpo[off + i] = (i * 31 + 7) % 256
    struct.pack_into("<I", corpo, 12, 0)  # cryptid = 0
    return {"despejado": True, "dados": bytes(corpo), "regiao": [off, size]}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Despeja Mach-O descriptografado")
    args = ap.parse_args(argv)
    _ = args
    blob = MAGIC + struct.pack("<III", 16, 64, 1) + bytes([0xAA] * 64)
    r = despejar(blob)
    json.dump(
        {
            "despejado": r["despejado"],
            "regiao": r.get("regiao"),
            "tamanho": len(r["dados"]),
        },
        sys.stdout,
        ensure_ascii=False,
    )
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
