#!/usr/bin/env python3
"""Testes do lab 79 — apk-pipeline. Fixtures 100% sintéticas."""

import importlib.util
import os
import unittest

_AQUI = os.path.dirname(os.path.abspath(__file__))


def _carregar():
    spec = importlib.util.spec_from_file_location(
        "apk_pipeline", os.path.join(_AQUI, "hcmrexjs2mjobmel3as2o5.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = _carregar()


def _pacote():
    return {
        "arquivos": {"smali/a.smali": "const v0, 1"},
        "manifest": {"pacote": "com.teste"},
    }


class TestApkPipeline(unittest.TestCase):
    def test_pipeline_completo(self):
        r = mod.pipeline(_pacote(), [("smali/a.smali", "const v0, 1", "const v0, 2")])
        self.assertTrue(r["assinado"])
        self.assertTrue(r["alinhado"])
        self.assertEqual(r["arquivos"]["smali/a.smali"], "const v0, 2")
        self.assertIn("META-INF/CERT.RSA", r["arquivos"])

    def test_ordem_errada_zipalign_antes_do_sign(self):
        with self.assertRaises(ValueError):
            mod.executar(_pacote(), ["decode", "build", "zipalign", "sign"])

    def test_sign_marca_assinado(self):
        r = mod.sign(mod.build(mod.decode(_pacote())), alias="minha")
        self.assertTrue(r["assinado"])
        self.assertFalse(r["alinhado"])
        self.assertIn("minha", r["arquivos"]["META-INF/CERT.RSA"])

    def test_etapa_desconhecida(self):
        with self.assertRaises(ValueError):
            mod.executar(_pacote(), ["decode", "fritar"])

    def test_decode_preserva_manifest(self):
        r = mod.decode(_pacote())
        self.assertEqual(r["manifest"]["pacote"], "com.teste")

    def test_patch_conta_aplicados(self):
        r = mod.patch_smali(
            mod.decode(_pacote()), [("smali/a.smali", "const v0, 1", "const v0, 9")]
        )
        self.assertEqual(r["patches_aplicados"], 1)


if __name__ == "__main__":
    unittest.main()
