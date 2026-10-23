#!/usr/bin/env python3
"""Testes do qospd4bifqjqxx3j6zos0g. Fixtures sinteticas geradas no proprio teste."""
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
_mx_prologue_scan = _loadmod("it4mcsmqidin2ywfrxqyjy.py")
classify_prologue, scan, main = _mx_prologue_scan.classify_prologue, _mx_prologue_scan.scan, _mx_prologue_scan.main


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f)


FUNCS = {"functions": [
    {"name": "CreateFileW", "addr": "0x7ff10000", "bytes": "e9aabbccdd90"},
    {"name": "ReadFile", "addr": "0x7ff10010", "bytes": "eb1090909090"},
    {"name": "WriteFile", "addr": "0x7ff10020",
     "bytes": "6820400071c3"},
    {"name": "CloseHandle", "addr": "0x7ff10030",
     "bytes": "ff251020400090"},
    {"name": "NormalFunc", "addr": "0x401000",
     "bytes": "558bec83ec209090"},  # push ebp; mov ebp,esp
]}


class TestPrologueScan(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "funcs.json")
        write_json(self.path, FUNCS)

    def tearDown(self):
        self.tmp.cleanup()

    def test_detects_all_patches(self):
        result = scan(FUNCS["functions"])
        self.assertEqual(result["hooked_count"], 4)
        self.assertEqual(result["clean_count"], 1)
        patches = {h["name"]: h["patch"] for h in result["hooked"]}
        self.assertEqual(patches["CreateFileW"], "jmp rel32")
        self.assertEqual(patches["ReadFile"], "jmp rel8")
        self.assertEqual(patches["WriteFile"], "push imm32 (push/ret)")
        self.assertEqual(patches["CloseHandle"], "jmp [mem] indireto")

    def test_classify_each(self):
        self.assertEqual(classify_prologue(bytes.fromhex("e900000000")),
                         "jmp rel32")
        self.assertEqual(classify_prologue(bytes.fromhex("eb10")), "jmp rel8")
        self.assertEqual(classify_prologue(bytes.fromhex("6812345678")),
                         "push imm32 (push/ret)")
        self.assertEqual(classify_prologue(bytes.fromhex("ff2510204000")),
                         "jmp [mem] indireto")
        self.assertIsNone(classify_prologue(bytes.fromhex("558bec")))
        self.assertIsNone(classify_prologue(b""))

    def test_invalid_hex_counts_clean(self):
        result = scan([{"name": "X", "addr": "0x0", "bytes": "zz"}])
        self.assertEqual(result["clean_count"], 1)
        self.assertEqual(result["hooked_count"], 0)

    def test_cli(self):
        out = os.path.join(self.tmp.name, "out.json")
        rc = main([self.path, "--output", out])
        self.assertEqual(rc, 0)
        with open(out, encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["hooked_count"], 4)


if __name__ == "__main__":
    unittest.main()
