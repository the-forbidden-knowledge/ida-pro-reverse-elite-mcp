#!/usr/bin/env python3
"""Testes do lab 92 — fidelity-ledger (fixtures sintéticas)."""

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
_mx_fidelity_ledger = _loadmod("dl7c8duizxtdfffu98vld7.py")
build_ledger, diff_methods, fidelity_score, ledger_entry, ledger_score, to_json = (_mx_fidelity_ledger.build_ledger, _mx_fidelity_ledger.diff_methods, _mx_fidelity_ledger.fidelity_score, _mx_fidelity_ledger.ledger_entry, _mx_fidelity_ledger.ledger_score, _mx_fidelity_ledger.to_json)


def metodo(nome, sig="()V", tam=100):
    return {"nome": nome, "assinatura": sig, "tamanho": tam}


class TestDiffMethods(unittest.TestCase):
    def test_identicos(self):
        d = diff_methods([metodo("a"), metodo("b")], [metodo("a"), metodo("b")])
        self.assertEqual(d["identical"], ["a", "b"])
        self.assertEqual(d["similar"], [])
        self.assertEqual(d["new"], [])
        self.assertEqual(d["deleted"], [])

    def test_categorias(self):
        orig = [metodo("a"), metodo("b"), metodo("c")]
        clone = [metodo("a"), metodo("b", "()I"), metodo("d")]
        d = diff_methods(orig, clone)
        self.assertEqual(d["identical"], ["a"])
        self.assertEqual(d["similar"], ["b"])
        self.assertEqual(d["new"], ["d"])
        self.assertEqual(d["deleted"], ["c"])

    def test_tamanho_diferente_eh_similar(self):
        d = diff_methods([metodo("a", "()V", 100)], [metodo("a", "()V", 120)])
        self.assertEqual(d["similar"], ["a"])

    def test_vazios(self):
        d = diff_methods([], [])
        self.assertEqual(d["identical"], [])


class TestFidelityScore(unittest.TestCase):
    def test_100(self):
        d = diff_methods([metodo("a")], [metodo("a")])
        self.assertEqual(fidelity_score(d, 1), 100.0)

    def test_parcial(self):
        d = {"identical": ["a"], "similar": ["b"], "new": [], "deleted": ["c"]}
        self.assertEqual(fidelity_score(d, 3), 50.0)

    def test_zero_original(self):
        self.assertEqual(fidelity_score(diff_methods([], []), 0), 100.0)


class TestLedger(unittest.TestCase):
    def test_entry(self):
        e = ledger_entry("dex", "app.apk", [
            {"nome": "metodos", "passou": True, "detalhe": "10/10"},
            {"nome": "strings", "passou": False, "detalhe": "8/10"}])
        self.assertEqual(e["passaram"], 1)
        self.assertEqual(e["total"], 2)

    def test_build_e_score(self):
        entradas = [
            ledger_entry("elf64", "a", [{"nome": "x", "passou": True, "detalhe": ""}]),
            ledger_entry("dex", "b", [{"nome": "y", "passou": False, "detalhe": ""}]),
        ]
        ledger = build_ledger(entradas)
        self.assertEqual(ledger["verificacoes_ok"], 1)
        self.assertEqual(ledger["verificacoes_total"], 2)
        self.assertEqual(ledger_score(ledger), 50.0)

    def test_to_json(self):
        ledger = build_ledger([ledger_entry("pe", "p", [])])
        self.assertEqual(json.loads(to_json(ledger))["verificacoes_total"], 0)


class TestCli(unittest.TestCase):
    def test_cli(self):
        entradas = [ledger_entry("elf64", "a",
                                 [{"nome": "x", "passou": True, "detalhe": ""}])]
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w",
                                         encoding="utf-8") as f:
            json.dump(entradas, f)
            caminho = f.name
        try:
            r = subprocess.run(
                [sys.executable,
                 os.path.join(os.path.dirname(__file__), "dl7c8duizxtdfffu98vld7.py"),
                 caminho],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 0)
            self.assertIn("100.0%", r.stdout)
        finally:
            os.unlink(caminho)


if __name__ == "__main__":
    unittest.main()
