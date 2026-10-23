"""Testes do ga07t5mx7v0op0qahwb3uc (fixtures sinteticas)."""

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
        "obligation_ledger", os.path.join(HERE, "m2ese22k0myo678menipp9.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = load_module()

MAPA = {
    "BEH-001": {"funcoes": ["sub_401000"], "evidencias": [
        {"id": "EV-001", "descricao": "chamada WSASocket", "funcao": "sub_401000"},
        {"id": "EV-002", "descricao": "string connect", "funcao": "sub_401000"},
    ]},
    "BEH-002": {"funcoes": [], "evidencias": []},
}


class TestBuildLedger(unittest.TestCase):
    def test_uma_obrigacao_por_evidencia(self):
        led = mod.build_ledger(MAPA)
        self.assertEqual(len(led["obrigacoes"]), 3)
        self.assertTrue(all(o["status"] == "pendente" for o in led["obrigacoes"]))

    def test_marca_concluidas(self):
        led = mod.build_ledger(MAPA, ["BEH-001"])
        feitas = [o for o in led["obrigacoes"] if o["comportamento"] == "BEH-001"]
        pend = [o for o in led["obrigacoes"] if o["comportamento"] == "BEH-002"]
        self.assertTrue(all(o["status"] == "feito" for o in feitas))
        self.assertTrue(all(o["status"] == "pendente" for o in pend))

    def test_sem_evidencia_tem_nota(self):
        led = mod.build_ledger(MAPA)
        o = [x for x in led["obrigacoes"] if x["comportamento"] == "BEH-002"][0]
        self.assertIn("investigar", o["notas"])

    def test_ordenado(self):
        led = mod.build_ledger(MAPA)
        ids = [o["comportamento"] for o in led["obrigacoes"]]
        self.assertEqual(ids, sorted(ids))

    def test_mapa_vazio(self):
        self.assertEqual(mod.build_ledger({}), {"obrigacoes": []})
        self.assertEqual(mod.build_ledger(None), {"obrigacoes": []})


class TestCli(unittest.TestCase):
    def test_cli(self):
        with tempfile.TemporaryDirectory() as td:
            inp = os.path.join(td, "mapa.json")
            with open(inp, "w", encoding="utf-8") as f:
                json.dump({"mapa": MAPA}, f)
            r = subprocess.run(
                [sys.executable, os.path.join(HERE, "m2ese22k0myo678menipp9.py"),
                 "--input", inp, "--concluidas", "BEH-001"],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            led = json.loads(r.stdout)
            self.assertEqual(len(led["obrigacoes"]), 3)
            self.assertEqual(
                sum(1 for o in led["obrigacoes"] if o["status"] == "feito"), 2)


if __name__ == "__main__":
    unittest.main()
