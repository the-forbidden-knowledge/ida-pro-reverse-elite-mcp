#!/usr/bin/env python3
"""Valida um dump como executavel PE e avalia entry point e imports.

Le um arquivo, verifica as assinaturas MZ e PE, confere se o
AddressOfEntryPoint cai dentro de uma secao marcada como executavel e se o
diretorio de imports aponta para dentro do arquivo. Imprime um checklist
em JSON na saida padrao.
"""

import argparse
import json
import struct
import sys

IMAGE_SCN_MEM_EXECUTE = 0x20000000


def _u16(buf, off):
    return struct.unpack_from("<H", buf, off)[0]


def _u32(buf, off):
    return struct.unpack_from("<I", buf, off)[0]


def parse_pe(buf):
    """Extrai cabecalhos basicos de um PE.

    Retorna dict com entry_point, sections, import_rva e import_size.
    Levanta ValueError se o buffer nao for um PE valido.
    """
    if len(buf) < 64:
        raise ValueError("arquivo menor que o cabecalho DOS")
    if buf[0:2] != b"MZ":
        raise ValueError("magic MZ ausente")
    e_lfanew = _u32(buf, 0x3C)
    if e_lfanew + 6 > len(buf):
        raise ValueError("e_lfanew aponta para fora do arquivo")
    if buf[e_lfanew:e_lfanew + 4] != b"PE\x00\x00":
        raise ValueError("assinatura PE ausente")
    coff = e_lfanew + 4
    n_sections = _u16(buf, coff + 2)
    opt_size = _u16(buf, coff + 16)
    opt = coff + 20
    if opt + opt_size > len(buf):
        raise ValueError("optional header truncado")
    magic = _u16(buf, opt)
    if magic == 0x10B:  # PE32
        import_dir_off = opt + 96 + 8
    elif magic == 0x20B:  # PE32+
        import_dir_off = opt + 112 + 8
    else:
        raise ValueError("magic do optional header desconhecido: 0x%04x" % magic)
    if import_dir_off + 8 > len(buf):
        raise ValueError("data directories fora do arquivo")
    entry_point = _u32(buf, opt + 16)
    import_rva = _u32(buf, import_dir_off)
    import_size = _u32(buf, import_dir_off + 4)
    sections = []
    sh = opt + opt_size
    for i in range(n_sections):
        base = sh + i * 40
        if base + 40 > len(buf):
            raise ValueError("tabela de secoes truncada")
        name = buf[base:base + 8].split(b"\x00")[0].decode("ascii", "replace")
        vsize = _u32(buf, base + 8)
        vaddr = _u32(buf, base + 12)
        raw_size = _u32(buf, base + 16)
        raw_ptr = _u32(buf, base + 20)
        chars = _u32(buf, base + 36)
        sections.append({
            "name": name,
            "virtual_address": vaddr,
            "virtual_size": vsize,
            "raw_size": raw_size,
            "raw_ptr": raw_ptr,
            "characteristics": chars,
            "executable": bool(chars & IMAGE_SCN_MEM_EXECUTE),
        })
    return {
        "entry_point": entry_point,
        "sections": sections,
        "import_rva": import_rva,
        "import_size": import_size,
    }


def analyze(path):
    """Roda o checklist sobre o arquivo e retorna o dict do relatorio."""
    with open(path, "rb") as handle:
        buf = handle.read()
    checks = []
    try:
        pe = parse_pe(buf)
    except ValueError as exc:
        checks.append({"check": "cabecalhos_pe", "ok": False, "detail": str(exc)})
        return {
            "valid_pe": False,
            "ep_in_exec_section": False,
            "imports_readable": False,
            "checks": checks,
        }
    checks.append({"check": "magic_mz", "ok": True,
                   "detail": "assinatura 'MZ' presente"})
    checks.append({"check": "assinatura_pe", "ok": True,
                   "detail": "'PE\\0\\0' presente"})
    ep = pe["entry_point"]
    hit = None
    for sec in pe["sections"]:
        span = max(sec["virtual_size"], sec["raw_size"])
        if sec["virtual_address"] <= ep < sec["virtual_address"] + span:
            hit = sec
            break
    if hit and hit["executable"]:
        ep_ok = True
        ep_detail = ("entry point 0x%x dentro da secao executavel '%s'"
                     % (ep, hit["name"]))
    elif hit:
        ep_ok = False
        ep_detail = ("entry point 0x%x dentro da secao '%s', sem flag de execucao"
                     % (ep, hit["name"]))
    else:
        ep_ok = False
        ep_detail = "entry point 0x%x fora de todas as secoes" % ep
    checks.append({"check": "entry_point_em_secao_executavel",
                   "ok": ep_ok, "detail": ep_detail})
    rva, size = pe["import_rva"], pe["import_size"]
    if size == 0 or rva == 0:
        imp_ok = True
        imp_detail = "nenhum diretorio de imports declarado"
    elif rva + size <= len(buf):
        imp_ok = True
        imp_detail = ("diretorio de imports [0x%x, 0x%x) dentro do arquivo "
                      "(%d bytes)" % (rva, rva + size, len(buf)))
    else:
        imp_ok = False
        imp_detail = ("diretorio de imports [0x%x, 0x%x) fora do arquivo "
                      "(%d bytes)" % (rva, rva + size, len(buf)))
    checks.append({"check": "diretorio_de_imports_legivel",
                   "ok": imp_ok, "detail": imp_detail})
    return {
        "valid_pe": True,
        "ep_in_exec_section": ep_ok,
        "imports_readable": imp_ok,
        "checks": checks,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("arquivo", help="dump/arquivo a validar")
    args = parser.parse_args(argv)
    print(json.dumps(analyze(args.arquivo), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
