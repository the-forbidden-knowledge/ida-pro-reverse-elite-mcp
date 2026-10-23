"""Testes do d9yen9lqdjkquwp3jjyxep (fixtures sinteticas)."""

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
        "behavior_spec", os.path.join(HERE, "50x6rnt1dsaz2bm9gktlzd.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = load_module()


class TestParseSpec(unittest.TestCase):
    def test_linha_simples(self):
        out = mod.parse_spec(["cria arquivo temporario\n"])
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["id"], "BEH-001")
        self.assertEqual(out[0]["descricao"], "cria arquivo temporario")
        self.assertEqual(out[0]["pre_condicoes"], "")
        self.assertEqual(out[0]["efeitos"], "")

    def test_linha_completa(self):
        out = mod.parse_spec(
            ["persiste no registro ;; usuario logado ;; chave criada em Run\n"])
        self.assertEqual(out[0]["pre_condicoes"], "usuario logado")
        self.assertEqual(out[0]["efeitos"], "chave criada em Run")

    def test_ids_sequenciais(self):
        out = mod.parse_spec(["a\n", "b\n", "c\n"])
        self.assertEqual([b["id"] for b in out], ["BEH-001", "BEH-002", "BEH-003"])

    def test_ignora_comentarios_e_vazias(self):
        out = mod.parse_spec(["# cabecalho\n", "\n", "  \n", "valido\n"])
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["descricao"], "valido")

    def test_vazio(self):
        self.assertEqual(mod.parse_spec([]), [])


class TestCli(unittest.TestCase):
    def test_cli_stdout(self):
        with tempfile.TemporaryDirectory() as td:
            inp = os.path.join(td, "b.txt")
            with open(inp, "w", encoding="utf-8") as f:
                f.write("# obs\nabre socket ;; rede disponivel ;; conexao tcp\n")
            r = subprocess.run(
                [sys.executable, os.path.join(HERE, "50x6rnt1dsaz2bm9gktlzd.py"),
                 "--input", inp],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            spec = json.loads(r.stdout)
            self.assertEqual(len(spec["comportamentos"]), 1)
            self.assertEqual(spec["comportamentos"][0]["efeitos"], "conexao tcp")

    def test_cli_arquivo(self):
        with tempfile.TemporaryDirectory() as td:
            inp = os.path.join(td, "b.txt")
            out = os.path.join(td, "spec.json")
            with open(inp, "w", encoding="utf-8") as f:
                f.write("faz polling\n")
            r = subprocess.run(
                [sys.executable, os.path.join(HERE, "50x6rnt1dsaz2bm9gktlzd.py"),
                 "--input", inp, "--output", out],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            with open(out, encoding="utf-8") as f:
                spec = json.load(f)
            self.assertEqual(spec["comportamentos"][0]["id"], "BEH-001")


if __name__ == "__main__":
    unittest.main()
