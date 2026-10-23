#!/usr/bin/env python3
"""Testes do lab 69 -- firewall-ids (fixtures sinteticas)."""
import importlib.util
import json
import os
import unittest

_AQUI = os.path.dirname(os.path.abspath(__file__))


def _load():
    spec = importlib.util.spec_from_file_location(
        "firewall_ids", os.path.join(_AQUI, "gyatz70xutuf9vpu18a0d5.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


mod = _load()


class TestFirewallIds(unittest.TestCase):
    def _ev(self):
        with open(os.path.join(_AQUI, "events.json"), encoding="utf-8") as f:
            return json.load(f)

    def test_graph(self):
        g = mod.parse_events(self._ev())
        self.assertEqual(len(g), 2)
        self.assertEqual(len(g["1234"]["connections"]), 1)
        self.assertEqual(len(g["1234"]["binds"]), 1)

    def test_unknown_id_ignored(self):
        g = mod.parse_events(self._ev())
        self.assertNotIn("1", g)

    def test_blocked(self):
        g = mod.parse_events(self._ev())
        self.assertEqual(g["5678"]["connections"][0]["kind"],
                         "blocked-connection")

    def test_l2_invisible(self):
        g = mod.parse_events(self._ev())
        inv = mod.l2_invisible(g)
        self.assertEqual(len(inv), 1)
        self.assertEqual(inv[0]["id"], 5153)
        self.assertEqual(inv[0]["process"], "C:\\App\\old.exe")

    def test_empty(self):
        self.assertEqual(mod.parse_events([]), {})


if __name__ == "__main__":
    unittest.main()
