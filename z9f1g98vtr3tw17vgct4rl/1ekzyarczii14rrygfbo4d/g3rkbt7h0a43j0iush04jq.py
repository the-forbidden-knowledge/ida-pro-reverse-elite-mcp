#!/usr/bin/env python3
"""Testes do lab 58 — capability-inventory (fixtures sintéticas)."""

import json
import os
import subprocess
import sys
import tempfile
import unittest

import importlib.util as _ilu
import os as _os
def _loadmod(_fname):
    _sp = _ilu.spec_from_file_location("_m", _os.path.join(_os.path.dirname(__file__), _fname))
    _mm = _ilu.module_from_spec(_sp); _sp.loader.exec_module(_mm)
    return _mm
_mx_capability_inventory = _loadmod("ysustmo0hgjfqz9lj1uzsx.py")
inventory, summarize = _mx_capability_inventory.inventory, _mx_capability_inventory.summarize


class TestInventory(unittest.TestCase):
    def test_ios(self):
        inv = inventory(["CFNetwork", "CoreLocation", "Security"])
        self.assertEqual(inv["CFNetwork"], ["rede"])
        self.assertEqual(inv["CoreLocation"], ["localizacao"])
        self.assertEqual(inv["Security"], ["cripto"])

    def test_windows(self):
        inv = inventory(["wininet.dll", "crypt32.dll"])
        self.assertEqual(inv["wininet.dll"], ["rede"])
        self.assertEqual(inv["crypt32.dll"], ["cripto"])

    def test_caminho_framework(self):
        inv = inventory(["/System/Library/Frameworks/CFNetwork.framework/CFNetwork"])
        self.assertEqual(inv["/System/Library/Frameworks/CFNetwork.framework/CFNetwork"],
                         ["rede"])

    def test_desconhecida(self):
        self.assertEqual(inventory(["BibliotecaX"])["BibliotecaX"], ["desconhecida"])

    def test_vazia(self):
        self.assertEqual(inventory([]), {})


class TestSummarize(unittest.TestCase):
    def test_contagem(self):
        resumo = summarize(inventory(["CFNetwork", "CoreLocation", "AVFoundation"]))
        self.assertEqual(resumo["por_capacidade"]["rede"], 1)
        self.assertEqual(resumo["total_itens"], 3)

    def test_escore_sobe_com_sensiveis(self):
        baixo = summarize(inventory(["CFNetwork"]))["escore_exposicao"]
        alto = summarize(inventory(["CoreLocation", "AVFoundation"]))["escore_exposicao"]
        self.assertGreater(alto, baixo)

    def test_escore_teto(self):
        itens = ["CoreLocation", "AVFoundation", "Contacts", "HealthKit",
                 "CoreBluetooth", "CoreNFC"]
        self.assertLessEqual(summarize(inventory(itens))["escore_exposicao"], 100)


class TestCli(unittest.TestCase):
    def test_cli(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w",
                                         encoding="utf-8") as f:
            json.dump(["CFNetwork", "Security"], f)
            caminho = f.name
        try:
            r = subprocess.run(
                [sys.executable,
                 os.path.join(os.path.dirname(__file__), "ysustmo0hgjfqz9lj1uzsx.py"),
                 caminho],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 0)
            saida = json.loads(r.stdout)
            self.assertEqual(saida["inventario"]["CFNetwork"], ["rede"])
        finally:
            os.unlink(caminho)


if __name__ == "__main__":
    unittest.main()
