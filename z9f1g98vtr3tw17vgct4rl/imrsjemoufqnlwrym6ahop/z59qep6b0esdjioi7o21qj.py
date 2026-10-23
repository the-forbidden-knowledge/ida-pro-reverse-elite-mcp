#!/usr/bin/env python3
"""Lab 06 — import-inventory: parse da Import Table do PE.

Somente stdlib. Localiza o diretório de imports no optional header,
converte RVAs para offsets de arquivo via tabela de seções e percorre os
descritores (IMAGE_IMPORT_DESCRIPTOR), a ILT e as entradas Hint/Name.
"""

import argparse
import json
import struct
import sys


def _rva_para_offset(secoes, rva):
    for s in secoes:
        limite = s["vaddr"] + max(s["vsize"], s["rawsize"], 1)
        if s["vaddr"] <= rva < limite:
            return rva - s["vaddr"] + s["rawptr"]
    raise ValueError("RVA fora das seções: 0x%X" % rva)


def _cstring(data, off):
    fim = data.index(b"\x00", off)
    return data[off:fim].decode("ascii", "replace")


def _cabecalhos(data):
    if len(data) < 64 or data[0:2] != b"MZ":
        raise ValueError("assinatura MZ não encontrada")
    (e_lfanew,) = struct.unpack_from("<I", data, 0x3C)
    if data[e_lfanew : e_lfanew + 4] != b"PE\0\0":
        raise ValueError("assinatura PE não encontrada")
    coff = e_lfanew + 4
    (_m, num, _t, _p, _n, opt_size, _c) = struct.unpack_from(
        "<HHIIIHH", data, coff
    )
    opt = coff + 20
    (magic,) = struct.unpack_from("<H", data, opt)
    if magic == 0x10B:
        dd_off, nrva_off = opt + 96, opt + 92
    elif magic == 0x20B:
        dd_off, nrva_off = opt + 112, opt + 108
    else:
        raise ValueError("optional header desconhecido")
    (num_rva,) = struct.unpack_from("<I", data, nrva_off)
    import_rva = 0
    if num_rva > 1:
        (import_rva, _sz) = struct.unpack_from("<II", data, dd_off + 8)
    secoes = []
    base = coff + 20 + opt_size
    for i in range(num):
        bruto = data[base + i * 40 : base + (i + 1) * 40]
        nome = bruto[0:8].split(b"\x00")[0].decode("ascii", "replace")
        vsize, vaddr, rawsize, rawptr = struct.unpack_from("<IIII", bruto, 8)
        secoes.append(
            {
                "name": nome,
                "vsize": vsize,
                "vaddr": vaddr,
                "rawsize": rawsize,
                "rawptr": rawptr,
            }
        )
    return secoes, import_rva


def parse_imports(data):
    """Extrai a tabela de imports dos bytes do PE.

    Retorna {imports: {dll: [funções]}, total_dlls, total_funcoes}.
    Import por ordinal vira "ordinal_N".
    """
    secoes, import_rva = _cabecalhos(data)
    imports = {}
    if import_rva:
        off = _rva_para_offset(secoes, import_rva)
        while True:
            desc = data[off : off + 20]
            if len(desc) < 20 or desc == b"\x00" * 20:
                break
            oft, _ts, _fc, name_rva, ft = struct.unpack("<IIIII", desc)
            dll = _cstring(data, _rva_para_offset(secoes, name_rva))
            thunk = oft or ft
            funcoes = []
            t = _rva_para_offset(secoes, thunk)
            while True:
                (entry,) = struct.unpack_from("<I", data, t)
                if entry == 0:
                    break
                if entry & 0x80000000:
                    funcoes.append("ordinal_%d" % (entry & 0xFFFF))
                else:
                    hn = _rva_para_offset(secoes, entry & 0x7FFFFFFF)
                    funcoes.append(_cstring(data, hn + 2))
                t += 4
            imports[dll] = funcoes
            off += 20
    return {
        "imports": imports,
        "total_dlls": len(imports),
        "total_funcoes": sum(len(v) for v in imports.values()),
    }


def import_inventory(path):
    """Extrai a tabela de imports a partir de um caminho de arquivo."""
    with open(path, "rb") as f:
        data = f.read()
    return parse_imports(data)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Lista as DLLs e funções importadas por um PE."
    )
    parser.add_argument("arquivo", help="caminho do arquivo PE")
    parser.add_argument(
        "-o", "--saida", help="grava o JSON neste arquivo (padrão: stdout)"
    )
    args = parser.parse_args(argv)
    resultado = import_inventory(args.arquivo)
    texto = json.dumps(resultado, indent=2)
    if args.saida:
        with open(args.saida, "w", encoding="utf-8") as f:
            f.write(texto + "\n")
    else:
        print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
