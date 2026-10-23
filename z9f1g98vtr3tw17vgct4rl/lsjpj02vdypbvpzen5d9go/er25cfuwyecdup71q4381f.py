#!/usr/bin/env python3
"""Testes do lab 55 — dex-header (fixtures sintéticas, sem binários reais)."""

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
_mx_dex_header = _loadmod("kn3sau0500meaywgcjemld.py")
DexError, build_dex, main, parse_dex_header, verify_checksum, verify_signature = _mx_dex_header.DexError, _mx_dex_header.build_dex, _mx_dex_header.main, _mx_dex_header.parse_dex_header, _mx_dex_header.verify_checksum, _mx_dex_header.verify_signature


class TestParseDex(unittest.TestCase):
    def test_header_ok(self):
        p = parse_dex_header(build_dex(string_ids_size=10, type_ids_size=4))
        self.assertEqual(p["formato"], "DEX")
        self.assertEqual(p["string_ids"]["quantidade"], 10)
        self.assertEqual(p["type_ids"]["quantidade"], 4)
        self.assertTrue(p["checksum_ok"])
        self.assertTrue(p["assinatura_ok"])

    def test_magic_invalido(self):
        with self.assertRaises(DexError):
            parse_dex_header(b"\x7fELF" + bytes(200))

    def test_arquivo_curto(self):
        with self.assertRaises(DexError):
            parse_dex_header(b"dex\n")

    def test_tamanhos(self):
        p = parse_dex_header(build_dex(method_ids_size=7, class_defs_size=2))
        self.assertEqual(p["method_ids"]["quantidade"], 7)
        self.assertEqual(p["class_defs"]["quantidade"], 2)


class TestVerify(unittest.TestCase):
    def test_checksum_ok(self):
        self.assertTrue(verify_checksum(build_dex()))

    def test_checksum_corrompido(self):
        data = bytearray(build_dex())
        data[50] ^= 0xFF
        self.assertFalse(verify_checksum(bytes(data)))

    def test_assinatura_ok(self):
        self.assertTrue(verify_signature(build_dex()))

    def test_assinatura_corrompida(self):
        data = bytearray(build_dex())
        data[60] ^= 0xFF
        self.assertFalse(verify_signature(bytes(data)))

    def test_curto_retorna_false(self):
        self.assertFalse(verify_checksum(b"dex"))
        self.assertFalse(verify_signature(b"dex"))


class TestCli(unittest.TestCase):
    def test_cli(self):
        with tempfile.NamedTemporaryFile(suffix=".dex", delete=False) as f:
            f.write(build_dex(string_ids_size=3))
            caminho = f.name
        try:
            r = subprocess.run(
                [sys.executable, os.path.join(os.path.dirname(__file__), "kn3sau0500meaywgcjemld.py"),
                 caminho],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 0)
            saida = json.loads(r.stdout)
            self.assertEqual(saida["string_ids"]["quantidade"], 3)
        finally:
            os.unlink(caminho)


if __name__ == "__main__":
    unittest.main()
