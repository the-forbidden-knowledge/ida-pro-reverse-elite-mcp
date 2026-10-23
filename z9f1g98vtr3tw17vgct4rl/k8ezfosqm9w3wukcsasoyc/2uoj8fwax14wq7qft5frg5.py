#!/usr/bin/env python3
"""Remove a relocacao de base (ASLR) de um PE.

Zera a flag IMAGE_DLLCHARACTERISTICS_DYNAMIC_BASE (0x0040) no campo
DllCharacteristics do optional header, com edicao in-place via struct.
Antes de qualquer escrita, cria um backup "<arquivo>.bak".
Imprime JSON com o resultado.
"""

import argparse
import json
import shutil
import struct
import sys

IMAGE_DLLCHARACTERISTICS_DYNAMIC_BASE = 0x0040


def dll_characteristics_offset(buf):
    """Retorna o offset em arquivo do campo DllCharacteristics.

    Suporta PE32 (offset +68 no optional header) e PE32+ (offset +70).
    Levanta ValueError se o buffer nao for um PE valido.
    """
    if len(buf) < 64 or buf[0:2] != b"MZ":
        raise ValueError("magic MZ ausente")
    e_lfanew = struct.unpack_from("<I", buf, 0x3C)[0]
    if e_lfanew + 4 > len(buf) or buf[e_lfanew:e_lfanew + 4] != b"PE\x00\x00":
        raise ValueError("assinatura PE ausente")
    opt = e_lfanew + 24
    if opt + 2 > len(buf):
        raise ValueError("optional header fora do arquivo")
    magic = struct.unpack_from("<H", buf, opt)[0]
    if magic == 0x10B:
        return opt + 68
    if magic == 0x20B:
        return opt + 70
    raise ValueError("magic do optional header desconhecido: 0x%04x" % magic)


def read_dll_characteristics(path):
    """Le o valor atual de DllCharacteristics sem modificar o arquivo."""
    with open(path, "rb") as handle:
        buf = handle.read()
    off = dll_characteristics_offset(buf)
    return struct.unpack_from("<H", buf, off)[0]


def strip_aslr(path):
    """Faz backup .bak, zera a flag e retorna {"patched", "backup"}.

    patched e True apenas se a flag estava ligada e foi zerada; as demais
    flags de DllCharacteristics sao preservadas.
    """
    with open(path, "rb") as handle:
        buf = bytearray(handle.read())
    off = dll_characteristics_offset(buf)
    old = struct.unpack_from("<H", buf, off)[0]
    backup = path + ".bak"
    shutil.copy2(path, backup)
    patched = bool(old & IMAGE_DLLCHARACTERISTICS_DYNAMIC_BASE)
    if patched:
        struct.pack_into("<H", buf, off, old & ~IMAGE_DLLCHARACTERISTICS_DYNAMIC_BASE)
        with open(path, "wb") as handle:
            handle.write(buf)
    return {"patched": patched, "backup": backup}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("arquivo", help="PE a modificar (backup .bak antes)")
    args = parser.parse_args(argv)
    try:
        result = strip_aslr(args.arquivo)
    except (ValueError, OSError) as exc:
        print(json.dumps({"patched": False, "backup": "",
                          "error": str(exc)}, ensure_ascii=False))
        sys.exit(1)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
