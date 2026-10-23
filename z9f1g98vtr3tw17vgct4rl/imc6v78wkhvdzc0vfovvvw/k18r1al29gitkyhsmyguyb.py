#!/usr/bin/env python3
"""Testes do lab 93 — baroque-verdict (fixtures sintéticas)."""

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
    _mm = _ilu.module_from_spec(_sp); _sp.loader.exec_module(_mm)
    return _mm
_mx_baroque_verdict = _loadmod("f8sur1l9f7koeo1kg96gn1.py")
verdict = _mx_baroque_verdict.verdict


def ledger(ok: int, total: int, formato="elf64", alvo="a"):
    verifs = [{"nome": "v%d" % i, "passou": i < ok, "detalhe": ""}
              for i in range(total)]
    return {"entradas": [{"formato": formato, "alvo": alvo,
                          "verificacoes": verifs,
                          "passaram": ok, "total": total}],
            "verificacoes_ok": ok, "verificacoes_total": total}


class TestVerdict(unittest.TestCase):
    def test_clonado_100(self):
        r = verdict(ledger(4, 4), "aaa", "bbb")
        self.assertEqual(r["veredito"], "CLONADO 100%")
        self.assertEqual(r["cobertura"], 100.0)
        self.assertEqual(r["divergencias"], [])
        self.assertEqual(r["sha256_alvo"], "aaa")
        self.assertEqual(r["sha256_clone"], "bbb")

    def test_parcial(self):
        r = verdict(ledger(8, 10), "aaa", "bbb")
        self.assertEqual(r["veredito"], "PARCIAL")
        self.assertEqual(r["cobertura"], 80.0)
        self.assertEqual(len(r["divergencias"]), 2)

    def test_divergente(self):
        r = verdict(ledger(1, 10), "aaa", "bbb")
        self.assertEqual(r["veredito"], "DIVERGENTE")

    def test_formatos(self):
        lg = {"entradas": [
            {"formato": "dex", "alvo": "a", "verificacoes": [],
             "passaram": 0, "total": 0},
            {"formato": "elf64", "alvo": "b", "verificacoes": [],
             "passaram": 0, "total": 0}],
            "verificacoes_ok": 0, "verificacoes_total": 0}
        r = verdict(lg, "aaa", "bbb")
        self.assertEqual(r["formatos"], ["dex", "elf64"])
        self.assertEqual(r["veredito"], "CLONADO 100%")

    def test_divergencia_nomeada(self):
        r = verdict(ledger(1, 2, alvo="app.apk"), "aaa", "bbb")
        self.assertIn("app.apk/v1", r["divergencias"])


class TestCli(unittest.TestCase):
    def test_cli_veredito(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w",
                                         encoding="utf-8") as f:
            json.dump(ledger(2, 2), f)
            caminho = f.name
        try:
            r = subprocess.run(
                [sys.executable,
                 os.path.join(os.path.dirname(__file__), "f8sur1l9f7koeo1kg96gn1.py"),
                 caminho, "--sha-alvo", "aaa", "--sha-clone", "bbb"],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 0)
            saida = json.loads(r.stdout)
            self.assertEqual(saida["veredito"], "CLONADO 100%")
        finally:
            os.unlink(caminho)

    def test_cli_falha_retorna_2(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w",
                                         encoding="utf-8") as f:
            json.dump(ledger(0, 2), f)
            caminho = f.name
        try:
            r = subprocess.run(
                [sys.executable,
                 os.path.join(os.path.dirname(__file__), "f8sur1l9f7koeo1kg96gn1.py"),
                 caminho, "--sha-alvo", "aaa", "--sha-clone", "bbb"],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 2)
            self.assertEqual(json.loads(r.stdout)["veredito"], "DIVERGENTE")
        finally:
            os.unlink(caminho)


if __name__ == "__main__":
    unittest.main()
