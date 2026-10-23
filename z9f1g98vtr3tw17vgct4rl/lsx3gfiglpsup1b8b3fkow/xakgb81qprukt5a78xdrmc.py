#!/usr/bin/env python3
"""Testes do oep_hunt com fixtures sinteticas construidas em bytes."""

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
oep_hunt = _loadmod("h38d8gegsebkljy66flja7.py")

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "h38d8gegsebkljy66flja7.py")


def build_pe(entry_point=0x1000, section_chars=0x60000020,
             dll_chars=0x0000, import_rva=0, import_size=0,
             vaddr=0x1000, vsize=0x100, raw_size=0x200, raw_ptr=0x200,
             mz=b"MZ", pe_sig=b"PE\x00\x00"):
    """Constroi um PE32 minimo valido em bytes (1 secao .text)."""
    buf = bytearray(0x400)
    buf[0:2] = mz
    struct.pack_into("<I", buf, 0x3C, 0x80)  # e_lfanew
    buf[0x80:0x84] = pe_sig
    # COFF: Machine, NumberOfSections, ..., SizeOfOptionalHeader, Characteristics
    struct.pack_into("<HHIIIHH", buf, 0x84, 0x14C, 1, 0, 0, 0, 0xE0, 0x0102)
    opt = 0x98
    struct.pack_into("<H", buf, opt, 0x10B)  # Magic PE32
    struct.pack_into("<I", buf, opt + 16, entry_point)  # AddressOfEntryPoint
    struct.pack_into("<I", buf, opt + 28, 0x400000)  # ImageBase
    struct.pack_into("<I", buf, opt + 32, 0x1000)  # SectionAlignment
    struct.pack_into("<I", buf, opt + 36, 0x200)  # FileAlignment
    struct.pack_into("<H", buf, opt + 68, dll_chars)  # DllCharacteristics
    struct.pack_into("<I", buf, opt + 90, 16)  # NumberOfRvaAndSizes
    struct.pack_into("<II", buf, opt + 104, import_rva, import_size)  # imports (indice 1)
    sh = opt + 0xE0
    struct.pack_into("<8sIIIIIIHHI", buf, sh, b".text\x00\x00\x00",
                     vsize, vaddr, raw_size, raw_ptr, 0, 0, 0, 0, section_chars)
    buf[0x200:0x400] = b"\xcc" * 0x200  # dados crus da secao
    return bytes(buf)


class TestOepHunt(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def write(self, data, name="dump.bin"):
        path = os.path.join(self.tmp.name, name)
        with open(path, "wb") as handle:
            handle.write(data)
        return path

    def run_cli(self, path):
        proc = subprocess.run([sys.executable, SCRIPT, path],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout)

    def test_pe_valido_ep_executavel_imports_ok(self):
        data = build_pe(entry_point=0x1000, import_rva=0x200, import_size=0x40)
        report = oep_hunt.analyze(self.write(data))
        self.assertTrue(report["valid_pe"])
        self.assertTrue(report["ep_in_exec_section"])
        self.assertTrue(report["imports_readable"])
        self.assertEqual(len(report["checks"]), 4)
        self.assertTrue(all(c["ok"] for c in report["checks"]))

    def test_ep_fora_das_secoes(self):
        data = build_pe(entry_point=0x9000)
        report = oep_hunt.analyze(self.write(data))
        self.assertTrue(report["valid_pe"])
        self.assertFalse(report["ep_in_exec_section"])

    def test_ep_em_secao_sem_execucao(self):
        data = build_pe(entry_point=0x1000, section_chars=0x40000040)
        report = oep_hunt.analyze(self.write(data))
        self.assertTrue(report["valid_pe"])
        self.assertFalse(report["ep_in_exec_section"])

    def test_sem_magic_mz(self):
        data = build_pe(mz=b"ZZ")
        report = oep_hunt.analyze(self.write(data))
        self.assertFalse(report["valid_pe"])
        self.assertFalse(report["ep_in_exec_section"])
        self.assertFalse(report["imports_readable"])

    def test_sem_assinatura_pe(self):
        data = build_pe(pe_sig=b"XX\x00\x00")
        report = oep_hunt.analyze(self.write(data))
        self.assertFalse(report["valid_pe"])

    def test_imports_fora_do_arquivo(self):
        data = build_pe(import_rva=0xFFFFF, import_size=0x100)
        report = oep_hunt.analyze(self.write(data))
        self.assertTrue(report["valid_pe"])
        self.assertFalse(report["imports_readable"])

    def test_cli_imprime_json(self):
        data = build_pe(entry_point=0x1000, import_rva=0x200, import_size=0x40)
        report = self.run_cli(self.write(data))
        self.assertEqual(set(report),
                         {"valid_pe", "ep_in_exec_section",
                          "imports_readable", "checks"})
        self.assertTrue(report["valid_pe"])


if __name__ == "__main__":
    unittest.main()
