#!/usr/bin/env python3
"""Testes do lab 65 -- service-privs (fixtures sinteticas)."""
import importlib.util
import json
import os
import unittest

_AQUI = os.path.dirname(os.path.abspath(__file__))


def _load():
    spec = importlib.util.spec_from_file_location(
        "service_privs", os.path.join(_AQUI, "oijjin7mdsyham2yhaub87.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


mod = _load()


class TestServicePrivs(unittest.TestCase):
    def _svcs(self):
        with open(os.path.join(_AQUI, "services.json"), encoding="utf-8") as f:
            return json.load(f)

    def test_flags_dangerous(self):
        r = mod.inventory(self._svcs())
        self.assertIn("SeDebugPrivilege", r["LegadoSvc"]["dangerous"])
        self.assertEqual(r["LegadoSvc"]["risk"], "HIGH")

    def test_clean_service(self):
        r = mod.inventory(self._svcs())
        self.assertEqual(r["MeuAppSvc"]["dangerous"], [])
        self.assertEqual(r["MeuAppSvc"]["risk"], "LOW")

    def test_identity_kept(self):
        r = mod.inventory(self._svcs())
        self.assertEqual(r["Spooler"]["identity"], "LocalSystem")

    def test_diff_added(self):
        cur = self._svcs()
        base = {n: {"privileges": v["privileges"]} for n, v in cur.items()}
        base["LegadoSvc"] = {"privileges": ["SeBackupPrivilege"]}
        divs = mod.diff_vs_baseline(cur, base)
        added = [d for d in divs if d.get("added") == "SeDebugPrivilege"]
        self.assertEqual(len(added), 1)
        self.assertTrue(added[0]["dangerous"])
        self.assertEqual(added[0]["service"], "LegadoSvc")

    def test_diff_removed(self):
        base = {"MeuAppSvc": {"privileges": ["SeChangeNotifyPrivilege", "SeDebugPrivilege"]}}
        divs = mod.diff_vs_baseline(self._svcs(), base)
        rem = [d for d in divs if d.get("removed") == "SeDebugPrivilege"]
        self.assertEqual(len(rem), 1)


if __name__ == "__main__":
    unittest.main()
