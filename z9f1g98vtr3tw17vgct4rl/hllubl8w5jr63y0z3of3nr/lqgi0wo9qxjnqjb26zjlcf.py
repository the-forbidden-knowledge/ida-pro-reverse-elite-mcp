#!/usr/bin/env python3
"""Testes do lab 68 -- dpapi-system (fixtures sinteticas)."""
import importlib.util
import os
import unittest

_AQUI = os.path.dirname(os.path.abspath(__file__))


def _load():
    spec = importlib.util.spec_from_file_location(
        "dpapi_system", os.path.join(_AQUI, "g5gwft6bj5qstl8q0g6atg.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


mod = _load()


class TestDpapiSystem(unittest.TestCase):
    def test_deterministic(self):
        a = mod.machine_mk_seed(bytes.fromhex("001122"))
        b = mod.machine_mk_seed(bytes.fromhex("001122"))
        self.assertEqual(a, b)
        self.assertEqual(len(a), 32)

    def test_sensitive(self):
        a = mod.machine_mk_seed(bytes.fromhex("001122"))
        b = mod.machine_mk_seed(bytes.fromhex("001133"))
        self.assertNotEqual(a, b)

    def test_empty_rejected(self):
        with self.assertRaises(ValueError):
            mod.machine_mk_seed(b"")

    def test_iterations(self):
        a = mod.machine_mk_seed(bytes.fromhex("aa"), iterations=5600)
        b = mod.machine_mk_seed(bytes.fromhex("aa"), iterations=1)
        self.assertNotEqual(a, b)


if __name__ == "__main__":
    unittest.main()
