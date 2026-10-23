#!/usr/bin/env python3
"""Testes do lab 84 — frida-hooks. Fixtures 100% sintéticas."""

import importlib.util
import os
import unittest

_AQUI = os.path.dirname(os.path.abspath(__file__))


def _carregar():
    spec = importlib.util.spec_from_file_location(
        "frida_hooks", os.path.join(_AQUI, "um48xakyadwik0ss20bjr8.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = _carregar()


class TestFridaHooks(unittest.TestCase):
    def test_contem_java_use_e_implementation(self):
        js = mod.gerar_script([("com.a.B", "f", [])])
        self.assertIn('Java.use("com.a.B")', js)
        self.assertIn(".implementation = function()", js)

    def test_overload_quando_ha_tipos(self):
        js = mod.gerar_script([("com.a.B", "f", ["java.lang.String"])])
        self.assertIn('.overload("java.lang.String")', js)

    def test_sem_overload_quando_vazio(self):
        js = mod.gerar_script([("com.a.B", "f", [])])
        self.assertNotIn("overload", js)

    def test_repasse_ao_original(self):
        js = mod.gerar_script([("com.a.B", "f", [])])
        self.assertIn(".apply(this, arguments)", js)

    def test_multiplos_alvos(self):
        js = mod.gerar_script([("com.a.B", "f", []), ("com.a.C", "g", ["int"])])
        self.assertIn('Java.use("com.a.B")', js)
        self.assertIn('Java.use("com.a.C")', js)
        self.assertIn('.overload("int")', js)

    def test_envolve_em_java_perform(self):
        js = mod.gerar_script([])
        self.assertTrue(js.startswith("Java.perform(function() {"))
        self.assertTrue(js.rstrip().endswith("});"))


if __name__ == "__main__":
    unittest.main()
