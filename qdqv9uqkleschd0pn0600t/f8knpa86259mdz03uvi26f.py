#!/usr/bin/env python3
"""Teste ponta a ponta da prova de clonagem: roda o qdqv9uqkleschd0pn0600t completo e afirma
cobertura de 100% e strings recuperadas idênticas às esperadas."""

import ast
import importlib.util
import json
import os
import unittest

_AQUI = os.path.dirname(os.path.abspath(__file__))


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestDemo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qdqv9uqkleschd0pn0600t = _load(os.path.join(_AQUI, "z71me9i2b581v1yejqq9v1.py"), "run_qdqv9uqkleschd0pn0600t")
        cls.resultado = cls.qdqv9uqkleschd0pn0600t.main()
        with open(os.path.join(_AQUI, "target_spec.json"),
                  encoding="utf-8") as f:
            cls.spec = json.load(f)

    def test_veredito(self):
        self.assertTrue(self.resultado["ok"])
        self.assertEqual(self.resultado["veredito"], "CLONADO 100%")

    def test_cobertura_100(self):
        self.assertEqual(self.resultado["cobertura"], 100.0)

    def test_strings_recuperadas(self):
        self.assertEqual(sorted(self.resultado["strings"]),
                         sorted(self.spec["strings_esperadas"]))

    def test_clone_valido(self):
        clone = os.path.join(_AQUI, "gk6g9tpaa4540ycewbkqgj.py")
        self.assertTrue(os.path.exists(clone))
        with open(clone, encoding="utf-8") as f:
            ast.parse(f.read())  # sintaxe válida

    def test_shas_presentes(self):
        self.assertEqual(len(self.resultado["sha_alvo"]), 64)
        self.assertEqual(len(self.resultado["sha_clone"]), 64)
        self.assertEqual(self.resultado["sha_alvo"], self.spec["sha256"])


if __name__ == "__main__":
    unittest.main()
