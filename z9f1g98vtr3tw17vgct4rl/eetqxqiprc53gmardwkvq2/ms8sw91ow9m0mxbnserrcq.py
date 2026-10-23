#!/usr/bin/env python3
"""Testes do lab 80 — smali-deobfuscate. Fixtures 100% sintéticas."""

import importlib.util
import os
import unittest

_AQUI = os.path.dirname(os.path.abspath(__file__))


def _carregar():
    spec = importlib.util.spec_from_file_location(
        "smali_deobfuscate", os.path.join(_AQUI, "zi4g4gmex74toyl9z1gly2.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = _carregar()


class TestDeobfuscate(unittest.TestCase):
    def test_metodo_string_vira_getString(self):
        r = mod.deobfuscar([{"kind": "method", "name": "a", "sig": "()Ljava/lang/String;"}])
        self.assertEqual(r, [("a", "getString")])

    def test_colisao_ganha_sufixo(self):
        r = mod.deobfuscar(
            [
                {"kind": "method", "name": "a", "sig": "()Ljava/lang/String;"},
                {"kind": "method", "name": "b", "sig": "()Ljava/lang/String;"},
            ]
        )
        self.assertEqual(r[1], ("b", "getString_1"))

    def test_nome_legivel_preservado(self):
        r = mod.deobfuscar(
            [{"kind": "method", "name": "onCreate", "sig": "(Landroid/os/Bundle;)V"}]
        )
        self.assertEqual(r, [("onCreate", "onCreate")])

    def test_field_int_vira_count(self):
        r = mod.deobfuscar([{"kind": "field", "name": "c", "sig": "I"}])
        self.assertEqual(r, [("c", "count")])

    def test_void_vira_run(self):
        r = mod.deobfuscar([{"kind": "method", "name": "z", "sig": "()V"}])
        self.assertEqual(r, [("z", "run")])

    def test_deterministico(self):
        membros = [
            {"kind": "method", "name": "a", "sig": "()V"},
            {"kind": "method", "name": "b", "sig": "()V"},
        ]
        self.assertEqual(mod.deobfuscar(membros), mod.deobfuscar(membros))


if __name__ == "__main__":
    unittest.main()
