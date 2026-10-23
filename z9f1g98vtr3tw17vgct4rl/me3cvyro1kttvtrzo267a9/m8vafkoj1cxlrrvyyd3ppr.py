#!/usr/bin/env python3
"""Testes do me3cvyro1kttvtrzo267a9. Fixtures sinteticas geradas no proprio teste."""
import json
import os
import tempfile
import unittest

import importlib.util as _ilu
import os as _os
def _loadmod(_fname):
    _sp = _ilu.spec_from_file_location("_m", _os.path.join(_os.path.dirname(__file__), _fname))
    _mm = _ilu.module_from_spec(_sp)
    _sp.loader.exec_module(_mm)
    return _mm
_mx_injection_chain = _loadmod("uwk6wdc1p13aqg89iw400l.py")
clean, detect, main = _mx_injection_chain.clean, _mx_injection_chain.detect, _mx_injection_chain.main


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f)


FULL = {
    "imports": {
        "kernel32.dll": ["OpenProcess", "VirtualAllocEx", "WriteProcessMemory",
                         "CreateRemoteThread", "CloseHandle"],
    },
    "calls": [
        ["main", "OpenProcess"],
        ["main", "VirtualAllocEx"],
        ["main", "WriteProcessMemory"],
        ["main", "CreateRemoteThread"],
    ],
}


class TestInjectionChain(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "trace.json")
        write_json(self.path, FULL)

    def tearDown(self):
        self.tmp.cleanup()

    def test_full_chain_detected(self):
        result = detect(FULL)
        self.assertTrue(result["detected"])
        self.assertEqual(result["missing"], [])
        self.assertTrue(result["in_order"])

    def test_missing_api(self):
        data = {"imports": {"kernel32.dll": ["OpenProcess", "WriteProcessMemory"]},
                "calls": []}
        result = detect(data)
        self.assertFalse(result["detected"])
        self.assertIn("virtualalloc", result["missing"])
        self.assertIn("createremotethread", result["missing"])

    def test_out_of_order(self):
        data = dict(FULL)
        data["calls"] = [["main", "CreateRemoteThread"],
                         ["main", "WriteProcessMemory"],
                         ["main", "VirtualAllocEx"],
                         ["main", "OpenProcess"]]
        result = detect(data)
        self.assertFalse(result["in_order"])
        self.assertFalse(result["detected"])

    def test_suffix_variants(self):
        data = {"imports": {"kernel32.dll": ["OpenProcess",
                         "VirtualAllocEx", "WriteProcessMemory",
                         "CreateRemoteThreadEx"]}}
        result = detect(data)
        self.assertTrue(result["detected"])
        self.assertIsNone(result["in_order"])

    def test_clean(self):
        self.assertEqual(clean("CreateRemoteThreadEx"), "createremotethread")
        self.assertEqual(clean("WriteProcessMemory"), "writeprocessmemory")
        self.assertEqual(clean("MessageBoxW"), "messagebox")

    def test_cli(self):
        out = os.path.join(self.tmp.name, "out.json")
        rc = main([self.path, "--output", out])
        self.assertEqual(rc, 0)
        with open(out, encoding="utf-8") as f:
            data = json.load(f)
        self.assertTrue(data["detected"])


if __name__ == "__main__":
    unittest.main()
