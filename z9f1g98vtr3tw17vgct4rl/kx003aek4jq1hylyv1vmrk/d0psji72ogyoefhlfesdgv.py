"""Testes do kx003aek4jq1hylyv1vmrk (fixtures sinteticas)."""

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
        "behavior_diff", os.path.join(HERE, "ue4knvccnagx0aa7a8j78p.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = load_module()

ORIG = {"comportamentos": [
    {"id": "BEH-001", "descricao": "abre socket",
     "pre_condicoes": "rede ok", "efeitos": "conexao tcp"},
    {"id": "BEH-002", "descricao": "cria arquivo",
     "pre_condicoes": "", "efeitos": "arquivo tmp"},
    {"id": "BEH-003", "descricao": "persiste no registro",
     "pre_condicoes": "admin", "efeitos": "chave Run"},
]}
CLONE = {"comportamentos": [
    {"id": "BEH-001", "descricao": "abre socket",
     "pre_condicoes": "rede ok", "efeitos": "conexao tcp"},
    {"id": "BEH-002", "descricao": "cria arquivo",
     "pre_condicoes": "", "efeitos": "arquivo TEMP"},  # efeito igual (case)
    {"id": "BEH-004", "descricao": "exibe janela",
     "pre_condicoes": "", "efeitos": "gui"},
]}


class TestDiff(unittest.TestCase):
    def test_faltando_e_extras(self):
        rel = mod.diff(ORIG, CLONE)
        self.assertEqual([f["id"] for f in rel["faltando"]], ["BEH-003"])
        self.assertEqual([e["id"] for e in rel["extras"]], ["BEH-004"])

    def test_divergente(self):
        clone = {"comportamentos": [
            {"id": "BEH-001", "descricao": "abre socket",
             "pre_condicoes": "rede ok", "efeitos": "conexao UDP"}]}
        rel = mod.diff(ORIG, clone)
        divs = {d["id"]: d for d in rel["divergentes"]}
        self.assertIn("BEH-001", divs)
        self.assertIn("efeitos", divs["BEH-001"]["mudancas"])

    def test_identicos(self):
        rel = mod.diff(ORIG, ORIG)
        self.assertEqual(rel["faltando"], [])
        self.assertEqual(rel["extras"], [])
        self.assertEqual(rel["divergentes"], [])
        self.assertEqual(rel["resumo"]["total_original"], 3)

    def test_casa_por_descricao(self):
        clone = {"comportamentos": [
            {"id": "B-1", "descricao": "abre socket",
             "pre_condicoes": "rede ok", "efeitos": "conexao tcp"}]}
        orig = {"comportamentos": [
            {"id": "BEH-001", "descricao": "abre socket",
             "pre_condicoes": "rede ok", "efeitos": "conexao tcp"}]}
        rel = mod.diff(orig, clone)
        self.assertEqual(rel["faltando"], [])
        self.assertEqual(rel["extras"], [])

    def test_vazios(self):
        rel = mod.diff({"comportamentos": []}, {"comportamentos": []})
        self.assertEqual(rel["resumo"]["total_original"], 0)


class TestCli(unittest.TestCase):
    def test_cli(self):
        with tempfile.TemporaryDirectory() as td:
            o = os.path.join(td, "o.json")
            c = os.path.join(td, "c.json")
            with open(o, "w", encoding="utf-8") as f:
                json.dump(ORIG, f)
            with open(c, "w", encoding="utf-8") as f:
                json.dump(CLONE, f)
            r = subprocess.run(
                [sys.executable, os.path.join(HERE, "ue4knvccnagx0aa7a8j78p.py"),
                 "--original", o, "--clone", c],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            rel = json.loads(r.stdout)
            self.assertEqual(rel["resumo"]["faltando"], 1)
            self.assertEqual(rel["resumo"]["extras"], 1)


if __name__ == "__main__":
    unittest.main()
