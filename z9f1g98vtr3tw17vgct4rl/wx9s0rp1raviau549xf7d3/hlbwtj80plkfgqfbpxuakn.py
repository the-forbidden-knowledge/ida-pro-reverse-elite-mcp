#!/usr/bin/env python3
"""Testes do lab 54 — macho-fat (fixtures sintéticas, sem binários reais)."""

import os
import struct
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
macho_fat = _loadmod("ak6f2jsqerwx4g7hodx44g.py")
_mx_macho_fat = _loadmod("ak6f2jsqerwx4g7hodx44g.py")
MachOError, cpu_name, parse_fat, thin = _mx_macho_fat.MachOError, _mx_macho_fat.cpu_name, _mx_macho_fat.parse_fat, _mx_macho_fat.thin

X86_64 = 0x01000007
ARM64 = 0x0100000C


def make_fat() -> bytes:
    """Monta um Mach-O fat sintético com 2 slices."""
    slice_x86 = b"X" * 64
    slice_arm = b"A" * 96
    off_x86 = 8 + 2 * 20
    off_arm = off_x86 + 64
    hdr = struct.pack(">II", 0xCAFEBABE, 2)
    a1 = struct.pack(">IIIII", X86_64, 3, off_x86, 64, 12)
    a2 = struct.pack(">IIIII", ARM64, 0, off_arm, 96, 12)
    return hdr + a1 + a2 + slice_x86 + slice_arm


class TestParseFat(unittest.TestCase):
    def test_duas_arquiteturas(self):
        p = parse_fat(make_fat())
        self.assertEqual(p["formato"], "Mach-O fat")
        self.assertEqual(len(p["arquiteturas"]), 2)

    def test_campos(self):
        p = parse_fat(make_fat())
        a0 = p["arquiteturas"][0]
        self.assertEqual(a0["cputype_nome"], "x86_64")
        self.assertEqual(a0["tamanho"], 64)
        self.assertEqual(p["arquiteturas"][1]["cputype_nome"], "arm64")

    def test_magic_invalido(self):
        with self.assertRaises(MachOError):
            parse_fat(b"MZ" + bytes(64))

    def test_arquivo_curto(self):
        with self.assertRaises(MachOError):
            parse_fat(bytes(4))


class TestThin(unittest.TestCase):
    def test_thin_x86(self):
        self.assertEqual(thin(make_fat(), X86_64), b"X" * 64)

    def test_thin_arm64(self):
        self.assertEqual(thin(make_fat(), ARM64), b"A" * 96)

    def test_thin_inexistente(self):
        with self.assertRaises(MachOError):
            thin(make_fat(), 0x0000000C)


class TestCpuName(unittest.TestCase):
    def test_conhecidos(self):
        self.assertEqual(cpu_name(X86_64), "x86_64")
        self.assertEqual(cpu_name(ARM64), "arm64")

    def test_desconhecido(self):
        self.assertIn("desconhecido", cpu_name(0xDEADBEEF))


class TestCli(unittest.TestCase):
    def test_cli_thin(self):
        with tempfile.NamedTemporaryFile(suffix=".fat", delete=False) as f:
            f.write(make_fat())
            caminho = f.name
        saida = caminho + ".arm64"
        try:
            r = subprocess.run(
                [sys.executable, os.path.join(os.path.dirname(__file__), "ak6f2jsqerwx4g7hodx44g.py"),
                 caminho, "--thin", "0x0100000c", "--saida", saida],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 0)
            with open(saida, "rb") as f:
                self.assertEqual(f.read(), b"A" * 96)
        finally:
            os.unlink(caminho)
            if os.path.exists(saida):
                os.unlink(saida)


if __name__ == "__main__":
    unittest.main()
