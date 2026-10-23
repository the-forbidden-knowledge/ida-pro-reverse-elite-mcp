#!/usr/bin/env python3
"""Testes do lab 81 — simplify-deadcode. Fixtures 100% sintéticas."""

import importlib.util
import os
import unittest

_AQUI = os.path.dirname(os.path.abspath(__file__))


def _carregar():
    spec = importlib.util.spec_from_file_location(
        "simplify_deadcode", os.path.join(_AQUI, "jby54ndv70x0cck3m7igdw.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = _carregar()


class TestDeadcode(unittest.TestCase):
    def test_cadeia_toda_viva(self):
        g = {"a": ["b"], "b": ["c"], "c": []}
        r = mod.podar(g, ["a"])
        self.assertEqual(r["mortos"], [])
        self.assertEqual(r["removidos"], 0)

    def test_isolado_morre(self):
        g = {"a": ["b"], "b": [], "x": ["y"], "y": []}
        r = mod.podar(g, ["a"])
        self.assertEqual(r["mortos"], ["x", "y"])
        self.assertEqual(r["removidos"], 2)

    def test_ciclo_nao_trava(self):
        g = {"a": ["b"], "b": ["a"], "z": []}
        r = mod.podar(g, ["a"])
        self.assertEqual(sorted(r["vivos"]), ["a", "b"])
        self.assertEqual(r["mortos"], ["z"])

    def test_multiplas_entradas(self):
        g = {"a": [], "b": [], "c": []}
        r = mod.podar(g, ["a", "b"])
        self.assertEqual(r["mortos"], ["c"])

    def test_entrada_fora_do_grafo(self):
        r = mod.podar({"a": []}, ["fantasma"])
        self.assertIn("fantasma", r["vivos"])
        self.assertEqual(r["mortos"], ["a"])


if __name__ == "__main__":
    unittest.main()
