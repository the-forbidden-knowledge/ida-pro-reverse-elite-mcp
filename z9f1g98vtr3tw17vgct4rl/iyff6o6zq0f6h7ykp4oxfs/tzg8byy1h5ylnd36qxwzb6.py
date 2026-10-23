#!/usr/bin/env python3
"""Testes do lab 70 -- credguard-report (fixtures sinteticas)."""
import importlib.util
import json
import os
import unittest

_AQUI = os.path.dirname(os.path.abspath(__file__))


def _load():
    spec = importlib.util.spec_from_file_location(
        "credguard_report", os.path.join(_AQUI, "tp2163rqzm4ifu04t7li9j.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


mod = _load()


class TestCredguardReport(unittest.TestCase):
    def _inp(self):
        with open(os.path.join(_AQUI, "inputs.json"), encoding="utf-8") as f:
            return json.load(f)

    def test_sections(self):
        r = mod.build(self._inp())["credguard_report"]
        for s in ("dpapi", "credhist", "lsa", "token", "wfp", "services",
                  "dpapi_system"):
            self.assertIn(s, r)

    def test_no_secret_values(self):
        r = json.dumps(mod.build(self._inp()))
        self.assertNotIn("Svc-Spooler", r)

    def test_lsa_names_only(self):
        r = mod.build(self._inp())["credguard_report"]["lsa"]
        self.assertEqual(r["service_secrets"], ["_SC_Spooler", "_SC_wuauserv"])

    def test_token_summary(self):
        r = mod.build(self._inp())["credguard_report"]["token"]
        self.assertEqual(r["exposure_score"], 12)
        self.assertEqual(r["dangerous"], ["SeDebugPrivilege"])

    def test_high_risk(self):
        r = mod.build(self._inp())["credguard_report"]["services"]
        self.assertEqual(r["high_risk"], ["LegadoSvc"])

    def test_partial_inputs(self):
        r = mod.build({"token": {"exposure_score": 0, "dangerous_enabled": []}})
        self.assertIn("token", r["credguard_report"])
        self.assertNotIn("dpapi", r["credguard_report"])

    def test_redact(self):
        self.assertEqual(mod.redact("abcdefghij123456"), "abcd***REDACTED***")
        self.assertEqual(mod.redact("abc"), "***REDACTED***")


if __name__ == "__main__":
    unittest.main()
