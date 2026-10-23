#!/usr/bin/env python3
"""Testes do lab 90 — mobile-report. Fixtures 100% sintéticas."""

import importlib.util
import os
import unittest

_AQUI = os.path.dirname(os.path.abspath(__file__))


def _carregar():
    spec = importlib.util.spec_from_file_location(
        "mobile_report", os.path.join(_AQUI, "elhs2np1rvwj8m4u4bz9g2.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = _carregar()


class TestMobileReport(unittest.TestCase):
    def test_todas_as_secoes(self):
        r = mod.gerar(
            {
                "app": "com.x",
                "pipeline": {"assinado": True, "alinhado": True},
                "diff": {"fidelity_score": 90.0},
                "mobsf": {"score": 80, "nivel": "alto"},
                "hibrido": {"framework": "phonegap"},
                "vazamentos": [{}, {}],
            }
        )
        self.assertEqual(r["app"], "com.x")
        self.assertEqual(r["total_secoes"], 5)
        self.assertTrue(r["secoes"]["pipeline"]["assinado"])
        self.assertEqual(r["secoes"]["fidelidade"]["score"], 90.0)
        self.assertEqual(r["secoes"]["framework"], "phonegap")
        self.assertEqual(r["secoes"]["vazamentos_log"], 2)

    def test_secoes_ausentes_sao_puladas(self):
        r = mod.gerar({"pipeline": {"assinado": True, "alinhado": False}})
        self.assertEqual(r["total_secoes"], 1)
        self.assertNotIn("fidelidade", r["secoes"])

    def test_vazio(self):
        r = mod.gerar({})
        self.assertEqual(r["total_secoes"], 0)
        self.assertEqual(r["app"], "desconhecido")


if __name__ == "__main__":
    unittest.main()
