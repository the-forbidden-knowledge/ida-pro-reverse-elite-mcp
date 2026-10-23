#!/usr/bin/env python3
"""Testes do r0zx4dq741d2qo17exc2dm. Fixtures sinteticas geradas no proprio teste."""
import json
import os
import struct
import tempfile
import unittest

import importlib.util as _ilu
import os as _os
def _loadmod(_fname):
    _sp = _ilu.spec_from_file_location("_m", _os.path.join(_os.path.dirname(__file__), _fname))
    _mm = _ilu.module_from_spec(_sp)
    _sp.loader.exec_module(_mm)
    return _mm
_mx_stackstring_decode = _loadmod("jsgipjcsv0qjxk2hcjnewc.py")
decode_dwords, main = _mx_stackstring_decode.decode_dwords, _mx_stackstring_decode.main


def pack_str(s):
    """Empacota string ASCII em dwords little-endian (simula stack string)."""
    raw = s.encode("ascii")
    raw += b"\x00" * (-len(raw) % 4)
    return raw


class TestStackStringDecode(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        junk = struct.pack("<II", 0xDEADBEEF, 0x01020304)
        self.data = junk + pack_str("http://x.co") + junk + pack_str("cmd.exe")
        self.path = os.path.join(self.tmp.name, "stack.bin")
        with open(self.path, "wb") as f:
            f.write(self.data)

    def tearDown(self):
        self.tmp.cleanup()

    def test_finds_strings(self):
        found = [s["string"] for s in decode_dwords(self.data)]
        self.assertIn("http://x.co", found)
        self.assertIn("cmd.exe", found)

    def test_offsets_are_correct(self):
        found = {s["string"]: s["offset"] for s in decode_dwords(self.data)}
        self.assertEqual(found["http://x.co"], 8)
        self.assertEqual(found["cmd.exe"], 8 + len(pack_str("http://x.co")) + 8)

    def test_min_len_filters(self):
        found = decode_dwords(self.data, min_len=20)
        self.assertEqual(found, [])

    def test_junk_not_decoded(self):
        found = [s["string"] for s in decode_dwords(self.data)]
        for s in found:
            self.assertTrue(all(32 <= ord(c) < 127 for c in s))

    def test_cli_output_file(self):
        out = os.path.join(self.tmp.name, "out.json")
        rc = main([self.path, "--output", out])
        self.assertEqual(rc, 0)
        with open(out, encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["count"], 2)
        self.assertIn("http://x.co", [s["string"] for s in data["strings"]])


if __name__ == "__main__":
    unittest.main()
