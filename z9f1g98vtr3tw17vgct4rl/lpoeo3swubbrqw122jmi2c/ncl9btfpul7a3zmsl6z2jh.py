#!/usr/bin/env python3
"""Testes do lpoeo3swubbrqw122jmi2c. Fixtures sinteticas geradas no proprio teste."""
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
_mx_hook_trampoline = _loadmod("ijkmsk91ju98zx9czr5t6e.py")
detect, main = _mx_hook_trampoline.detect, _mx_hook_trampoline.main


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f)


FULL = {
    "imports": {
        "kernel32.dll": ["ReadProcessMemory", "VirtualProtect",
                         "WriteProcessMemory", "FlushInstructionCache"],
    },
    "calls": [
        ["patch_fn", "ReadProcessMemory"],
        ["patch_fn", "VirtualProtect"],
        ["patch_fn", "WriteProcessMemory"],
    ],
}


class TestHookTrampoline(unittest.TestCase):
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

    def test_missing_virtualprotect(self):
        data = {"imports": {"kernel32.dll": ["ReadProcessMemory",
                                             "WriteProcessMemory"]}}
        result = detect(data)
        self.assertFalse(result["detected"])
        self.assertIn("virtualprotect", result["missing"])

    def test_out_of_order(self):
        data = dict(FULL)
        data["calls"] = [["patch_fn", "WriteProcessMemory"],
                         ["patch_fn", "VirtualProtect"],
                         ["patch_fn", "ReadProcessMemory"]]
        result = detect(data)
        self.assertFalse(result["in_order"])
        self.assertFalse(result["detected"])

    def test_no_calls_section(self):
        data = {"imports": FULL["imports"]}
        result = detect(data)
        self.assertTrue(result["detected"])
        self.assertIsNone(result["in_order"])

    def test_cli(self):
        out = os.path.join(self.tmp.name, "out.json")
        rc = main([self.path, "--output", out])
        self.assertEqual(rc, 0)
        with open(out, encoding="utf-8") as f:
            data = json.load(f)
        self.assertTrue(data["detected"])


if __name__ == "__main__":
    unittest.main()
