#!/usr/bin/env python3
"""Testes do lab 82 — androsim-diff. Fixtures 100% sintéticas."""

import importlib.util
import os
import unittest

_AQUI = os.path.dirname(os.path.abspath(__file__))


def _carregar():
    spec = importlib.util.spec_from_file_location(
        "androsim_diff", os.path.join(_AQUI, "gx81zth8924sn2qo0790zd.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = _carregar()


class TestAndrosimDiff(unittest.TestCase):
    def test_identicos_score_100(self):
        r = mod.comparar({"a": "h1"}, {"a": "h1"})
        self.assertEqual(r["fidelity_score"], 100.0)
        self.assertEqual(r["identical"], ["a"])

    def test_similar_meio_ponto(self):
        r = mod.comparar({"a": "h1", "b": "h2"}, {"a": "h1", "b": "hX"})
        self.assertEqual(r["fidelity_score"], 75.0)
        self.assertEqual(r["similar"], ["b"])

    def test_new_e_deleted(self):
        r = mod.comparar({"a": "h1"}, {"b": "h2"})
        self.assertEqual(r["deleted"], ["a"])
        self.assertEqual(r["new"], ["b"])
        self.assertEqual(r["fidelity_score"], 0.0)

    def test_vazio_score_100(self):
        self.assertEqual(mod.comparar({}, {})["fidelity_score"], 100.0)

    def test_misto(self):
        r = mod.comparar(
            {"a": "1", "b": "2", "c": "3"}, {"a": "1", "b": "X", "d": "4"}
        )
        self.assertEqual(r["identical"], ["a"])
        self.assertEqual(r["similar"], ["b"])
        self.assertEqual(r["deleted"], ["c"])
        self.assertEqual(r["new"], ["d"])
        # (1 + 0.5) / 4 * 100 = 37.5
        self.assertEqual(r["fidelity_score"], 37.5)


if __name__ == "__main__":
    unittest.main()
