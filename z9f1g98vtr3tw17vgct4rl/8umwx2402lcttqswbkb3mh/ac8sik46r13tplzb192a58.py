"""Testes do 8umwx2402lcttqswbkb3mh (fixtures sinteticas)."""

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
        "evidence_link", os.path.join(HERE, "oj6vfrk6ees32192x89s4v.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = load_module()

BEHS = [{"id": "BEH-001", "descricao": "abre socket"},
        {"id": "BEH-002", "descricao": "cria arquivo"}]
EVS = [
    {"id": "EV-001", "funcao": "sub_401000", "descricao": "chamada WSASocket",
     "comportamento": "BEH-001"},
    {"id": "EV-002", "funcao": "sub_401000", "descricao": "string 'connect'",
     "comportamento": "BEH-001"},
    {"id": "EV-003", "funcao": "sub_402000", "descricao": "chamada CreateFileW",
     "comportamento": "BEH-002"},
]


class TestBuildMap(unittest.TestCase):
    def test_liga_tudo(self):
        rel = mod.build_map(BEHS, EVS)
        m = rel["mapa"]
        self.assertEqual(m["BEH-001"]["funcoes"], ["sub_401000"])
        self.assertEqual(len(m["BEH-001"]["evidencias"]), 2)
        self.assertEqual(m["BEH-002"]["funcoes"], ["sub_402000"])
        self.assertEqual(rel["sem_evidencia"], [])

    def test_sem_evidencia(self):
        rel = mod.build_map([{"id": "BEH-009", "descricao": "x"}], [])
        self.assertEqual(rel["sem_evidencia"], ["BEH-009"])
        self.assertEqual(rel["mapa"]["BEH-009"]["evidencias"], [])

    def test_evidencia_orfa_ignorada(self):
        evs = [{"id": "EV-9", "funcao": "f", "descricao": "d",
                "comportamento": "BEH-XXX"}]
        rel = mod.build_map(BEHS, evs)
        self.assertNotIn("BEH-XXX", rel["mapa"])

    def test_funcao_sem_duplicar(self):
        rel = mod.build_map(BEHS, EVS)
        self.assertEqual(len(rel["mapa"]["BEH-001"]["funcoes"]), 1)

    def test_entradas_vazias(self):
        rel = mod.build_map([], [])
        self.assertEqual(rel["mapa"], {})
        self.assertEqual(rel["sem_evidencia"], [])


class TestCli(unittest.TestCase):
    def test_cli(self):
        with tempfile.TemporaryDirectory() as td:
            b = os.path.join(td, "b.json")
            e = os.path.join(td, "e.json")
            with open(b, "w", encoding="utf-8") as f:
                json.dump({"comportamentos": BEHS}, f)
            with open(e, "w", encoding="utf-8") as f:
                json.dump({"evidencias": EVS}, f)
            r = subprocess.run(
                [sys.executable, os.path.join(HERE, "oj6vfrk6ees32192x89s4v.py"),
                 "--behaviors", b, "--evidences", e],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            rel = json.loads(r.stdout)
            self.assertEqual(len(rel["mapa"]), 2)
            self.assertEqual(rel["sem_evidencia"], [])


if __name__ == "__main__":
    unittest.main()
