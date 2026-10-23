"""Testes do ugqtqasgy279l2p5axv4is (PE sintetico gerado no teste)."""

import importlib.util
import json
import os
import struct
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def load_module():
    spec = importlib.util.spec_from_file_location(
        "tls_parse", os.path.join(HERE, "nd23wixgi0e1j565ctf8po.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = load_module()

IMAGE_BASE = 0x400000


def build_pe(com_tls=True):
    """Monta um PE32 minimo com (ou sem) TLS Directory."""
    buf = bytearray(0x800)
    buf[0:2] = b"MZ"
    struct.pack_into("<I", buf, 0x3C, 0x80)          # e_lfanew
    buf[0x80:0x84] = b"PE\x00\x00"
    # COFF
    struct.pack_into("<HHIIIHH", buf, 0x84,
                     0x14C, 1, 0, 0, 0, 0xE0, 0x010F)
    # Optional32
    opt = 0x98
    struct.pack_into("<H", buf, opt, 0x10B)          # magic
    struct.pack_into("<I", buf, opt + 28, IMAGE_BASE)
    struct.pack_into("<I", buf, opt + 92, 16)       # NumberOfRvaAndSizes
    if com_tls:
        struct.pack_into("<II", buf, opt + 96 + 8 * 9, 0x3000, 0x18)
    # secao .tls
    sec = opt + 0xE0
    struct.pack_into("<8sIIII", buf, sec,
                     b".tls\x00\x00\x00\x00", 0x200, 0x3000, 0x200, 0x400)
    if com_tls:
        # TLS directory em file offset 0x400 (RVA 0x3000)
        struct.pack_into("<IIIIII", buf, 0x400,
                         0x403000, 0x403100, 0x403010, 0x403100, 0, 0)
        # array de callbacks em file offset 0x500 (RVA 0x3100)
        struct.pack_into("<III", buf, 0x500, 0x404000, 0x405000, 0)
    return bytes(buf)


class TestParseTls(unittest.TestCase):
    def test_com_tls(self):
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "a.exe")
            with open(p, "wb") as f:
                f.write(build_pe(True))
            rel = mod.parse_tls(p)
        self.assertTrue(rel["tls_presente"])
        self.assertEqual(rel["bits"], 32)
        self.assertEqual(rel["total_callbacks"], 2)
        vas = [c["va"] for c in rel["callbacks"]]
        self.assertIn("0x404000", vas)
        self.assertIn("0x405000", vas)
        rvas = [c["rva"] for c in rel["callbacks"]]
        self.assertIn("0x4000", rvas)
        self.assertEqual(rel["diretorio"]["address_of_callbacks"], "0x403100")

    def test_sem_tls(self):
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "b.exe")
            with open(p, "wb") as f:
                f.write(build_pe(False))
            rel = mod.parse_tls(p)
        self.assertFalse(rel["tls_presente"])
        self.assertEqual(rel["total_callbacks"], 0)
        self.assertEqual(rel["callbacks"], [])

    def test_nao_pe(self):
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "x.bin")
            with open(p, "wb") as f:
                f.write(b"ZZ" + b"\x00" * 100)
            with self.assertRaises(ValueError):
                mod.parse_tls(p)


class TestCli(unittest.TestCase):
    def test_cli_stdout(self):
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "a.exe")
            with open(p, "wb") as f:
                f.write(build_pe(True))
            r = subprocess.run(
                [sys.executable, os.path.join(HERE, "nd23wixgi0e1j565ctf8po.py"),
                 "--input", p],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            rel = json.loads(r.stdout)
            self.assertTrue(rel["tls_presente"])

    def test_cli_arquivo_invalido(self):
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "x.bin")
            with open(p, "wb") as f:
                f.write(b"nada aqui")
            r = subprocess.run(
                [sys.executable, os.path.join(HERE, "nd23wixgi0e1j565ctf8po.py"),
                 "--input", p],
                capture_output=True, text=True)
            self.assertNotEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
