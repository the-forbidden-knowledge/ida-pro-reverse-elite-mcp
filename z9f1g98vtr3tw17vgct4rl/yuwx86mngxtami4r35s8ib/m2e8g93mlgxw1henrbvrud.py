#!/usr/bin/env python3
"""Testes do lab 87 — mobsf-score. Fixtures 100% sintéticas."""

import importlib.util
import os
import unittest

_AQUI = os.path.dirname(os.path.abspath(__file__))


def _carregar():
    spec = importlib.util.spec_from_file_location(
        "mobsf_score", os.path.join(_AQUI, "nshk5uee4n2m3m6cwh30de.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = _carregar()


class TestMobsfScore(unittest.TestCase):
    def test_app_limpo_score_100(self):
        r = mod.pontuar({"permissoes": ["INTERNET"], "atividades": [], "apis": []})
        self.assertEqual(r["score"], 100)
        self.assertEqual(r["nivel"], "alto")
        self.assertEqual(r["achados"], [])

    def test_permissao_perigosa_desconta(self):
        r = mod.pontuar({"permissoes": ["READ_SMS"], "atividades": [], "apis": []})
        self.assertEqual(r["score"], 92)
        self.assertEqual(r["achados"][0]["tipo"], "permissao-perigosa")

    def test_atividade_exportada_sem_permissao(self):
        r = mod.pontuar(
            {
                "permissoes": [],
                "atividades": [{"nome": "X", "exportada": True, "permissao": ""}],
                "apis": [],
            }
        )
        self.assertEqual(r["score"], 90)

    def test_atividade_exportada_com_permissao_ok(self):
        r = mod.pontuar(
            {
                "permissoes": [],
                "atividades": [{"nome": "X", "exportada": True, "permissao": "P"}],
                "apis": [],
            }
        )
        self.assertEqual(r["score"], 100)

    def test_api_arriscada(self):
        r = mod.pontuar({"permissoes": [], "atividades": [], "apis": ["Runtime.exec"]})
        self.assertEqual(r["score"], 95)

    def test_piso_zero(self):
        r = mod.pontuar(
            {"permissoes": ["READ_SMS"] * 20, "atividades": [], "apis": []}
        )
        self.assertEqual(r["score"], 0)
        self.assertEqual(r["nivel"], "baixo")


if __name__ == "__main__":
    unittest.main()
