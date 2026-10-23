#!/usr/bin/env python3
"""Testes do lab 56 — class-dump (fixtures sintéticas, sem binários reais)."""

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
_mx_class_dump = _loadmod("t1ac14y2dxg1x1w3cgjy5f.py")
dump_all, dump_class, dump_ivar, dump_method = _mx_class_dump.dump_all, _mx_class_dump.dump_class, _mx_class_dump.dump_ivar, _mx_class_dump.dump_method


def classe_exemplo() -> dict:
    return {
        "nome": "LoginDescriptor",
        "superclasse": "NSObject",
        "protocolos": ["NSCoding"],
        "ivars": [
            {"nome": "token", "tipo": "NSString"},
            {"nome": "idade", "tipo": "int"},
        ],
        "metodos": [
            {"nome": "autenticar", "kind": "instancia", "retorno": "BOOL",
             "partes": [{"rotulo": "autenticar", "tipo": "NSString", "nome": "usuario"}]},
            {"nome": "versao", "kind": "classe", "retorno": "NSString", "partes": []},
        ],
    }


class TestDumpIvar(unittest.TestCase):
    def test_ponteiro(self):
        self.assertEqual(dump_ivar({"nome": "token", "tipo": "NSString"}),
                         "    NSString * _token;")

    def test_tipo_simples(self):
        self.assertEqual(dump_ivar({"nome": "x", "tipo": "int"}), "    int * _x;")


class TestDumpMethod(unittest.TestCase):
    def test_sem_argumentos(self):
        self.assertEqual(
            dump_method({"nome": "versao", "kind": "classe", "retorno": "NSString", "partes": []}),
            "+ (NSString)versao;")

    def test_com_argumento(self):
        decl = dump_method({"nome": "autenticar", "kind": "instancia", "retorno": "BOOL",
                            "partes": [{"rotulo": "autenticar", "tipo": "NSString", "nome": "usuario"}]})
        self.assertEqual(decl, "- (BOOL)autenticar:(NSString)usuario;")


class TestDumpClass(unittest.TestCase):
    def test_estrutura(self):
        saida = dump_class(classe_exemplo())
        self.assertIn("@interface LoginDescriptor : NSObject <NSCoding>", saida)
        self.assertIn("NSString * _token;", saida)
        self.assertIn("- (BOOL)autenticar:(NSString)usuario;", saida)
        self.assertIn("+ (NSString)versao;", saida)
        self.assertTrue(saida.rstrip().endswith("@end"))

    def test_sem_protocolo(self):
        saida = dump_class({"nome": "A", "metodos": []})
        self.assertIn("@interface A : NSObject", saida)
        self.assertNotIn("<", saida.split("\n")[0])

    def test_dump_all(self):
        saida = dump_all([classe_exemplo(), {"nome": "B", "metodos": []}])
        self.assertEqual(saida.count("@interface"), 2)
        self.assertEqual(saida.count("@end"), 2)


class TestCli(unittest.TestCase):
    def test_cli(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w",
                                         encoding="utf-8") as f:
            json.dump([classe_exemplo()], f)
            caminho = f.name
        try:
            r = subprocess.run(
                [sys.executable, os.path.join(os.path.dirname(__file__), "t1ac14y2dxg1x1w3cgjy5f.py"),
                 caminho],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 0)
            self.assertIn("@interface LoginDescriptor", r.stdout)
        finally:
            os.unlink(caminho)


if __name__ == "__main__":
    unittest.main()
