#!/usr/bin/env python3
"""Testes do vmnu7l4sv08o5mr6lmevlp. Fixtures sinteticas geradas no proprio teste."""
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
_mx_rwx_scan = _loadmod("dbj8imukuzce65hmiabxtm.py")
scan, main = _mx_rwx_scan.scan, _mx_rwx_scan.main


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f)


REGIONS = {"regions": [
    {"base": "0x10000", "size": 4096, "protect": "RWX",
     "has_mz": True, "has_code": True},
    {"base": "0x20000", "size": 8192, "protect": "RWX",
     "has_mz": False, "has_code": True},
    {"base": "0x30000", "size": 4096, "protect": "RWX",
     "has_mz": False, "has_code": False},
    {"base": "0x40000", "size": 4096, "protect": "RX",
     "has_mz": False, "has_code": True},
    {"base": "0x50000", "size": 4096, "protect": "RW",
     "has_mz": True, "has_code": False},
]}


class TestRwxScan(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "regions.json")
        write_json(self.path, REGIONS)

    def tearDown(self):
        self.tmp.cleanup()

    def test_finds_suspicious(self):
        result = scan(REGIONS["regions"])
        self.assertEqual(result["count"], 2)
        self.assertEqual(result["total_regions"], 5)
        bases = [s["base"] for s in result["suspicious"]]
        self.assertIn("0x10000", bases)
        self.assertIn("0x20000", bases)

    def test_sorted_by_score(self):
        result = scan(REGIONS["regions"])
        self.assertEqual(result["suspicious"][0]["base"], "0x10000")
        self.assertEqual(result["suspicious"][0]["score"], 7)
        self.assertEqual(result["suspicious"][1]["score"], 5)

    def test_rwx_without_code_ignored(self):
        result = scan(REGIONS["regions"])
        bases = [s["base"] for s in result["suspicious"]]
        self.assertNotIn("0x30000", bases)

    def test_rx_and_rw_ignored(self):
        result = scan(REGIONS["regions"])
        bases = [s["base"] for s in result["suspicious"]]
        self.assertNotIn("0x40000", bases)
        self.assertNotIn("0x50000", bases)

    def test_empty(self):
        result = scan([])
        self.assertEqual(result["count"], 0)
        self.assertEqual(result["suspicious"], [])

    def test_cli(self):
        out = os.path.join(self.tmp.name, "out.json")
        rc = main([self.path, "--output", out])
        self.assertEqual(rc, 0)
        with open(out, encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["count"], 2)


if __name__ == "__main__":
    unittest.main()
