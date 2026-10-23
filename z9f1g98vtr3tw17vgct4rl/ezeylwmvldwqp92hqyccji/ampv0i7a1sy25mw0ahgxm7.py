#!/usr/bin/env python3
"""Testes do lab 83 — dumpdecrypted. Fixtures 100% sintéticas."""

import importlib.util
import os
import struct
import unittest

_AQUI = os.path.dirname(os.path.abspath(__file__))


def _carregar():
    spec = importlib.util.spec_from_file_location(
        "t1oaw20zqx9l04tlqc1fbc", os.path.join(_AQUI, "t1oaw20zqx9l04tlqc1fbc.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = _carregar()

MAGIC = b"\xfe\xed\xfa\xce"


def _blob(cid=1, off=16, size=32):
    return MAGIC + struct.pack("<III", off, size, cid) + bytes([0xAA] * size)


class TestDumpdecrypted(unittest.TestCase):
    def test_despeja_e_zera_cryptid(self):
        r = mod.despejar(_blob())
        self.assertTrue(r["despejado"])
        cid = struct.unpack_from("<I", r["dados"], 12)[0]
        self.assertEqual(cid, 0)
        self.assertEqual(r["regiao"], [16, 32])

    def test_regiao_deterministica(self):
        r1 = mod.despejar(_blob())
        r2 = mod.despejar(_blob())
        self.assertEqual(r1["dados"], r2["dados"])
        self.assertNotIn(b"\xaa" * 8, r1["dados"][16:48])

    def test_ja_descriptografado_passthrough(self):
        blob = _blob(cid=0)
        r = mod.despejar(blob)
        self.assertFalse(r["despejado"])
        self.assertEqual(r["dados"], blob)

    def test_magic_invalido(self):
        with self.assertRaises(ValueError):
            mod.despejar(b"XXXX" + struct.pack("<III", 16, 8, 1) + b"\x00" * 8)

    def test_binario_curto(self):
        with self.assertRaises(ValueError):
            mod.despejar(b"\x00" * 4)

    def test_regiao_fora_do_binario(self):
        blob = MAGIC + struct.pack("<III", 16, 999, 1) + b"\x00" * 16
        with self.assertRaises(ValueError):
            mod.despejar(blob)


if __name__ == "__main__":
    unittest.main()
