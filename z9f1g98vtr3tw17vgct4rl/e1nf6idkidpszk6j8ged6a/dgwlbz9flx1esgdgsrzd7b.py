#!/usr/bin/env python3
"""Parse de ELF64: ELF header, program headers e section headers (só stdlib).

Lê os bytes de um binário ELF de 64 bits little-endian e devolve a
estrutura: tipo, máquina, ponto de entrada, segmentos (program headers)
e seções (section headers) com nomes resolvidos via .shstrtab.
"""

import argparse
import json
import struct
import sys

ELF_MAGIC = b"\x7fELF"
ELFCLASS64 = 2
ELFDATA2LSB = 1

ET_EXEC = 2
EM_X86_64 = 62

PT_LOAD = 1

SHT_NULL = 0
SHT_PROGBITS = 1
SHT_STRTAB = 3

ELF64_EHDR = struct.Struct("<16sHHIQQQIHHHHHH")
ELF64_PHDR = struct.Struct("<IIQQQQQQ")
ELF64_SHDR = struct.Struct("<IIQQQQIIQQ")

PT_NAMES = {
    0: "PT_NULL", 1: "PT_LOAD", 2: "PT_DYNAMIC", 3: "PT_INTERP",
    4: "PT_NOTE", 6: "PT_PHDR",
    0x6474E550: "PT_GNU_EH_FRAME", 0x6474E551: "PT_GNU_STACK",
    0x6474E552: "PT_GNU_RELRO",
}
SHT_NAMES = {
    0: "SHT_NULL", 1: "SHT_PROGBITS", 2: "SHT_SYMTAB", 3: "SHT_STRTAB",
    4: "SHT_RELA", 5: "SHT_HASH", 6: "SHT_DYNAMIC", 7: "SHT_NOTE",
    8: "SHT_NOBITS", 9: "SHT_REL", 10: "SHT_SHLIB", 11: "SHT_DYNSYM",
}


class ElfError(ValueError):
    """Binário inválido ou não suportado."""


def parse_elf(data: bytes) -> dict:
    """Faz o parse completo de um ELF64 little-endian. Levanta ElfError."""
    if len(data) < ELF64_EHDR.size:
        raise ElfError("arquivo menor que o ELF header (%d bytes)" % ELF64_EHDR.size)
    e_ident = data[:16]
    if e_ident[:4] != ELF_MAGIC:
        raise ElfError("magic inválido: não é um ELF")
    if e_ident[4] != ELFCLASS64:
        raise ElfError("só ELF64 (classe 2) é suportado")
    if e_ident[5] != ELFDATA2LSB:
        raise ElfError("só little-endian é suportado")
    (_ident, e_type, e_machine, _ver, e_entry, e_phoff, e_shoff,
     _flags, _ehsize, e_phentsize, e_phnum, e_shentsize, e_shnum,
     e_shstrndx) = ELF64_EHDR.unpack_from(data, 0)
    if e_phentsize and e_phentsize != ELF64_PHDR.size:
        raise ElfError("tamanho de program header inesperado: %d" % e_phentsize)
    if e_shentsize and e_shentsize != ELF64_SHDR.size:
        raise ElfError("tamanho de section header inesperado: %d" % e_shentsize)
    phdrs = parse_program_headers(data, e_phoff, e_phnum)
    shdrs = parse_section_headers(data, e_shoff, e_shnum)
    _resolve_section_names(data, shdrs, e_shstrndx)
    return {
        "formato": "ELF64",
        "tipo": e_type,
        "tipo_nome": "EXEC" if e_type == ET_EXEC else "OUTRO(%d)" % e_type,
        "maquina": e_machine,
        "maquina_nome": "x86-64" if e_machine == EM_X86_64 else "desconhecida(%d)" % e_machine,
        "entrada": e_entry,
        "program_headers": phdrs,
        "section_headers": shdrs,
    }


def parse_program_headers(data: bytes, phoff: int, phnum: int) -> list:
    """Lista os program headers (segmentos)."""
    out = []
    for i in range(phnum):
        off = phoff + i * ELF64_PHDR.size
        if off + ELF64_PHDR.size > len(data):
            raise ElfError("program header %d fora do arquivo" % i)
        (p_type, p_flags, p_offset, p_vaddr, _paddr,
         p_filesz, p_memsz, p_align) = ELF64_PHDR.unpack_from(data, off)
        out.append({
            "indice": i,
            "tipo": p_type,
            "tipo_nome": PT_NAMES.get(p_type, "DESCONHECIDO(%d)" % p_type),
            "flags": p_flags,
            "permissoes": _flags_str(p_flags),
            "offset": p_offset,
            "vaddr": p_vaddr,
            "filesz": p_filesz,
            "memsz": p_memsz,
            "align": p_align,
        })
    return out


def parse_section_headers(data: bytes, shoff: int, shnum: int) -> list:
    """Lista os section headers (seções)."""
    out = []
    for i in range(shnum):
        off = shoff + i * ELF64_SHDR.size
        if off + ELF64_SHDR.size > len(data):
            raise ElfError("section header %d fora do arquivo" % i)
        (sh_name, sh_type, sh_flags, sh_addr, sh_offset,
         sh_size, _link, _info, sh_addralign, _entsize) = ELF64_SHDR.unpack_from(data, off)
        out.append({
            "indice": i,
            "nome_off": sh_name,
            "nome": None,  # resolvido depois via .shstrtab
            "tipo": sh_type,
            "tipo_nome": SHT_NAMES.get(sh_type, "DESCONHECIDO(%d)" % sh_type),
            "flags": sh_flags,
            "endereco": sh_addr,
            "offset": sh_offset,
            "tamanho": sh_size,
            "alinhamento": sh_addralign,
        })
    return out


def _resolve_section_names(data: bytes, shdrs: list, shstrndx: int) -> None:
    """Preenche o campo 'nome' de cada seção usando a .shstrtab."""
    if not shdrs or shstrndx >= len(shdrs):
        return
    strtab = shdrs[shstrndx]
    base = strtab["offset"]
    size = strtab["tamanho"]
    if base + size > len(data):
        return
    raw = data[base:base + size]
    for sh in shdrs:
        off = sh["nome_off"]
        end = raw.find(b"\x00", off)
        if 0 <= off < len(raw) and end != -1:
            try:
                sh["nome"] = raw[off:end].decode("ascii")
            except UnicodeDecodeError:
                sh["nome"] = None


def _flags_str(flags: int) -> str:
    return "".join([
        "R" if flags & 4 else "-",
        "W" if flags & 2 else "-",
        "X" if flags & 1 else "-",
    ])


def summarize(parsed: dict) -> dict:
    """Resumo de alto nível para o pipeline de clonagem."""
    carregaveis = [p for p in parsed["program_headers"] if p["tipo"] == PT_LOAD]
    return {
        "formato": parsed["formato"],
        "tipo": parsed["tipo_nome"],
        "maquina": parsed["maquina_nome"],
        "entrada": "0x%x" % parsed["entrada"],
        "segmentos": len(parsed["program_headers"]),
        "segmentos_carregaveis": len(carregaveis),
        "secoes": [s["nome"] or ("#%d" % s["indice"]) for s in parsed["section_headers"]],
        "tamanho_texto": sum(s["tamanho"] for s in parsed["section_headers"]
                             if s["nome"] == ".text"),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Parse de ELF64 (header + segmentos + seções).")
    ap.add_argument("arquivo", help="binário ELF64")
    ap.add_argument("--json", action="store_true", help="saída em JSON")
    args = ap.parse_args(argv)
    with open(args.arquivo, "rb") as f:
        data = f.read()
    try:
        parsed = parse_elf(data)
    except ElfError as exc:
        print("erro: %s" % exc, file=sys.stderr)
        return 1
    resumo = summarize(parsed)
    if args.json:
        print(json.dumps(resumo, indent=2, ensure_ascii=False))
    else:
        print("ELF64 %s (%s) entrada=%s" % (resumo["tipo"], resumo["maquina"], resumo["entrada"]))
        for p in parsed["program_headers"]:
            print("  [%d] %-12s %s vaddr=0x%x filesz=%d" % (
                p["indice"], p["tipo_nome"], p["permissoes"], p["vaddr"], p["filesz"]))
        for s in parsed["section_headers"]:
            print("  (%d) %-12s %-12s addr=0x%x size=%d" % (
                s["indice"], s["nome"] or "?", s["tipo_nome"], s["endereco"], s["tamanho"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
