#!/usr/bin/env python3
"""Testes do lab 63 -- wfp-snapshot (fixtures sinteticas)."""
import importlib.util
import json
import os
import unittest

_AQUI = os.path.dirname(os.path.abspath(__file__))


def _load():
    spec = importlib.util.spec_from_file_location(
        "wfp_snapshot", os.path.join(_AQUI, "q0ybcbyxly0g42ykdg24jo.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


mod = _load()


class TestWfpSnapshot(unittest.TestCase):
    def _st(self):
        with open(os.path.join(_AQUI, "fwstate.json"), encoding="utf-8") as f:
            return json.load(f)

    def test_all_stores(self):
        s = mod.snapshot(self._st())
        self.assertEqual(set(s["stores"]), set(mod.STORES))

    def test_hidden_present(self):
        s = mod.snapshot(self._st())
        self.assertIn("StaticServiceStore", s["hidden_stores_present"])
        self.assertEqual(len(s["stores"]["StaticServiceStore"]), 2)

    def test_total(self):
        s = mod.snapshot(self._st())
        self.assertEqual(s["total_rules"], 6)

    def test_active_store_bug(self):
        s = mod.snapshot(self._st())
        # ActiveStore = Persistent(2) + RSOP(1) = 3, IGNORA os ocultos (2+1)
        self.assertEqual(s["active_store_rule_count"], 3)
        self.assertLess(s["active_store_rule_count"], s["total_rules"])
        self.assertIn("bug", s["warning"])

    def test_rule_sources(self):
        src = mod.rule_sources(self._st())
        self.assertEqual(src["WSH-EventLog-In"], "StaticServiceStore")
        self.assertEqual(src["GPO-Block-Telnet"], "RSOP")
        self.assertEqual(src["Allow-Web-Out"], "PersistentStore")


if __name__ == "__main__":
    unittest.main()
