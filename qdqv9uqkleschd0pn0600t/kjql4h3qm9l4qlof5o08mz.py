#!/usr/bin/env python3
"""Constrói o alvo sintético da prova de clonagem: um PE 32-bit mínimo e
válido, com 2 seções (uma de alta entropia simulando packing), tabela de
imports (kernel32 + advapi32) e 3 strings ofuscadas com XOR de 1 byte.

Saída: qdqv9uqkleschd0pn0600t/target_synth.exe + qdqv9uqkleschd0pn0600t/target_spec.json (comportamento esperado).

Somente stdlib. Nenhum código real de terceiros no alvo — bytes sintéticos.
"""

import hashlib
import json
import os
import random
import struct
import sys

_AQUI = os.path.dirname(os.path.abspath(__file__))

XOR_KEY = 0x42
STRINGS = [
    "http://exemplo.local/c2",
    "Software\\Vendor\\App",
    "dados-sensiveis.bin",
]
IMPORTS = {
    "kernel32.dll": ["CreateFileA", "ReadFile", "WriteFile"],
    "advapi32.dll": ["RegSetValueExA"],
}

RV_TEXT = 0x1000
RV_PACKED = 0x2000
RAW_TEXT = 0x200
RAW_PACKED = 0x400


def _xor(data, key):
    return bytes(b ^ key for b in data)


def build_pe():
    # --- cabeçalhos ---
    dos = bytearray(64)
    dos[0:2] = b"MZ"
    struct.pack_into("<I", dos, 0x3C, 0x80)  # e_lfanew

    pe_sig = b"PE\x00\x00"
    coff = struct.pack("<HHIIIHH", 0x14C, 2, 0x5A5A5A5A, 0, 0, 0xE0, 0x010F)

    # optional header PE32 (224 bytes)
    opt = bytearray(224)
    struct.pack_into("<H", opt, 0, 0x10B)          # Magic
    struct.pack_into("<I", opt, 16, RV_TEXT)      # AddressOfEntryPoint
    struct.pack_into("<I", opt, 20, RV_TEXT)      # BaseOfCode
    struct.pack_into("<I", opt, 24, RV_PACKED)    # BaseOfData
    struct.pack_into("<I", opt, 28, 0x400000)     # ImageBase
    struct.pack_into("<I", opt, 32, 0x1000)       # SectionAlignment
    struct.pack_into("<I", opt, 36, 0x200)        # FileAlignment
    struct.pack_into("<I", opt, 56, 0x3000)       # SizeOfImage
    struct.pack_into("<I", opt, 60, 0x200)        # SizeOfHeaders
    struct.pack_into("<I", opt, 92, 16)           # NumberOfRvaAndSizes
    # DataDirectory[1] = Import Table -> RVA 0x1010
    struct.pack_into("<II", opt, 96 + 8, 0x1010, 60)

    sec_text = struct.pack("<8sIIIIIIHHI", b".text\x00\x00\x00",
                           0x200, RV_TEXT, 0x200, RAW_TEXT,
                           0, 0, 0, 0, 0x60000020)
    sec_packed = struct.pack("<8sIIIIIIHHI", b".upx0\x00\x00\x00",
                             0x400, RV_PACKED, 0x400, RAW_PACKED,
                             0, 0, 0, 0, 0xC0000040)

    headers = bytes(dos) + b"\x00" * (0x80 - 64) + pe_sig + coff + bytes(opt) \
        + sec_text + sec_packed
    assert len(headers) <= 0x200
    headers = headers + b"\x00" * (0x200 - len(headers))

    # --- seção .text: código + estruturas de import + strings ofuscadas ---
    text = bytearray(0x200)
    text[0:16] = b"\x90" * 15 + b"\xC3"  # NOPs + RET (entry point)

    def w32(rva, val):
        struct.pack_into("<I", text, rva - RV_TEXT, val)

    def wbytes(rva, blob):
        off = rva - RV_TEXT
        text[off:off + len(blob)] = blob

    # descritores de import (RVA 0x1010)
    w32(0x1010, 0x1050)          # OriginalFirstThunk kernel32
    w32(0x1014, 0)
    w32(0x1018, 0)
    w32(0x101C, 0x10C0)          # Name -> "kernel32.dll"
    w32(0x1020, 0x1050)          # FirstThunk
    w32(0x1024, 0x1060)          # OriginalFirstThunk advapi32
    w32(0x1028, 0)
    w32(0x102C, 0)
    w32(0x1030, 0x10CD)          # Name -> "advapi32.dll"
    w32(0x1034, 0x1060)          # FirstThunk
    # descritor nulo em 0x1038 (já zerado)

    # Hint/Name (RVA 0x1070)
    hn = {0x1070: "CreateFileA", 0x107D: "ReadFile",
          0x1088: "WriteFile", 0x1094: "RegSetValueExA"}
    for rva, nome in hn.items():
        wbytes(rva, b"\x00\x00" + nome.encode() + b"\x00")

    # ILT/IAT kernel32 (RVA 0x1050)
    w32(0x1050, 0x1070)
    w32(0x1054, 0x107D)
    w32(0x1058, 0x1088)
    w32(0x105C, 0)
    # ILT/IAT advapi32 (RVA 0x1060)
    w32(0x1060, 0x1094)
    w32(0x1064, 0)

    # nomes das DLLs (RVA 0x10C0)
    wbytes(0x10C0, b"kernel32.dll\x00")
    wbytes(0x10CD, b"advapi32.dll\x00")

    # strings ofuscadas com XOR (RVA 0x10E0)
    pos = 0x10E0
    for s in STRINGS:
        enc = _xor(s.encode(), XOR_KEY)
        wbytes(pos, enc + b"\x00")
        pos += len(enc) + 1

    # --- seção .packed: bytes pseudoaleatórios (alta entropia) ---
    rnd = random.Random(0xC10E)
    packed = bytes(rnd.randrange(256) for _ in range(0x400))

    return headers + bytes(text) + packed


def main(argv=None):
    pe = build_pe()
    exe_path = os.path.join(_AQUI, "target_synth.exe")
    with open(exe_path, "wb") as f:
        f.write(pe)

    spec = {
        "alvo": "target_synth.exe",
        "sha256": hashlib.sha256(pe).hexdigest(),
        "tamanho": len(pe),
        "xor_key": XOR_KEY,
        "strings_esperadas": STRINGS,
        "apis_esperadas": sorted({f for fs in IMPORTS.values() for f in fs}),
        "dlls_esperadas": sorted(IMPORTS.keys()),
        "comportamentos": [
            "cria arquivo de dados via CreateFileA ;; caminho valido ;; arquivo criado no disco",
            "le conteudo via ReadFile ;; arquivo aberto ;; bytes lidos em buffer",
            "grava resultado via WriteFile ;; buffer preenchido ;; bytes gravados no arquivo",
            "persiste configuracao via RegSetValueExA ;; chave de registro acessivel ;; valor gravado no registro",
        ],
    }
    spec_path = os.path.join(_AQUI, "target_spec.json")
    with open(spec_path, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)

    print("alvo: %s (%d bytes, sha256 %s)" %
          (exe_path, len(pe), spec["sha256"]))
    print("spec: %s" % spec_path)


if __name__ == "__main__":
    main()
