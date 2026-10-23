#!/usr/bin/env python3
"""Testes do lab 85 — objection-repl. Fixtures 100% sintéticas."""

import importlib.util
import os
import unittest

_AQUI = os.path.dirname(os.path.abspath(__file__))


def _carregar():
    spec = importlib.util.spec_from_file_location(
        "objection_repl", os.path.join(_AQUI, "lvkyrtpyndmz485so2pcx2.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = _carregar()

ESTADO = {
    "classes": {"com.exemplo.Login": ["autenticar", "sair"]},
    "modulos": [{"nome": "libapp.so", "base": "0x7f001000"}],
}


class TestObjectionRepl(unittest.TestCase):
    def test_watch_class_ok(self):
        r = mod.executar("android hooking watch class com.exemplo.Login", ESTADO)
        self.assertEqual(r["classe"], "com.exemplo.Login")
        self.assertEqual(r["metodos_observados"], ["autenticar", "sair"])

    def test_watch_class_desconhecida(self):
        r = mod.executar("android hooking watch class com.x.Nada", ESTADO)
        self.assertIn("erro", r)

    def test_memory_list_modules(self):
        r = mod.executar("memory list modules", ESTADO)
        self.assertEqual(len(r["modulos"]), 1)
        self.assertEqual(r["modulos"][0]["nome"], "libapp.so")

    def test_comando_desconhecido(self):
        r = mod.executar("ios pwn tudo", ESTADO)
        self.assertIn("erro", r)

    def test_estado_vazio(self):
        r = mod.executar("memory list modules", {})
        self.assertEqual(r["modulos"], [])


if __name__ == "__main__":
    unittest.main()
