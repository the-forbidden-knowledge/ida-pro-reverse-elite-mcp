"""Testes do atww5zomvexic1pxsksaog (fixtures sinteticas)."""

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
        "defense_report", os.path.join(HERE, "87pd3uguu2cczxvkd0xxoy.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = load_module()

INV = {"defesas": [
    {"api": "IsDebuggerPresent", "categoria": "deteccao-debugger"},
    {"api": "GetTickCount", "categoria": "temporizacao"},
], "total": 2}
PATCH = {"patches": [
    {"alvo": "IsDebuggerPresent", "tipo": "forcar-retorno"},
    {"alvo": "ApiX", "tipo": "manual"},
]}
TLS = {"tls_presente": True, "total_callbacks": 1}


class TestBuildReport(unittest.TestCase):
    def test_completo(self):
        rel = mod.build_report(INV, PATCH, TLS)
        self.assertEqual(rel["fase"], "bypass")
        self.assertEqual(rel["resumo"]["defesas_encontradas"], 2)
        self.assertEqual(rel["resumo"]["patches_planejados"], 2)
        self.assertEqual(rel["resumo"]["patches_manuais"], 1)
        self.assertTrue(rel["resumo"]["tls_presente"])
        self.assertIn("deteccao-debugger", rel["defesas"]["por_categoria"])
        self.assertEqual(rel["patches"]["por_tipo"]["forcar-retorno"], 1)

    def test_vazio(self):
        rel = mod.build_report(None, None, None)
        self.assertEqual(rel["resumo"]["defesas_encontradas"], 0)
        self.assertEqual(rel["resumo"]["patches_planejados"], 0)
        self.assertFalse(rel["resumo"]["tls_presente"])
        self.assertEqual(rel["tls"]["callbacks"], 0)

    def test_so_inventario(self):
        rel = mod.build_report(INV, None, None)
        self.assertEqual(rel["resumo"]["defesas_encontradas"], 2)
        self.assertEqual(rel["resumo"]["patches_planejados"], 0)


class TestCli(unittest.TestCase):
    def _write(self, td, nome, obj):
        p = os.path.join(td, nome)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(obj, f)
        return p

    def test_cli_completo(self):
        with tempfile.TemporaryDirectory() as td:
            inv = self._write(td, "inv.json", INV)
            pat = self._write(td, "pat.json", PATCH)
            tls = self._write(td, "tls.json", TLS)
            out = os.path.join(td, "rel.json")
            r = subprocess.run(
                [sys.executable, os.path.join(HERE, "87pd3uguu2cczxvkd0xxoy.py"),
                 "--inventory", inv, "--patches", pat, "--tls", tls,
                 "--output", out],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            with open(out, encoding="utf-8") as f:
                rel = json.load(f)
            self.assertEqual(rel["fase"], "bypass")
            self.assertTrue(rel["tls"]["presente"])

    def test_cli_stdout(self):
        r = subprocess.run(
            [sys.executable, os.path.join(HERE, "87pd3uguu2cczxvkd0xxoy.py")],
            capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        rel = json.loads(r.stdout)
        self.assertEqual(rel["resumo"]["defesas_encontradas"], 0)


if __name__ == "__main__":
    unittest.main()
