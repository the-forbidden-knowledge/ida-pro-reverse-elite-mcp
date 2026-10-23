"""Testes do m49dd353e4mwmhzhwd1xcp (fixtures sinteticas)."""

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
        "coverage_verify", os.path.join(HERE, "3vvtel22lho9l5gwbqhfbr.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = load_module()

LEDGER = {"obrigacoes": [
    {"comportamento": "BEH-001", "status": "feito"},
    {"comportamento": "BEH-001", "status": "feito"},
    {"comportamento": "BEH-002", "status": "pendente"},
    {"comportamento": "BEH-003", "status": "pendente"},
]}


class TestVerify(unittest.TestCase):
    def test_contagens(self):
        rel = mod.verify(LEDGER)
        self.assertEqual(rel["total"], 4)
        self.assertEqual(rel["feitas"], 2)
        self.assertEqual(rel["pendentes"], 2)
        self.assertEqual(rel["cobertura_pct"], 50.0)

    def test_gaps(self):
        rel = mod.verify(LEDGER)
        self.assertEqual(rel["gaps"], ["BEH-002", "BEH-003"])

    def test_por_comportamento(self):
        rel = mod.verify(LEDGER)
        self.assertEqual(rel["por_comportamento"]["BEH-001"],
                         {"total": 2, "feitas": 2})
        self.assertEqual(rel["por_comportamento"]["BEH-002"],
                         {"total": 1, "feitas": 0})

    def test_tudo_feito(self):
        rel = mod.verify({"obrigacoes": [
            {"comportamento": "BEH-001", "status": "feito"}]})
        self.assertEqual(rel["cobertura_pct"], 100.0)
        self.assertEqual(rel["gaps"], [])

    def test_vazio(self):
        rel = mod.verify({"obrigacoes": []})
        self.assertEqual(rel["cobertura_pct"], 0.0)
        self.assertEqual(rel["total"], 0)

    def test_none(self):
        rel = mod.verify(None)
        self.assertEqual(rel["total"], 0)


class TestCli(unittest.TestCase):
    def test_cli(self):
        with tempfile.TemporaryDirectory() as td:
            inp = os.path.join(td, "ledger.json")
            with open(inp, "w", encoding="utf-8") as f:
                json.dump(LEDGER, f)
            r = subprocess.run(
                [sys.executable, os.path.join(HERE, "3vvtel22lho9l5gwbqhfbr.py"),
                 "--input", inp],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            rel = json.loads(r.stdout)
            self.assertEqual(rel["cobertura_pct"], 50.0)
            self.assertEqual(len(rel["gaps"]), 2)


if __name__ == "__main__":
    unittest.main()
