#!/usr/bin/env python3
"""Testes do lab 72 — dt-needed-recursive (fixtures sintéticas)."""

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
_mx_dt_needed_recursive = _loadmod("kybfpcmsxo3pv0rj3ap1s5.py")
naive_ldd, resolve_recursive, find_hidden, closure_report, main = _mx_dt_needed_recursive.naive_ldd, _mx_dt_needed_recursive.resolve_recursive, _mx_dt_needed_recursive.find_hidden, _mx_dt_needed_recursive.closure_report, _mx_dt_needed_recursive.main

# app -> liba, libb | liba -> libc | libb -> libc, libd | libc -> (ciclo) liba
DB = {
    "app": {"needed": ["liba.so", "libb.so"]},
    "liba.so": {"needed": ["libc.so"]},
    "libb.so": {"needed": ["libc.so", "libd.so"]},
    "libc.so": {"needed": ["liba.so"]},
    "libd.so": {"needed": []},
}


class TestNaive(unittest.TestCase):
    def test_diretas(self):
        self.assertEqual(naive_ldd(DB, "app"), ["liba.so", "libb.so"])

    def test_desconhecida(self):
        self.assertEqual(naive_ldd(DB, "fantasma"), [])


class TestRecursive(unittest.TestCase):
    def test_closure(self):
        r = resolve_recursive(DB, "app")
        self.assertEqual(set(r), {"liba.so", "libb.so", "libc.so", "libd.so"})

    def test_sem_ciclo_infinito(self):
        # libc -> liba fecha ciclo; não pode travar
        r = resolve_recursive(DB, "libc.so")
        self.assertIn("liba.so", r)

    def test_ldd_mente(self):
        rep = closure_report(DB, "app")
        self.assertIn("libc.so", rep["ldd_mente"])
        self.assertIn("libd.so", rep["ldd_mente"])


class TestHidden(unittest.TestCase):
    def test_ocultas(self):
        # libnss vista em runtime, fora da closure estática
        vistas = ["liba.so", "libnss_files.so.2"]
        self.assertEqual(find_hidden(DB, "app", vistas), ["libnss_files.so.2"])

    def test_sem_ocultas(self):
        self.assertEqual(find_hidden(DB, "app", ["liba.so"]), [])


class TestCLI(unittest.TestCase):
    def test_main(self):
        d = tempfile.mkdtemp()
        dbp = os.path.join(d, "db.json")
        rtp = os.path.join(d, "rt.json")
        out = os.path.join(d, "r.json")
        json.dump(DB, open(dbp, "w"))
        json.dump(["libnss_files.so.2"], open(rtp, "w"))
        self.assertEqual(main([dbp, "app", "--runtime", rtp, "-o", out]), 0)
        dados = json.load(open(out, encoding="utf-8"))
        self.assertEqual(dados["ocultas_runtime"], ["libnss_files.so.2"])
        self.assertEqual(len(dados["completas"]), 4)


if __name__ == "__main__":
    unittest.main()
