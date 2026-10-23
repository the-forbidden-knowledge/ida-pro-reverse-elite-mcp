"""Testes do r7vkuk0bo7khhekzv7to9p (fixtures sinteticas)."""

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
        "patch_plan", os.path.join(HERE, "k9blishyhhhwfov279ga8l.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = load_module()


class TestPlanFor(unittest.TestCase):
    def test_conhecida(self):
        p = mod.plan_for("IsDebuggerPresent", "deteccao-debugger")
        self.assertEqual(p["tipo"], "forcar-retorno")
        self.assertEqual(p["alvo"], "IsDebuggerPresent")
        self.assertEqual(p["categoria"], "deteccao-debugger")
        self.assertTrue(p["bytes"])

    def test_rdtsc_nop(self):
        p = mod.plan_for("rdtsc")
        self.assertEqual(p["tipo"], "nop")
        self.assertEqual(p["bytes"], "90 90")

    def test_desconhecida_manual(self):
        p = mod.plan_for("ApiEstranhaXyz")
        self.assertEqual(p["tipo"], "manual")
        self.assertEqual(p["alvo"], "ApiEstranhaXyz")

    def test_case_insensitive(self):
        p = mod.plan_for("SLEEP")
        self.assertEqual(p["tipo"], "forcar-retorno")


class TestBuildPlan(unittest.TestCase):
    def test_lista(self):
        plano = mod.build_plan([
            {"api": "IsDebuggerPresent", "categoria": "deteccao-debugger"},
            {"api": "GetTickCount"},
        ])
        self.assertEqual(len(plano["patches"]), 2)
        tipos = {p["tipo"] for p in plano["patches"]}
        self.assertIn("forcar-retorno", tipos)

    def test_vazia(self):
        self.assertEqual(mod.build_plan([]), {"patches": []})


class TestCli(unittest.TestCase):
    def test_cli_inventario(self):
        with tempfile.TemporaryDirectory() as td:
            inp = os.path.join(td, "inv.json")
            with open(inp, "w", encoding="utf-8") as f:
                json.dump({"defesas": [
                    {"api": "IsDebuggerPresent", "categoria": "deteccao-debugger"},
                    {"api": "rdtsc", "categoria": "temporizacao"},
                ]}, f)
            r = subprocess.run(
                [sys.executable, os.path.join(HERE, "k9blishyhhhwfov279ga8l.py"),
                 "--input", inp],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            plano = json.loads(r.stdout)
            self.assertEqual(len(plano["patches"]), 2)

    def test_cli_lista_simples(self):
        with tempfile.TemporaryDirectory() as td:
            inp = os.path.join(td, "apis.json")
            with open(inp, "w", encoding="utf-8") as f:
                json.dump(["Sleep", "cpuid"], f)
            r = subprocess.run(
                [sys.executable, os.path.join(HERE, "k9blishyhhhwfov279ga8l.py"),
                 "--input", inp],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            plano = json.loads(r.stdout)
            self.assertEqual(plano["patches"][0]["tipo"], "forcar-retorno")
            self.assertEqual(plano["patches"][1]["tipo"], "manual")

    def test_cli_arquivo_saida(self):
        with tempfile.TemporaryDirectory() as td:
            inp = os.path.join(td, "apis.json")
            out = os.path.join(td, "plano.json")
            with open(inp, "w", encoding="utf-8") as f:
                json.dump({"apis": ["GetTickCount"]}, f)
            r = subprocess.run(
                [sys.executable, os.path.join(HERE, "k9blishyhhhwfov279ga8l.py"),
                 "--input", inp, "--output", out],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            with open(out, encoding="utf-8") as f:
                plano = json.load(f)
            self.assertEqual(len(plano["patches"]), 1)


if __name__ == "__main__":
    unittest.main()
