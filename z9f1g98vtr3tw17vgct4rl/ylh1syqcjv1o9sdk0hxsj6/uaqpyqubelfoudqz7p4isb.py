#!/usr/bin/env python3
"""Testes do ylh1syqcjv1o9sdk0hxsj6. Fixtures sinteticas geradas no proprio teste."""
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
_mx_deobf_report = _loadmod("wq48w8utqpp3d0w2bmobyi.py")
build_report, main = _mx_deobf_report.build_report, _mx_deobf_report.main


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f)


class TestDeobfReport(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        # fixture: texto com XOR 1 byte + stack string em dwords
        plain = b"the hidden config value is 12345. " * 6
        self.cipher = bytes(b ^ 0x5A for b in plain)
        raw = b"http" + b"\x00" * 0 + b"://x." + b"co\x00\x00"
        data = self.cipher + b"\x00" * 8 + raw
        self.bin = os.path.join(self.tmp.name, "mix.bin")
        with open(self.bin, "wb") as f:
            f.write(data)
        self.dsl = os.path.join(self.tmp.name, "dsl.json")
        write_json(self.dsl, {"ops": [
            {"op": "xor", "key": 0x5A, "start": 0, "length": len(self.cipher)},
        ]})

    def tearDown(self):
        self.tmp.cleanup()

    def test_report_structure(self):
        report = build_report(self.bin, workdir=self.tmp.name)
        self.assertIn("xorsearch", report)
        self.assertIn("stackstrings", report)
        self.assertIsNone(report["xor_key"])
        self.assertIsNone(report["emulated"])
        self.assertEqual(len(report["sha256"]), 64)

    def test_xorsearch_finds_key(self):
        report = build_report(self.bin, workdir=self.tmp.name)
        self.assertEqual(report["xorsearch"]["best_key"], 0x5A)

    def test_stackstrings_found(self):
        report = build_report(self.bin, workdir=self.tmp.name)
        strings = [s["string"] for s in report["stackstrings"]["strings"]]
        self.assertIn("http://x.co", strings)

    def test_with_plaintext_and_dsl(self):
        report = build_report(self.bin, plaintext="the hid",
                              dsl=self.dsl, workdir=self.tmp.name)
        self.assertIsNotNone(report["xor_key"])
        self.assertEqual(report["xor_key"]["key_hex"], "5a")
        self.assertIsNotNone(report["emulated"]["sha256"])

    def test_cli_output_file(self):
        out = os.path.join(self.tmp.name, "report.json")
        rc = main([self.bin, "--output", out])
        self.assertEqual(rc, 0)
        with open(out, encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["xorsearch"]["best_key"], 0x5A)


if __name__ == "__main__":
    unittest.main()
