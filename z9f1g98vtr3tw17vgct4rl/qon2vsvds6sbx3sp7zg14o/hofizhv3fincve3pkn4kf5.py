#!/usr/bin/env python3
"""Testes do lab 88 — method-swizzle. Fixtures 100% sintéticas."""

import importlib.util
import os
import unittest

_AQUI = os.path.dirname(os.path.abspath(__file__))


def _carregar():
    spec = importlib.util.spec_from_file_location(
        "method_swizzle", os.path.join(_AQUI, "gw65uhu0jivy5e3nmp63em.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = _carregar()


class TestSwizzle(unittest.TestCase):
    def test_troca_implementacoes(self):
        r = mod.swizzle({"a": "impl_a", "b": "impl_b"}, "a", "b")
        self.assertEqual(r["tabela"]["a"], "impl_b")
        self.assertEqual(r["tabela"]["b"], "impl_a")
        self.assertEqual(r["trocados"], ["a", "b"])

    def test_duplo_swizzle_restaura(self):
        t = {"a": "impl_a", "b": "impl_b"}
        r1 = mod.swizzle(t, "a", "b")
        r2 = mod.swizzle(r1["tabela"], "a", "b")
        self.assertEqual(r2["tabela"], t)

    def test_metodo_desconhecido(self):
        with self.assertRaises(KeyError):
            mod.swizzle({"a": "x"}, "a", "z")

    def test_original_nao_mutada(self):
        t = {"a": "impl_a", "b": "impl_b"}
        mod.swizzle(t, "a", "b")
        self.assertEqual(t, {"a": "impl_a", "b": "impl_b"})


if __name__ == "__main__":
    unittest.main()
