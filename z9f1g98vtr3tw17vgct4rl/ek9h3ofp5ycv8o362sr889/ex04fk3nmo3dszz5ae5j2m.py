#!/usr/bin/env python3
"""Testes do lab 13 - function-anatomy.

Todas as fixtures sao textos de disassembly sinteticos, inventados aqui.
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
function_anatomy = _loadmod("c50srswv6gq3514hwui0rb.py")

STDCALL_FUNC = """\
sub_401000 proc near
push    ebp
mov     ebp, esp
sub     esp, 18h
mov     eax, [ebp+arg_0]
add     eax, [ebp+arg_4]
mov     [ebp+var_8], eax
mov     ecx, [ebp+var_C]
xor     ecx, ecx
mov     esp, ebp
pop     ebp
retn    8
sub_401000 endp
"""

CDECL_FUNC = """\
00401020 55            push    ebp
00401021 8B EC         mov     ebp, esp
00401023 83 EC 10      sub     esp, 10h
00401026 8B 45 08      mov     eax, [ebp+arg_0]
00401029 89 45 FC      mov     [ebp+var_4], eax
0040102C C9            leave
0040102D C3            retn
"""

NAKED_FUNC = """\
my_func:
xor     eax, eax
inc     eax
"""

CALLER_CLEANS = """\
push    5
call    sub_401000
add     esp, 4
retn
"""


class TestFunctionAnatomy(unittest.TestCase):
    def test_stdcall_full(self):
        r = function_anatomy.analyze(STDCALL_FUNC)
        self.assertTrue(r["prologue"])
        self.assertTrue(r["epilogue"])
        self.assertEqual(r["args"], 2)
        self.assertEqual(r["locals"], 2)
        self.assertEqual(r["convention"], "stdcall")

    def test_cdecl_leave_ret(self):
        r = function_anatomy.analyze(CDECL_FUNC)
        self.assertTrue(r["prologue"])
        self.assertTrue(r["epilogue"])
        self.assertEqual(r["args"], 1)
        self.assertEqual(r["locals"], 1)
        self.assertEqual(r["convention"], "cdecl")

    def test_naked_no_prologue(self):
        r = function_anatomy.analyze(NAKED_FUNC)
        self.assertFalse(r["prologue"])
        self.assertFalse(r["epilogue"])
        self.assertEqual(r["args"], 0)
        self.assertEqual(r["locals"], 0)
        self.assertEqual(r["convention"], "unknown")

    def test_caller_cleans_stack(self):
        r = function_anatomy.analyze(CALLER_CLEANS)
        self.assertFalse(r["prologue"])
        self.assertTrue(r["epilogue"])
        self.assertEqual(r["convention"], "cdecl")

    def test_ret_with_hex_size_is_stdcall(self):
        r = function_anatomy.analyze("push ebp\nmov ebp, esp\nretn 0Ch\n")
        self.assertEqual(r["convention"], "stdcall")

    def test_64bit_prologue(self):
        r = function_anatomy.analyze("push rbp\nmov rbp, rsp\nsub rsp, 20h\nret\n")
        self.assertTrue(r["prologue"])
        self.assertTrue(r["epilogue"])
        self.assertEqual(r["convention"], "cdecl")

    def test_arg_count_dedups_repeats(self):
        r = function_anatomy.analyze("mov eax, [ebp+arg_0]\nmov ebx, [ebp+arg_0]\nretn\n")
        self.assertEqual(r["args"], 1)

    def test_cli_prints_json(self):
        with tempfile.NamedTemporaryFile("w", suffix=".asm", delete=False) as fh:
            fh.write(STDCALL_FUNC)
            path = fh.name
        try:
            out = subprocess.run(
                [sys.executable, "c50srswv6gq3514hwui0rb.py", path],
                capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)),
            )
            self.assertEqual(out.returncode, 0, out.stderr)
            data = json.loads(out.stdout)
            self.assertEqual(data["convention"], "stdcall")
            self.assertTrue(data["prologue"])
            self.assertEqual(data["args"], 2)
            self.assertEqual(data["locals"], 2)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
