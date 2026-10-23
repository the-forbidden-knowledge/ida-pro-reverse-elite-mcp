#!/usr/bin/env python3
"""Testes do lab 53 — elf-parse (fixtures sintéticas, sem binários reais)."""

import json
import os
import subprocess
import sys
import tempfile
import unittest

import importlib.util as _ilu
import os as _os
def _loadmod(_fname):
    _sp = _ilu.spec_from_file_location("_m", _os.path.join(_os.path.dirname(__file__), _fname))
    _mm = _ilu.module_from_spec(_sp); _sp.loader.exec_module(_mm)
    return _mm
elf_parse = _loadmod("dgwlbz9flx1esgdgsrzd7b.py")
_mx_elf_parse = _loadmod("dgwlbz9flx1esgdgsrzd7b.py")
ElfError, parse_elf, summarize = _mx_elf_parse.ElfError, _mx_elf_parse.parse_elf, _mx_elf_parse.summarize


def make_elf() -> bytes:
    """Monta um ELF64 sintético mínimo: 1 PT_LOAD + 3 seções."""
    e_ident = b"\x7fELF" + bytes([2, 1, 1, 0]) + bytes(8)
    ehdr = elf_parse.ELF64_EHDR.pack(
        e_ident, 2, 62, 1, 0x401000, 64, 64 + 56, 0,
        64, 56, 1, 64, 3, 2)
    phdr = elf_parse.ELF64_PHDR.pack(1, 5, 0, 0x400000, 0x400000, 0x1000, 0x1000, 0x1000)
    sh_null = elf_parse.ELF64_SHDR.pack(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    sh_text = elf_parse.ELF64_SHDR.pack(1, 1, 6, 0x401000, 0x1000, 0x200, 0, 0, 16, 0)
    strtab = b"\x00.text\x00.shstrtab\x00"
    strtab_off = 64 + 56 + 3 * 64
    sh_str = elf_parse.ELF64_SHDR.pack(7, 3, 0, 0, strtab_off, len(strtab), 0, 0, 1, 0)
    return ehdr + phdr + sh_null + sh_text + sh_str + strtab


class TestParseElf(unittest.TestCase):
    def test_header_ok(self):
        p = parse_elf(make_elf())
        self.assertEqual(p["formato"], "ELF64")
        self.assertEqual(p["tipo_nome"], "EXEC")
        self.assertEqual(p["maquina_nome"], "x86-64")
        self.assertEqual(p["entrada"], 0x401000)

    def test_program_header(self):
        p = parse_elf(make_elf())
        self.assertEqual(len(p["program_headers"]), 1)
        ph = p["program_headers"][0]
        self.assertEqual(ph["tipo_nome"], "PT_LOAD")
        self.assertEqual(ph["permissoes"], "R-X")
        self.assertEqual(ph["vaddr"], 0x400000)

    def test_section_names(self):
        p = parse_elf(make_elf())
        nomes = [s["nome"] for s in p["section_headers"]]
        self.assertEqual(nomes, ["", ".text", ".shstrtab"])

    def test_section_text(self):
        p = parse_elf(make_elf())
        text = p["section_headers"][1]
        self.assertEqual(text["tipo_nome"], "SHT_PROGBITS")
        self.assertEqual(text["endereco"], 0x401000)
        self.assertEqual(text["tamanho"], 0x200)

    def test_magic_invalido(self):
        with self.assertRaises(ElfError):
            parse_elf(b"MZ" + bytes(100))

    def test_arquivo_curto(self):
        with self.assertRaises(ElfError):
            parse_elf(b"\x7fELF" + bytes(10))

    def test_classe32_rejeitada(self):
        data = bytearray(make_elf())
        data[4] = 1
        with self.assertRaises(ElfError):
            parse_elf(bytes(data))


class TestSummarize(unittest.TestCase):
    def test_resumo(self):
        r = summarize(parse_elf(make_elf()))
        self.assertEqual(r["formato"], "ELF64")
        self.assertEqual(r["segmentos_carregaveis"], 1)
        self.assertIn(".text", r["secoes"])
        self.assertEqual(r["tamanho_texto"], 0x200)
        self.assertEqual(r["entrada"], "0x401000")


class TestCli(unittest.TestCase):
    def test_cli_json(self):
        with tempfile.NamedTemporaryFile(suffix=".elf", delete=False) as f:
            f.write(make_elf())
            caminho = f.name
        try:
            r = subprocess.run(
                [sys.executable, os.path.join(os.path.dirname(__file__), "dgwlbz9flx1esgdgsrzd7b.py"),
                 caminho, "--json"],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 0)
            saida = json.loads(r.stdout)
            self.assertEqual(saida["formato"], "ELF64")
        finally:
            os.unlink(caminho)


if __name__ == "__main__":
    unittest.main()
