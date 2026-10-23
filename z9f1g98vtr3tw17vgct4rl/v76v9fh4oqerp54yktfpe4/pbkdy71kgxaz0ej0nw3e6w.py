#!/usr/bin/env python3
"""Testes do lab 64 -- wfp-simulate (fixtures sinteticas)."""
import importlib.util
import json
import os
import unittest

_AQUI = os.path.dirname(os.path.abspath(__file__))


def _load():
    spec = importlib.util.spec_from_file_location(
        "wfp_simulate", os.path.join(_AQUI, "o5ya9efmtt9leriy8lunft.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


mod = _load()


class TestWfpSimulate(unittest.TestCase):
    def _rules(self):
        with open(os.path.join(_AQUI, "rules.json"), encoding="utf-8") as f:
            return json.load(f)

    def test_hidden_block_wins(self):
        # bloqueio na camada oculta vence mesmo sem regra visivel
        r = mod.decide({"direction": "in", "proto": "tcp", "port": 80},
                       self._rules())
        self.assertEqual(r["verdict"], "block")
        self.assertEqual(r["layer"], "static")

    def test_best_match_specificity(self):
        # Vis-Allow-Web (3 campos) vence Vis-Block-443 (2 campos)
        r = mod.decide({"direction": "out", "proto": "tcp", "port": 443},
                       self._rules())
        self.assertEqual(r["verdict"], "allow")
        self.assertEqual(r["rule"], "Vis-Allow-Web")

    def test_configurable_layer(self):
        r = mod.decide({"direction": "out", "app": "updater.exe", "port": 443},
                       self._rules())
        self.assertEqual(r["layer"], "configurable")

    def test_auth_bypass(self):
        r = mod.decide({"direction": "out", "port": 8443}, self._rules())
        self.assertEqual(r["verdict"], "allow")
        self.assertEqual(r["layer"], "auth_bypass")

    def test_default_block(self):
        r = mod.decide({"direction": "out", "proto": "udp", "port": 9999},
                       self._rules())
        self.assertEqual(r["verdict"], "block")
        self.assertEqual(r["layer"], "default")

    def test_no_match_visible(self):
        # pacote in sem regra alem da estatica de bloqueio
        r = mod.decide({"direction": "in", "proto": "udp", "port": 53},
                       self._rules())
        self.assertEqual(r["verdict"], "block")


if __name__ == "__main__":
    unittest.main()
