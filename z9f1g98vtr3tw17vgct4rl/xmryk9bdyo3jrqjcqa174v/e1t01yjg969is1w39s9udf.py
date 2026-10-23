#!/usr/bin/env python3
"""Testes do iat_rebuild: agrupamento por DLL e geracao do IDC."""

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
iat_rebuild = _loadmod("uie1lpxr4wfkdchmwuffa3.py")

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "uie1lpxr4wfkdchmwuffa3.py")

HINTS = {
    "0x401000": "kernel32.CreateFileA",
    "0x401004": "kernel32.ReadFile",
    "0x402000": "user32.MessageBoxA",
}


class TestIatRebuild(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def write_hints(self, hints):
        path = os.path.join(self.tmp.name, "hints.json")
        with open(path, "w", encoding="utf-8") as handle:
            json.dump({"hints": hints}, handle)
        return path

    def run_cli(self, path, *extra):
        proc = subprocess.run([sys.executable, SCRIPT, path, *extra],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return proc.stdout

    def test_agrupa_por_dll(self):
        rebuilt = iat_rebuild.rebuild(HINTS)
        self.assertEqual(set(rebuilt["imports"]), {"kernel32", "user32"})
        k32 = rebuilt["imports"]["kernel32"]
        self.assertEqual(len(k32), 2)
        self.assertEqual([e["addr"] for e in k32], ["0x401000", "0x401004"])
        self.assertEqual(k32[0]["name"], "CreateFileA")
        self.assertEqual(rebuilt["imports"]["user32"][0]["name"], "MessageBoxA")

    def test_chave_decimal_e_case_insensitive(self):
        hints = {"4198400": "KERNEL32.CreateFileA", "0x401004": "kernel32.ReadFile"}
        rebuilt = iat_rebuild.rebuild(hints)
        self.assertEqual(set(rebuilt["imports"]), {"kernel32"})
        self.assertEqual(len(rebuilt["imports"]["kernel32"]), 2)

    def test_sem_ponto_vai_para_unknown(self):
        rebuilt = iat_rebuild.rebuild({"0x401000": "funcao_solta"})
        self.assertIn("unknown", rebuilt["imports"])
        self.assertEqual(rebuilt["imports"]["unknown"][0]["name"], "funcao_solta")

    def test_idc_contem_make_name_para_todos(self):
        rebuilt = iat_rebuild.rebuild(HINTS)
        idc = iat_rebuild.generate_idc(rebuilt)
        self.assertIn("static main()", idc)
        self.assertEqual(idc.count("MakeName"), 3)
        self.assertIn('MakeName(ea, "kernel32_CreateFileA")', idc)
        self.assertIn('MakeName(ea, "kernel32_ReadFile")', idc)
        self.assertIn('MakeName(ea, "user32_MessageBoxA")', idc)
        self.assertIn("0x00401000", idc)

    def test_idc_sanitiza_nomes(self):
        name = iat_rebuild.idc_name("kernel32", "CreateFileA")
        self.assertEqual(name, "kernel32_CreateFileA")
        name2 = iat_rebuild.idc_name("ws2_32", "WSAStartup!")
        self.assertNotRegex(name2, r"[^A-Za-z0-9_]")

    def test_cli_json(self):
        out = self.run_cli(self.write_hints(HINTS))
        data = json.loads(out)
        self.assertIn("imports", data)
        self.assertEqual(set(data["imports"]), {"kernel32", "user32"})

    def test_cli_idc(self):
        out = self.run_cli(self.write_hints(HINTS), "--idc")
        self.assertIn("MakeName", out)
        self.assertIn("kernel32_CreateFileA", out)
        self.assertNotIn('"imports"', out)


if __name__ == "__main__":
    unittest.main()
