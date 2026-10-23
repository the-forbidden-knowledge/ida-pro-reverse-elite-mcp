#!/usr/bin/env python3
"""Testes do lab 59 -- dpapi-derive (fixtures sinteticas)."""
import hashlib
import importlib.util
import os
import unittest

_AQUI = os.path.dirname(os.path.abspath(__file__))


def _load():
    spec = importlib.util.spec_from_file_location(
        "dpapi_derive", os.path.join(_AQUI, "jzffxsk1ap4gm1yd3mp25y.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


mod = _load()


class TestDpapiDerive(unittest.TestCase):
    def test_mkp_deterministic(self):
        a = mod.derive_mkp(b"senha", b"salt123456789012", 5600)
        b = mod.derive_mkp(b"senha", b"salt123456789012", 5600)
        self.assertEqual(a, b)
        self.assertEqual(len(a), 32)

    def test_mkp_sensitive(self):
        a = mod.derive_mkp(b"senha1", b"salt123456789012", 5600)
        b = mod.derive_mkp(b"senha2", b"salt123456789012", 5600)
        self.assertNotEqual(a, b)

    def test_iterations_honored(self):
        a = mod.derive_mkp(b"senha", b"salt123456789012", 5600)
        b = mod.derive_mkp(b"senha", b"salt123456789012", 1)
        self.assertNotEqual(a, b)

    def test_iterations_invalid(self):
        with self.assertRaises(ValueError):
            mod.derive_mkp(b"senha", b"salt", 0)

    def test_roundtrip(self):
        mkpk = mod.derive_mkp(b"correta", b"salt123456789012", 5600)
        mk = hashlib.sha256(b"mk-real").digest() * 2
        mk = mk[:64]
        f = mod.seal_master_key(mk, mkpk, "guid-1", b"salt123456789012", 5600)
        self.assertEqual(mod.open_master_key(f, mkpk), mk)

    def test_wrong_passphrase(self):
        boa = mod.derive_mkp(b"correta", b"salt123456789012", 5600)
        ruim = mod.derive_mkp(b"errada", b"salt123456789012", 5600)
        mk = b"\x01" * 64
        f = mod.seal_master_key(mk, boa, "guid-1", b"salt123456789012", 5600)
        with self.assertRaises(ValueError):
            mod.open_master_key(f, ruim)

    def test_tampered_blob(self):
        mkpk = mod.derive_mkp(b"correta", b"salt123456789012", 5600)
        f = mod.seal_master_key(b"\x02" * 64, mkpk, "guid-1",
                                b"salt123456789012", 5600)
        f["blob"] = "ff" + f["blob"][2:]
        with self.assertRaises(ValueError):
            mod.open_master_key(f, mkpk)

    def test_session_key(self):
        s1 = mod.derive_session_key(b"\x03" * 64)
        s2 = mod.derive_session_key(b"\x03" * 64, b"outro-contexto")
        self.assertEqual(len(s1), 32)
        self.assertNotEqual(s1, s2)


if __name__ == "__main__":
    unittest.main()
