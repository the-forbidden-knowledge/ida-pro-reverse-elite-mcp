"""Testes do krsi0v4p4a8251u4z853pm (fixtures sinteticas)."""

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
        "9pd1ao2s9soicz7ndhxu9e_report", os.path.join(HERE, "hgrtba8s3eyyyd8ujqgex1.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = load_module()


class TestBuildReport(unittest.TestCase):
    def _manifest(self, td, fases):
        man = {}
        for fase, obj in fases.items():
            p = os.path.join(td, fase + ".json")
            with open(p, "w", encoding="utf-8") as f:
                json.dump(obj, f)
            man[fase] = p
        return man

    def test_todas_fases(self):
        with tempfile.TemporaryDirectory() as td:
            man = self._manifest(td, {
                "triagem": {"resumo": {"arquivos": 1}},
                "leitura": {"resumo": {"funcoes": 10}},
            })
            rel = mod.build_report(man)
        self.assertEqual(rel["relatorio"], "CLONAR")
        self.assertEqual(rel["resumo"]["fases_executadas"], 2)
        self.assertEqual(len(rel["resumo"]["fases_pendentes"]), 6)
        self.assertEqual(rel["fases"]["triagem"]["status"], "ok")
        self.assertEqual(rel["fases"]["unpack"]["status"], "nao-executada")
        self.assertIn("gerado_em", rel)

    def test_arquivo_invalido(self):
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "ruim.json")
            with open(p, "w", encoding="utf-8") as f:
                f.write("{invalido")
            rel = mod.build_report({"triagem": p})
        self.assertEqual(rel["fases"]["triagem"]["status"], "erro")

    def test_manifest_vazio(self):
        rel = mod.build_report({})
        self.assertEqual(rel["resumo"]["fases_executadas"], 0)
        self.assertEqual(len(rel["resumo"]["fases_pendentes"]), 8)

    def test_none(self):
        rel = mod.build_report(None)
        self.assertEqual(rel["fases"]["memoria"]["status"], "nao-executada")


class TestMarkdown(unittest.TestCase):
    def test_estrutura(self):
        rel = mod.build_report({})
        md = mod.to_markdown(rel)
        self.assertIn("# Relatorio CLONAR", md)
        self.assertIn("## Fases", md)
        self.assertIn("### triagem", md)
        self.assertIn("Fases executadas: 0/8", md)


class TestCli(unittest.TestCase):
    def test_cli_json(self):
        with tempfile.TemporaryDirectory() as td:
            man = os.path.join(td, "man.json")
            f1 = os.path.join(td, "t.json")
            with open(f1, "w", encoding="utf-8") as f:
                json.dump({"resumo": {"a": 1}}, f)
            with open(man, "w", encoding="utf-8") as f:
                json.dump({"triagem": f1}, f)
            r = subprocess.run(
                [sys.executable, os.path.join(HERE, "hgrtba8s3eyyyd8ujqgex1.py"),
                 "--manifest", man],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            rel = json.loads(r.stdout)
            self.assertEqual(rel["resumo"]["fases_executadas"], 1)

    def test_cli_md(self):
        with tempfile.TemporaryDirectory() as td:
            man = os.path.join(td, "man.json")
            with open(man, "w", encoding="utf-8") as f:
                json.dump({}, f)
            r = subprocess.run(
                [sys.executable, os.path.join(HERE, "hgrtba8s3eyyyd8ujqgex1.py"),
                 "--manifest", man, "--format", "md"],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("# Relatorio CLONAR", r.stdout)


if __name__ == "__main__":
    unittest.main()
