#!/usr/bin/env python3
"""Testes do lab 66 -- smb-dialect (fixtures sinteticas)."""
import importlib.util
import os
import unittest

_AQUI = os.path.dirname(os.path.abspath(__file__))


def _load():
    spec = importlib.util.spec_from_file_location(
        "smb_dialect", os.path.join(_AQUI, "v47hzheiv4imr0haykpjx6.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


mod = _load()


class TestSmbDialect(unittest.TestCase):
    def test_highest_common(self):
        self.assertEqual(mod.negotiate(["3.1.1", "3.0"], ["3.0", "2.1"]), "3.0")

    def test_no_common(self):
        self.assertIsNone(mod.negotiate(["3.1.1"], ["1.0"]))

    def test_ok(self):
        r = mod.detect_downgrade("3.1.1", "3.1.1", False)
        self.assertEqual(r["status"], "ok")
        self.assertFalse(r["suspicious"])

    def test_blind_spot(self):
        # caiu para 1.0 sem Event 1005 = ponto cego
        r = mod.detect_downgrade("3.0", "1.0", False)
        self.assertEqual(r["status"], "downgrade-blind-spot")
        self.assertTrue(r["suspicious"])

    def test_detected_downgrade(self):
        r = mod.detect_downgrade("3.0", "2.1", True)
        self.assertEqual(r["status"], "downgrade-detected")
        self.assertFalse(r["suspicious"])

    def test_undetected_downgrade(self):
        r = mod.detect_downgrade("3.0", "2.0", False)
        self.assertEqual(r["status"], "downgrade-undetected")
        self.assertTrue(r["suspicious"])


if __name__ == "__main__":
    unittest.main()
