#!/usr/bin/env python3
"""Testes do lab 62 -- token-inventory (fixtures sinteticas)."""
import importlib.util
import json
import os
import unittest

_AQUI = os.path.dirname(os.path.abspath(__file__))


def _load():
    spec = importlib.util.spec_from_file_location(
        "token_inventory", os.path.join(_AQUI, "eu9xcsf5orwyctw14733bk.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


mod = _load()


class TestTokenInventory(unittest.TestCase):
    def _tok(self):
        with open(os.path.join(_AQUI, "token.json"), encoding="utf-8") as f:
            return json.load(f)

    def test_flags_debug(self):
        r = mod.inventory(self._tok())
        nomes = [f["privilege"] for f in r["dangerous_enabled"]]
        self.assertIn("SeDebugPrivilege", nomes)

    def test_disabled_not_flagged(self):
        r = mod.inventory(self._tok())
        nomes = [f["privilege"] for f in r["dangerous_enabled"]]
        self.assertNotIn("SeImpersonatePrivilege", nomes)

    def test_score(self):
        r = mod.inventory(self._tok())
        # enabled=10 (SeDebug) + disabled=2 (SeImpersonate) + resto 0
        self.assertEqual(r["exposure_score"], 12)

    def test_clean_token(self):
        r = mod.inventory({"user": "x", "integrity": "Low", "privileges": {}})
        self.assertEqual(r["dangerous_enabled"], [])
        self.assertEqual(r["exposure_score"], 0)

    def test_tcb_critical(self):
        r = mod.inventory({"user": "x", "privileges": {"SeTcbPrivilege": "enabled"}})
        self.assertEqual(len(r["dangerous_enabled"]), 1)
        self.assertEqual(r["exposure_score"], 10)


if __name__ == "__main__":
    unittest.main()
