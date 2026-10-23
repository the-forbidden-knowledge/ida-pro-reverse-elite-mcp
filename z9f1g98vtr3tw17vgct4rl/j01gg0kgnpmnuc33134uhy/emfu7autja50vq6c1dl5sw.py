#!/usr/bin/env python3
"""Testes do lab 15 - loop-deconstruct.

Fixtures sinteticas, inventadas neste arquivo.
"""

import json
import os
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
loop_deconstruct = _loadmod("kxva252vefs4lkfh7c072l.py")

BASIC_LOOP = """\
mov     ecx, 0
mov     esi, 0x1000
loc_loop:
mov     eax, [esi+ecx*4]
add     eax, 1
mov     [esi+ecx*4], eax
inc     ecx
cmp     ecx, 10
jl      loc_loop
"""

ADD_UPDATE_LOOP = """\
mov     edx, 0x2000
xor     ebx, ebx
top:
mov     eax, [edx+ebx]
xor     eax, 0x55
mov     [edx+ebx], eax
add     ebx, 4
cmp     ebx, 64
jb      top
"""

NO_LOOP_LABEL = """\
mov     eax, 1
mov     ebx, 2
"""


class TestLoopDeconstruct(unittest.TestCase):
    def test_basic_parts(self):
        r = loop_deconstruct.deconstruct(BASIC_LOOP)
        self.assertIn("mov     ecx, 0", r["init"])
        self.assertIn("cmp", r["condition"])
        self.assertIn("jl", r["condition"])
        self.assertIn("inc", r["update"])
        self.assertIn("ecx", r["update"])
        self.assertEqual(len(r["body"]), 3)
        self.assertTrue(any("add" in b for b in r["body"]))

    def test_add_update(self):
        r = loop_deconstruct.deconstruct(ADD_UPDATE_LOOP)
        self.assertIn("mov     edx, 0x2000", r["init"])
        self.assertNotIn("xor", r["init"])  # init: so linhas MOV
        self.assertIn("add", r["update"])
        self.assertIn("ebx", r["update"])
        self.assertIn("jb", r["condition"])
        self.assertEqual(len(r["body"]), 3)

    def test_no_backward_jump(self):
        r = loop_deconstruct.deconstruct(NO_LOOP_LABEL)
        self.assertEqual(r["condition"], "")
        self.assertEqual(r["update"], "")
        self.assertEqual(r["body"], [])

    def test_body_excludes_condition_and_update(self):
        r = loop_deconstruct.deconstruct(BASIC_LOOP)
        joined = "\n".join(r["body"])
        self.assertNotIn("cmp", joined)
        self.assertNotIn("inc", joined)
        self.assertNotIn("jl", joined)

    def test_cli_prints_json(self):
        with tempfile.NamedTemporaryFile("w", suffix=".asm", delete=False) as fh:
            fh.write(BASIC_LOOP)
            path = fh.name
        try:
            out = subprocess.run(
                [sys.executable, "kxva252vefs4lkfh7c072l.py", path],
                capture_output=True, text=True,
                cwd=os.path.dirname(os.path.abspath(__file__)),
            )
            self.assertEqual(out.returncode, 0, out.stderr)
            data = json.loads(out.stdout)
            self.assertIn("init", data)
            self.assertIn("condition", data)
            self.assertIn("update", data)
            self.assertIn("body", data)
            self.assertIn("ecx", data["update"])
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
