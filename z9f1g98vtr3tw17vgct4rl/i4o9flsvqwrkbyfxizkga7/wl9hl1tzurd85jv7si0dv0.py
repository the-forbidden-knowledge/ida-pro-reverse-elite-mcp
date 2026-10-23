#!/usr/bin/env python3
"""Testes do lab 77 — automount-trick (fixtures sintéticas)."""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import importlib.util as _ilu
import os as _os
def _loadmod(_fname):
    _sp = _ilu.spec_from_file_location("_m", _os.path.join(_os.path.dirname(__file__), _fname))
    _mm = _ilu.module_from_spec(_sp); _sp.loader.exec_module(_mm)
    return _mm
_mx_automount_trick = _loadmod("q2aejllffak1x7epz8zj1t.py")
parse_map, resolve, sandbox_for, main = _mx_automount_trick.parse_map, _mx_automount_trick.resolve, _mx_automount_trick.sandbox_for, _mx_automount_trick.main

MAPA = """\
# base compartilhada + dados por usuário
*   /       :/srv/jail/base \\
    /data   :/srv/jail/data/&
"""


class TestParse(unittest.TestCase):
    def test_entrada(self):
        ents = parse_map(MAPA)
        self.assertEqual(len(ents), 1)
        self.assertEqual(ents[0]["key"], "*")
        self.assertEqual(len(ents[0]["mounts"]), 2)

    def test_bind(self):
        ents = parse_map(MAPA)
        self.assertTrue(all(m["bind"] for m in ents[0]["mounts"]))


class TestResolve(unittest.TestCase):
    def test_macro(self):
        ents = parse_map(MAPA)
        r = resolve(ents[0], "ana")
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0]["source"], ":/srv/jail/base")
        self.assertEqual(r[1]["source"], ":/srv/jail/data/ana")

    def test_caveat(self):
        ents = parse_map(MAPA)
        r = resolve(ents[0], "ana")
        self.assertIn("bind não aceita", r[0]["caveat"])

    def test_chave_fixa(self):
        ents = parse_map("bob /data :/srv/data/bob\n")
        self.assertIsNone(resolve(ents[0], "ana"))
        self.assertIsNotNone(resolve(ents[0], "bob"))


class TestSandbox(unittest.TestCase):
    def test_layout(self):
        ents = parse_map(MAPA)
        s = sandbox_for(ents, "bia")
        self.assertEqual(s["key"], "bia")
        self.assertEqual(s["mounts"][1]["source"], ":/srv/jail/data/bia")

    def test_sem_casamento(self):
        s = sandbox_for([], "x")
        self.assertIn("erro", s)


class TestCLI(unittest.TestCase):
    def test_main(self):
        d = tempfile.mkdtemp()
        mp = os.path.join(d, "auto.map")
        out = os.path.join(d, "r.json")
        open(mp, "w").write(MAPA)
        self.assertEqual(main([mp, "ana", "-o", out]), 0)
        dados = json.load(open(out, encoding="utf-8"))
        self.assertEqual(dados["mounts"][1]["source"], ":/srv/jail/data/ana")


if __name__ == "__main__":
    unittest.main()
