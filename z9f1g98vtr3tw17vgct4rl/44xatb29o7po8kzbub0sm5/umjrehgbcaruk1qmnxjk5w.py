#!/usr/bin/env python3
"""Testes do dump_validate com fixtures sinteticas construidas em bytes."""

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
dump_validate = _loadmod("033jydbq9nrdlq8wn8eu9q.py")

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "033jydbq9nrdlq8wn8eu9q.py")


def build_pe(entry_point=0x1000, vaddr=0x1000, vsize=0x100,
             raw_size=0x200, raw_ptr=0x200, mz=b"MZ",
             pe_sig=b"PE\x00\x00"):
    """Constroi um PE32 minimo valido em bytes (1 secao .text)."""
    buf = bytearray(0x400)
    buf[0:2] = mz
    struct.pack_into("<I", buf, 0x3C, 0x80)  # e_lfanew
    buf[0x80:0x84] = pe_sig
    struct.pack_into("<HHIIIHH", buf, 0x84, 0x14C, 1, 0, 0, 0, 0xE0, 0x0102)
    opt = 0x98
    struct.pack_into("<H", buf, opt, 0x10B)
    struct.pack_into("<I", buf, opt + 16, entry_point)
    struct.pack_into("<I", buf, opt + 28, 0x400000)
    struct.pack_into("<I", buf, opt + 32, 0x1000)  # SectionAlignment
    struct.pack_into("<I", buf, opt + 36, 0x200)  # FileAlignment
    sh = opt + 0xE0
    struct.pack_into("<8sIIIIIIHHI", buf, sh, b".text\x00\x00\x00",
                     vsize, vaddr, raw_size, raw_ptr, 0, 0, 0, 0, 0x60000020)
    buf[0x200:0x400] = b"\xcc" * 0x200
    return bytes(buf)


class TestDumpValidate(unittest.TestCase):
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

    def test_pe_integro(self):
        report = dump_validate.validate(self.write(build_pe()))
        self.assertTrue(report["ok"])
        self.assertEqual(report["issues"], [])

    def test_virtual_address_desalinhado(self):
        report = dump_validate.validate(self.write(build_pe(vaddr=0x1001)))
        self.assertFalse(report["ok"])
        self.assertTrue(any("VirtualAddress" in i for i in report["issues"]))

    def test_size_of_raw_data_desalinhado(self):
        report = dump_validate.validate(self.write(build_pe(raw_size=0x201)))
        self.assertFalse(report["ok"])
        self.assertTrue(any("SizeOfRawData" in i for i in report["issues"]))

    def test_entry_point_fora_das_secoes(self):
        report = dump_validate.validate(self.write(build_pe(entry_point=0x9000)))
        self.assertFalse(report["ok"])
        self.assertTrue(any("entry point" in i for i in report["issues"]))

    def test_sem_magic_mz(self):
        report = dump_validate.validate(self.write(build_pe(mz=b"ZZ")))
        self.assertFalse(report["ok"])
        self.assertTrue(any("MZ" in i for i in report["issues"]))

    def test_sem_assinatura_pe(self):
        report = dump_validate.validate(self.write(build_pe(pe_sig=b"XX\x00\x00")))
        self.assertFalse(report["ok"])

    def test_cli_imprime_json(self):
        report = self.run_cli(self.write(build_pe()))
        self.assertEqual(set(report), {"ok", "issues"})
        self.assertTrue(report["ok"])


if __name__ == "__main__":
    unittest.main()
