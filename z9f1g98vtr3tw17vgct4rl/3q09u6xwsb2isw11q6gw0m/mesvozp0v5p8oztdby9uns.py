#!/usr/bin/env python3
"""Testes do lab 16 - jumptable-resolve.

Fixtures sinteticas: hex dumps inventados neste arquivo.
"""

import json
import os
import struct
import subprocess
import sys
import tempfile
import unittest

import importlib.util as _ilu
import os as _os
def _loadmod(_fname):
    _sp = _ilu.spec_from_file_location("_m", _os.path.join(_os.path.dirname(__file__), _fname))
    _mm = _ilu.module_from_spec(_sp)
    _sp.loader.exec_module(_mm)
    return _mm
jumptable_resolve = _loadmod("et7kucclfz81q4w51d8rcs.py")

BASE = 0x401000
RVAS_32 = [0x100, 0x150, 0x1A0, 0x200]
RVAS_64 = [0x1000, 0x2000]


def dump32():
    return " ".join(f"{b:02x}" for rva in RVAS_32
                    for b in struct.pack("<I", rva))


def dump64_multiline():
    lines = []
    for i, rva in enumerate(RVAS_64):
        raw = struct.pack("<Q", rva)
        hexbytes = " ".join(f"{b:02x}" for b in raw)
        ascii_col = "".join(chr(b) if 32 <= b < 127 else "." for b in raw)
        lines.append(f"{i*16:08x}: {hexbytes}  |{ascii_col}|")
    return "\n".join(lines) + "\n"


class TestJumptableResolve(unittest.TestCase):
    def _run_cli(self, content, *extra):
        with tempfile.NamedTemporaryFile("w", suffix=".hex", delete=False) as fh:
            fh.write(content)
            path = fh.name
        try:
            out = subprocess.run(
                [sys.executable, "et7kucclfz81q4w51d8rcs.py", path, *extra],
                capture_output=True, text=True,
                cwd=os.path.dirname(os.path.abspath(__file__)),
            )
            return out
        finally:
            os.unlink(path)

    def test_resolve_32bit(self):
        cases = jumptable_resolve.resolve(
            jumptable_resolve.parse_hex_dump(dump32()), BASE, 4, 4)
        self.assertEqual(len(cases), 4)
        for i, rva in enumerate(RVAS_32):
            self.assertEqual(cases[i]["index"], i)
            self.assertEqual(cases[i]["target"], hex(BASE + rva))

    def test_resolve_64bit_xxd_style(self):
        data = jumptable_resolve.parse_hex_dump(dump64_multiline())
        cases = jumptable_resolve.resolve(data, BASE, 2, 8)
        self.assertEqual(cases[0]["target"], hex(BASE + RVAS_64[0]))
        self.assertEqual(cases[1]["target"], hex(BASE + RVAS_64[1]))

    def test_continuous_hex_string(self):
        raw = b"".join(struct.pack("<I", r) for r in RVAS_32)
        cases = jumptable_resolve.resolve(
            jumptable_resolve.parse_hex_dump(raw.hex()), BASE, 4, 4)
        self.assertEqual(cases[2]["target"], hex(BASE + RVAS_32[2]))

    def test_insufficient_bytes_raises(self):
        with self.assertRaises(ValueError):
            jumptable_resolve.resolve(b"\x01\x02", BASE, 4, 4)

    def test_odd_nibble_raises(self):
        with self.assertRaises(ValueError):
            jumptable_resolve.parse_hex_dump("0f 1")

    def test_cli_json(self):
        out = self._run_cli(dump32(), "--base", "0x401000",
                            "--count", "4", "--ptrsize", "4")
        self.assertEqual(out.returncode, 0, out.stderr)
        data = json.loads(out.stdout)
        self.assertEqual(len(data["cases"]), 4)
        self.assertEqual(data["cases"][0]["target"], hex(BASE + RVAS_32[0]))
        self.assertEqual(data["cases"][3]["index"], 3)

    def test_cli_base_without_0x(self):
        out = self._run_cli(dump32(), "--base", "401000",
                            "--count", "4")
        self.assertEqual(out.returncode, 0, out.stderr)
        data = json.loads(out.stdout)
        self.assertEqual(data["cases"][1]["target"], hex(BASE + RVAS_32[1]))

    def test_cli_short_table_fails(self):
        out = self._run_cli("aa bb", "--base", "0x401000",
                            "--count", "4")
        self.assertNotEqual(out.returncode, 0)


if __name__ == "__main__":
    unittest.main()
