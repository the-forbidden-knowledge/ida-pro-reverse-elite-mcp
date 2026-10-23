#!/usr/bin/env python3
"""Testes do lab 14 - control-flow.

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
control_flow = _loadmod("mptrosthdlemn4edpmu7us.py")

IF_SNIPPET = """\
0x401000: mov eax, [ebp+8]
0x401004: cmp eax, 5
0x401007: jle 0x401020
0x40100c: mov ebx, 1
0x401020: ret
"""

LOOP_SNIPPET = """\
0x402000: mov ecx, 0
0x402004: add eax, ecx
0x402007: inc ecx
0x402008: cmp ecx, 10
0x40200c: jl 0x402004
0x402010: ret
"""

SWITCH_SNIPPET = """\
0x403000: mov eax, [ebp+8]
0x403004: cmp eax, 3
0x403007: ja 0x403030
0x40300c: jmp dword ptr [eax*4+0x404000]
0x403030: ret
"""

JMP_BACKWARD = """\
0x405000: nop
0x405001: jmp 0x405000
"""


class TestControlFlow(unittest.TestCase):
    def test_if_detected(self):
        pats = control_flow.detect(control_flow.parse_lines(IF_SNIPPET))
        ifs = [p for p in pats if p["type"] == "if"]
        self.assertEqual(len(ifs), 1)
        self.assertEqual(ifs[0]["addr"], "0x401007")
        self.assertIn("cmp", ifs[0]["detail"])
        self.assertIn("jle", ifs[0]["detail"])

    def test_loop_detected(self):
        pats = control_flow.detect(control_flow.parse_lines(LOOP_SNIPPET))
        loops = [p for p in pats if p["type"] == "loop"]
        self.assertEqual(len(loops), 1)
        self.assertEqual(loops[0]["addr"], "0x40200c")

    def test_switch_detected(self):
        pats = control_flow.detect(control_flow.parse_lines(SWITCH_SNIPPET))
        switches = [p for p in pats if p["type"] == "switch"]
        self.assertEqual(len(switches), 1)
        self.assertEqual(switches[0]["addr"], "0x40300c")
        self.assertIn("eax*4", switches[0]["detail"].replace(" ", ""))

    def test_forward_jump_is_not_loop(self):
        pats = control_flow.detect(control_flow.parse_lines(IF_SNIPPET))
        loops = [p for p in pats if p["type"] == "loop"]
        self.assertEqual(loops, [])

    def test_unconditional_backward_jump_is_loop(self):
        pats = control_flow.detect(control_flow.parse_lines(JMP_BACKWARD))
        loops = [p for p in pats if p["type"] == "loop"]
        self.assertEqual(len(loops), 1)
        self.assertEqual(loops[0]["addr"], "0x405001")

    def test_test_followed_by_jcc_is_if(self):
        src = "0x500000: test eax, eax\n0x500002: jz 0x500010\n"
        pats = control_flow.detect(control_flow.parse_lines(src))
        self.assertEqual(len([p for p in pats if p["type"] == "if"]), 1)

    def test_qword_table_is_switch(self):
        src = "0x600000: jmp qword ptr [rax*8+0x700000]\n"
        pats = control_flow.detect(control_flow.parse_lines(src))
        self.assertEqual([p["type"] for p in pats], ["switch"])

    def test_cli_prints_json(self):
        with tempfile.NamedTemporaryFile("w", suffix=".asm", delete=False) as fh:
            fh.write(LOOP_SNIPPET)
            path = fh.name
        try:
            out = subprocess.run(
                [sys.executable, "mptrosthdlemn4edpmu7us.py", path],
                capture_output=True, text=True,
                cwd=os.path.dirname(os.path.abspath(__file__)),
            )
            self.assertEqual(out.returncode, 0, out.stderr)
            data = json.loads(out.stdout)
            types = [p["type"] for p in data["patterns"]]
            self.assertIn("loop", types)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
