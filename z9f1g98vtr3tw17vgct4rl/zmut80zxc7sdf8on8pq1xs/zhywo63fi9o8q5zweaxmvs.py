#!/usr/bin/env python3
"""Testes do lab 57 — swift-demangle (fixtures sintéticas, sem binários reais)."""

import json
import os
import subprocess
import sys
import unittest

import importlib.util as _ilu
import os as _os
def _loadmod(_fname):
    _sp = _ilu.spec_from_file_location("_m", _os.path.join(_os.path.dirname(__file__), _fname))
    _mm = _ilu.module_from_spec(_sp); _sp.loader.exec_module(_mm)
    return _mm
_mx_swift_demangle = _loadmod("mczo23tqrnvyzvrnozghm5.py")
demangle, is_swift_mangled, kind_of = _mx_swift_demangle.demangle, _mx_swift_demangle.is_swift_mangled, _mx_swift_demangle.kind_of


class TestDemangle(unittest.TestCase):
    def test_classe_plano(self):
        # _TtC4Nome6Classe -> Nome.Classe (exemplo do plano, com comprimentos válidos)
        self.assertEqual(demangle("_TtC4Nome6Classe"), "Nome.Classe")

    def test_classe_realista(self):
        self.assertEqual(demangle("_TtC13TipCalculator11AppDelegate"),
                         "TipCalculator.AppDelegate")
        self.assertEqual(demangle("_TtC4Nome6Classe"), "Nome.Classe")

    def test_struct(self):
        self.assertEqual(demangle("_TtV9MeuModulo11MinhaStruct"), "MeuModulo.MinhaStruct")

    def test_enum(self):
        self.assertEqual(demangle("_TtO4Base6Estado"), "Base.Estado")

    def test_protocolo(self):
        self.assertEqual(demangle("_TtP4Rede10SessaoProt"), "Rede.SessaoProt")

    def test_nao_mangled_passa_intacto(self):
        self.assertEqual(demangle("printf"), "printf")
        self.assertEqual(demangle("_OBJC_CLASS_$_NSObject"), "_OBJC_CLASS_$_NSObject")

    def test_truncado_passa_intacto(self):
        self.assertEqual(demangle("_TtC4Nome6Clas"), "_TtC4Nome6Clas")

    def test_kind_invalido(self):
        self.assertEqual(demangle("_TtX3Abc"), "_TtX3Abc")


class TestKindOf(unittest.TestCase):
    def test_kinds(self):
        self.assertEqual(kind_of("_TtC4Nome6Classe"), "classe")
        self.assertEqual(kind_of("_TtV9MeuModulo11MinhaStruct"), "struct")
        self.assertEqual(kind_of("_TtO4Base6Estado"), "enum")
        self.assertEqual(kind_of("_TtP4Rede10SessaoProt"), "protocolo")

    def test_none(self):
        self.assertIsNone(kind_of("printf"))


class TestIsSwiftMangled(unittest.TestCase):
    def test_true(self):
        self.assertTrue(is_swift_mangled("_TtC4Nome6Classe"))

    def test_false(self):
        self.assertFalse(is_swift_mangled("main"))


class TestCli(unittest.TestCase):
    def test_cli_json(self):
        r = subprocess.run(
            [sys.executable, os.path.join(os.path.dirname(__file__), "mczo23tqrnvyzvrnozghm5.py"),
             "_TtC4Nome6Classe", "--json"],
            capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)
        saida = json.loads(r.stdout)
        self.assertEqual(saida[0]["decodificado"], "Nome.Classe")
        self.assertEqual(saida[0]["kind"], "classe")


if __name__ == "__main__":
    unittest.main()
