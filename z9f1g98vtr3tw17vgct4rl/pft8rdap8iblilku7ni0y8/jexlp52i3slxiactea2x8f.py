"""Testes do pft8rdap8iblilku7ni0y8 (fixtures sinteticas)."""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def load_module():
    spec = importlib.util.spec_from_file_location(
        "antidebug_inventory", os.path.join(HERE, "fa4e7im8y6mam8z81jt2sg.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = load_module()

IMPORTS = {
    "kernel32.dll": ["IsDebuggerPresent", "GetTickCount", "CreateFileW", "Sleep"],
    "user32.dll": ["GetCursorPos", "MessageBoxW"],
    "advapi32.dll": ["RegOpenKeyExA"],
}


class TestScanImports(unittest.TestCase):
    def test_acha_defesas(self):
        ach = mod.scan_imports(IMPORTS)
        apis = {a["api"] for a in ach}
        self.assertIn("IsDebuggerPresent", apis)
        self.assertIn("GetTickCount", apis)
        self.assertIn("GetCursorPos", apis)
        self.assertIn("RegOpenKeyExA", apis)
        self.assertIn("Sleep", apis)

    def test_ignora_benignas(self):
        ach = mod.scan_imports({"kernel32.dll": ["CreateFileW", "ReadFile"]})
        self.assertEqual(ach, [])

    def test_case_insensitive(self):
        ach = mod.scan_imports({"k.dll": ["ISDEBUGGERPRESENT"]})
        self.assertEqual(len(ach), 1)
        self.assertEqual(ach[0]["categoria"], "deteccao-debugger")

    def test_sem_duplicatas(self):
        ach = mod.scan_imports({
            "a.dll": ["GetTickCount"], "b.dll": ["GetTickCount"]})
        self.assertEqual(len(ach), 1)

    def test_imports_vazio(self):
        self.assertEqual(mod.scan_imports({}), [])
        self.assertEqual(mod.scan_imports(None), [])


class TestScanDisasm(unittest.TestCase):
    def test_rdtsc(self):
        ach = mod.scan_disasm("mov eax, ebx\nrdtsc\nmov [t1], eax")
        self.assertTrue(any(a["api"] == "rdtsc" and
                            a["categoria"] == "temporizacao" for a in ach))

    def test_cpuid_e_int3(self):
        ach = mod.scan_disasm("cpuid\nint 3\nret")
        cats = {a["categoria"] for a in ach}
        self.assertIn("anti-vm", cats)
        self.assertIn("deteccao-debugger", cats)

    def test_limpo(self):
        self.assertEqual(mod.scan_disasm("mov eax, 1\nret"), [])

    def test_none(self):
        self.assertEqual(mod.scan_disasm(None), [])


class TestBuildInventory(unittest.TestCase):
    def test_agrupa_por_categoria(self):
        inv = mod.build_inventory(IMPORTS, "rdtsc")
        self.assertGreater(inv["total"], 0)
        self.assertIn("deteccao-debugger", inv["por_categoria"])
        self.assertIn("temporizacao", inv["por_categoria"])
        self.assertIn("anti-sandbox", inv["por_categoria"])
        self.assertIn("anti-vm", inv["por_categoria"])
        self.assertEqual(inv["total"], len(inv["defesas"]))


class TestCli(unittest.TestCase):
    def test_cli_stdout(self):
        with tempfile.TemporaryDirectory() as td:
            inp = os.path.join(td, "imp.json")
            with open(inp, "w", encoding="utf-8") as f:
                json.dump(IMPORTS, f)
            r = subprocess.run(
                [sys.executable, os.path.join(HERE, "fa4e7im8y6mam8z81jt2sg.py"),
                 "--input", inp],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            inv = json.loads(r.stdout)
            self.assertGreater(inv["total"], 0)

    def test_cli_com_disasm(self):
        with tempfile.TemporaryDirectory() as td:
            inp = os.path.join(td, "imp.json")
            dasm = os.path.join(td, "d.txt")
            with open(inp, "w", encoding="utf-8") as f:
                json.dump({"k.dll": ["CreateFileW"]}, f)
            with open(dasm, "w", encoding="utf-8") as f:
                f.write("rdtsc\ncpuid\n")
            r = subprocess.run(
                [sys.executable, os.path.join(HERE, "fa4e7im8y6mam8z81jt2sg.py"),
                 "--input", inp, "--disasm", dasm],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            inv = json.loads(r.stdout)
            self.assertEqual(inv["total"], 2)


if __name__ == "__main__":
    unittest.main()
