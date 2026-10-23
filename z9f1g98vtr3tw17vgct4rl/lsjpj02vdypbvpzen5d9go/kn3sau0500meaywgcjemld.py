#!/usr/bin/env python3
"""Parse do cabeçalho DEX: magic, checksum (adler32), assinatura (SHA-1),
tamanhos e offsets de string_ids/type_ids (só stdlib)."""

import argparse
import hashlib
import json
import struct
import sys
import zlib

DEX_MAGIC = b"dex\n035\x00"
HEADER_SIZE = 0x70
ENDIAN_TAG = 0x12345678

DEX_HDR = struct.Struct("<8sI20s" + "I" * 20)


class DexError(ValueError):
    """Binário inválido ou não suportado."""


def parse_dex_header(data: bytes) -> dict:
    """Faz o parse do cabeçalho DEX. Levanta DexError."""
    if len(data) < DEX_HDR.size:
        raise DexError("arquivo menor que o cabeçalho DEX")
    (magic, checksum, signature, file_size, header_size, endian_tag,
     link_size, link_off, map_off,
     string_ids_size, string_ids_off,
     type_ids_size, type_ids_off,
     proto_ids_size, proto_ids_off,
     field_ids_size, field_ids_off,
     method_ids_size, method_ids_off,
     class_defs_size, class_defs_off,
     data_size, data_off) = DEX_HDR.unpack_from(data, 0)
    if magic != DEX_MAGIC:
        raise DexError("magic inválido: %r" % magic)
    if header_size != HEADER_SIZE:
        raise DexError("header_size inesperado: 0x%x" % header_size)
    if endian_tag != ENDIAN_TAG:
        raise DexError("endian_tag inesperado: 0x%08x" % endian_tag)
    if file_size != len(data):
        raise DexError("file_size (%d) difere do tamanho real (%d)" % (file_size, len(data)))
    return {
        "formato": "DEX",
        "magic": magic.decode("ascii", "replace"),
        "checksum": "0x%08x" % checksum,
        "assinatura_sha1": signature.hex(),
        "tamanho_arquivo": file_size,
        "string_ids": {"quantidade": string_ids_size, "offset": string_ids_off},
        "type_ids": {"quantidade": type_ids_size, "offset": type_ids_off},
        "method_ids": {"quantidade": method_ids_size, "offset": method_ids_off},
        "class_defs": {"quantidade": class_defs_size, "offset": class_defs_off},
        "checksum_ok": verify_checksum(data),
        "assinatura_ok": verify_signature(data),
    }


def verify_checksum(data: bytes) -> bool:
    """Confere o adler32 (calculado sobre tudo após o campo checksum)."""
    if len(data) < DEX_HDR.size:
        return False
    (stored,) = struct.unpack_from("<I", data, 8)
    return zlib.adler32(data[12:]) & 0xFFFFFFFF == stored


def verify_signature(data: bytes) -> bool:
    """Confere o SHA-1 (calculado sobre tudo após a assinatura)."""
    if len(data) < DEX_HDR.size:
        return False
    stored = data[12:32]
    return hashlib.sha1(data[32:]).digest() == stored


def build_dex(string_ids_size: int = 0, type_ids_size: int = 0,
              method_ids_size: int = 0, class_defs_size: int = 0) -> bytes:
    """Monta um DEX sintético mínimo com checksum e assinatura válidos."""
    corpo = bytes(64)  # área de dados fictícia
    file_size = DEX_HDR.size + len(corpo)
    sem = DEX_HDR.pack(
        DEX_MAGIC, 0, bytes(20), file_size, HEADER_SIZE, ENDIAN_TAG,
        0, 0, 0,
        string_ids_size, DEX_HDR.size if string_ids_size else 0,
        type_ids_size, 0,
        0, 0, 0, 0, method_ids_size, 0, class_defs_size, 0,
        len(corpo), DEX_HDR.size)
    blob = sem + corpo
    assinatura = hashlib.sha1(blob[32:]).digest()
    blob = blob[:12] + assinatura + blob[32:]
    checksum = zlib.adler32(blob[12:]) & 0xFFFFFFFF
    blob = blob[:8] + struct.pack("<I", checksum) + blob[12:]
    return blob


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Parse do cabeçalho DEX.")
    ap.add_argument("arquivo", help="arquivo .dex")
    args = ap.parse_args(argv)
    with open(args.arquivo, "rb") as f:
        data = f.read()
    try:
        print(json.dumps(parse_dex_header(data), indent=2, ensure_ascii=False))
    except DexError as exc:
        print("erro: %s" % exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
