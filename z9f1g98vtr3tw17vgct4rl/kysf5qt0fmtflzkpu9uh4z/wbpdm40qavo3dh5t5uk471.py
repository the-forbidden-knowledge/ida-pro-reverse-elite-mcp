#!/usr/bin/env python3
"""Testes do lab 67 -- ngen-detect (fixtures sinteticas)."""
import importlib.util
import os
import unittest

_AQUI = os.path.dirname(os.path.abspath(__file__))


def _load():
    spec = importlib.util.spec_from_file_location(
        "ngen_detect", os.path.join(_AQUI, "nwutdl4f2o2u34izsa7gg8.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


mod = _load()


class TestNgenDetect(unittest.TestCase):
    def test_ni_is_native(self):
        self.assertEqual(mod.classify("System.Management.Automation.ni.dll"),
                         "native (NGEN)")

    def test_plain_dll_is_il(self):
        self.assertEqual(mod.classify("MinhaLib.dll"), "IL (bytecode)")

    def test_case_insensitive(self):
        self.assertEqual(mod.classify("X.NI.DLL"), "native (NGEN)")

    def test_engine_variants(self):
        mods = ["C:\\a\\System.Management.Automation.ni.dll",
                "C:\\b\\System.Management.Automation.dll",
                "C:\\c\\outra.dll"]
        v = mod.engine_variants(mods)
        self.assertEqual(len(v["native"]), 1)
        self.assertEqual(len(v["il"]), 1)

    def test_scan(self):
        r = mod.scan(["a.ni.dll", "b.dll"])
        self.assertEqual([x["kind"] for x in r],
                         ["native (NGEN)", "IL (bytecode)"])


if __name__ == "__main__":
    unittest.main()
