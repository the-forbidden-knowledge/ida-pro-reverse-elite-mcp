#!/usr/bin/env python3
"""Testes do lab 86 — hybrid-detect. Fixtures 100% sintéticas."""

import importlib.util
import os
import unittest

_AQUI = os.path.dirname(os.path.abspath(__file__))


def _carregar():
    spec = importlib.util.spec_from_file_location(
        "hybrid_detect", os.path.join(_AQUI, "rnuavamkn7bnfiiiymstvz.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = _carregar()


class TestHybridDetect(unittest.TestCase):
    def test_phonegap(self):
        r = mod.detectar(["assets/www/cordova.js", "AndroidManifest.xml"])
        self.assertEqual(r["framework"], "phonegap")
        self.assertIn("assets/www/cordova.js", r["evidencias"])

    def test_xamarin_por_dlls(self):
        r = mod.detectar(["assemblies/Mono.Android.dll", "assemblies/App.dll"])
        self.assertEqual(r["framework"], "xamarin")
        self.assertEqual(len(r["evidencias"]), 2)

    def test_xamarin_por_notice(self):
        r = mod.detectar(["NOTICE", "lib/arm64/libapp.so"])
        self.assertEqual(r["framework"], "xamarin")

    def test_nativo(self):
        r = mod.detectar(["lib/arm64/libapp.so", "AndroidManifest.xml"])
        self.assertEqual(r["framework"], "nativo")
        self.assertEqual(r["evidencias"], [])

    def test_ambos(self):
        r = mod.detectar(["assets/www/cordova.js", "assemblies/A.dll"])
        self.assertEqual(r["framework"], "phonegap+xamarin")

    def test_vazio(self):
        self.assertEqual(mod.detectar([])["framework"], "nativo")


if __name__ == "__main__":
    unittest.main()
