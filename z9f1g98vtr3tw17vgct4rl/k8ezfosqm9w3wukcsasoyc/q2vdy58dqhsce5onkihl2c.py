#!/usr/bin/env python3
"""Testes do aslr_strip com PE sintetico construido em bytes."""

import json
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
    _mm = _ilu.module_from_spec(_sp)
    _sp.loader.exec_module(_mm)
    return _mm
aslr_strip = _loadmod("2uoj8fwax14wq7qft5frg5.py")

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "2uoj8fwax14wq7qft5frg5.py")

DYNAMIC_BASE = 0x0040
NX_COMPAT = 0x0100


def build_pe(dll_chars=0x0000):
    """Constroi um PE32 minimo valido em bytes (1 secao .text)."""
    buf = bytearray(0x400)
    buf[0:2] = b"MZ"
    struct.pack_into("<I", buf, 0x3C, 0x80)  # e_lfanew
    buf[0x80:0x84] = b"PE\x00\x00"
    struct.pack_into("<HHIIIHH", buf, 0x84, 0x14C, 1, 0, 0, 0, 0xE0, 0x0102)
    opt = 0x98
    struct.pack_into("<H", buf, opt, 0x10B)
    struct.pack_into("<I", buf, opt + 16, 0x1000)  # AddressOfEntryPoint
    struct.pack_into("<I", buf, opt + 28, 0x400000)
    struct.pack_into("<I", buf, opt + 32, 0x1000)
    struct.pack_into("<I", buf, opt + 36, 0x200)
    struct.pack_into("<H", buf, opt + 68, dll_chars)  # DllCharacteristics
    sh = opt + 0xE0
    struct.pack_into("<8sIIIIIIHHI", buf, sh, b".text\x00\x00\x00",
                     0x100, 0x1000, 0x200, 0x200, 0, 0, 0, 0, 0x60000020)
    buf[0x200:0x400] = b"\xcc" * 0x200
    return bytes(buf)


class TestAslrStrip(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def write(self, data, name="alvo.exe"):
        path = os.path.join(self.tmp.name, name)
        with open(path, "wb") as handle:
            handle.write(data)
        return path

    def dll_chars_of(self, path):
        return aslr_strip.read_dll_characteristics(path)

    def test_zera_flag_e_cria_backup(self):
        original = build_pe(dll_chars=DYNAMIC_BASE | NX_COMPAT)
        path = self.write(original)
        result = aslr_strip.strip_aslr(path)
        self.assertTrue(result["patched"])
        self.assertEqual(result["backup"], path + ".bak")
        self.assertTrue(os.path.exists(path + ".bak"))
        with open(path + ".bak", "rb") as handle:
            self.assertEqual(handle.read(), original)
        new_flags = self.dll_chars_of(path)
        self.assertEqual(new_flags & DYNAMIC_BASE, 0)
        self.assertNotEqual(new_flags & NX_COMPAT, 0)  # demais flags intactas

    def test_sem_flag_nao_modifica_mas_faz_backup(self):
        original = build_pe(dll_chars=NX_COMPAT)
        path = self.write(original)
        result = aslr_strip.strip_aslr(path)
        self.assertFalse(result["patched"])
        self.assertTrue(os.path.exists(path + ".bak"))
        with open(path, "rb") as handle:
            self.assertEqual(handle.read(), original)

    def test_arquivo_invalido_levanta_erro(self):
        path = self.write(b"nao e um pe")
        with self.assertRaises(ValueError):
            aslr_strip.strip_aslr(path)
        self.assertFalse(os.path.exists(path + ".bak"))

    def test_cli_imprime_json(self):
        path = self.write(build_pe(dll_chars=DYNAMIC_BASE))
        proc = subprocess.run([sys.executable, SCRIPT, path],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        result = json.loads(proc.stdout)
        self.assertEqual(set(result), {"patched", "backup"})
        self.assertTrue(result["patched"])
        self.assertEqual(self.dll_chars_of(path) & DYNAMIC_BASE, 0)


if __name__ == "__main__":
    unittest.main()
