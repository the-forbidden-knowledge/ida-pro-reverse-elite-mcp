#!/usr/bin/env python3
"""Testes do lab 61 -- lsa-secrets (fixtures sinteticas)."""
import importlib.util
import os
import unittest

_AQUI = os.path.dirname(os.path.abspath(__file__))


def _load():
    spec = importlib.util.spec_from_file_location(
        "lsa_secrets", os.path.join(_AQUI, "rm6oa20yd5rkxrtzouiw7a.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


mod = _load()
HIVE = mod.load_hive(os.path.join(_AQUI, "hive.json"))


class TestLsaSecrets(unittest.TestCase):
    def test_list_all(self):
        self.assertEqual(len(mod.list_secrets(HIVE)), 5)

    def test_service_only(self):
        svcs = mod.service_secrets(HIVE)
        nomes = [n for n, _ in svcs]
        self.assertEqual(sorted(nomes), ["_SC_Spooler", "_SC_wuauserv"])

    def test_non_service_excluded(self):
        nomes = [n for n, _ in mod.service_secrets(HIVE)]
        self.assertNotIn("DefaultPassword", nomes)
        self.assertNotIn("DPAPI_SYSTEM", nomes)

    def test_redact_default(self):
        r = mod.report(HIVE)
        for s in r["service_secrets"]:
            self.assertEqual(s["value"], "***REDACTED***")

    def test_show_values(self):
        r = mod.report(HIVE, show_values=True)
        vals = {s["name"]: s["value"] for s in r["service_secrets"]}
        self.assertEqual(vals["_SC_Spooler"], "Svc-Spooler-9Xq2")

    def test_redact_keep(self):
        self.assertEqual(mod.redact("abcdef", keep=2), "ab***REDACTED***")
        self.assertEqual(mod.redact("ab", keep=4), "***REDACTED***")


if __name__ == "__main__":
    unittest.main()
