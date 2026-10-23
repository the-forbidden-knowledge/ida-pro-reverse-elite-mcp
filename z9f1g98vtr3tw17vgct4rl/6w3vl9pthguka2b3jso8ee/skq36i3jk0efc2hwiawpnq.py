#!/usr/bin/env python3
"""Testes sinteticos para 146lsaj5ewqgp6lx1w3obn.py (disassembly inventado, sem binarios reais)."""

import json
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
x64_adapt = _loadmod("146lsaj5ewqgp6lx1w3obn.py")

X64_OK = """
0x401000: mov rcx, 0x1
0x401007: mov rdx, rbx
0x40100a: mov r8, 0x0
0x401010: call 0x402000
"""

X64_RIP = """
0x401000: lea rax, [rip+0x2000]
0x401007: sub rsp, 0x20
0x40100b: mov rcx, rax
0x40100e: call 0x402000
"""

X64_BAD_ORDER = """
0x401000: mov r8, 0x1
0x401007: mov rcx, 0x2
0x40100e: call 0x402000
"""

X86_PUSH = """
0x401000: push 0x1
0x401002: push 0x2
0x401004: call 0x402000
"""


class TestX64Adapt(unittest.TestCase):
    def test_convencao_ok(self):
        out = x64_adapt.analyze(X64_OK)
        self.assertTrue(out["args_ok"])
        self.assertEqual(out["rip_relative"], [])

    def test_rip_relativo(self):
        out = x64_adapt.analyze(X64_RIP)
        self.assertEqual(out["rip_relative"], ["0x401000"])
        self.assertTrue(out["args_ok"])
        self.assertTrue(any("shadow space" in n for n in out["notes"]))

    def test_ordem_errada(self):
        out = x64_adapt.analyze(X64_BAD_ORDER)
        self.assertFalse(out["args_ok"])
        self.assertTrue(any("fora da convencao" in n for n in out["notes"]))

    def test_push_estilo_x86(self):
        out = x64_adapt.analyze(X86_PUSH)
        self.assertFalse(out["args_ok"])
        self.assertTrue(any("estilo x86" in n for n in out["notes"]))

    def test_sem_call(self):
        out = x64_adapt.analyze("0x401000: mov rcx, 0x1")
        self.assertTrue(out["args_ok"])
        self.assertTrue(any("nenhuma instrucao call" in n
                            for n in out["notes"]))

    def test_cli_end_to_end(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt",
                                         delete=False) as fh:
            fh.write(X64_RIP)
            path = fh.name
        proc = subprocess.run([sys.executable, "146lsaj5ewqgp6lx1w3obn.py", path],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        out = json.loads(proc.stdout)
        self.assertEqual(set(out.keys()), {"args_ok", "rip_relative", "notes"})
        self.assertTrue(out["args_ok"])
        self.assertEqual(out["rip_relative"], ["0x401000"])


if __name__ == "__main__":
    unittest.main()
