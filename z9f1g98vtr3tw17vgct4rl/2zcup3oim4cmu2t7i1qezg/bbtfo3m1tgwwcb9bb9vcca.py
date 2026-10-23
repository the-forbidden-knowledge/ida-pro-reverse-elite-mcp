#!/usr/bin/env python3
"""Testes do lab 78 — dnssec-hierarchy (fixtures sintéticas)."""

import json
import os
import sys
import tempfile
import unittest
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import importlib.util as _ilu
import os as _os
def _loadmod(_fname):
    _sp = _ilu.spec_from_file_location("_m", _os.path.join(_os.path.dirname(__file__), _fname))
    _mm = _ilu.module_from_spec(_sp); _sp.loader.exec_module(_mm)
    return _mm
_mx_dnssec_hierarchy = _loadmod("nptdjvu6nwtk7gma9r7pcb.py")
nova_chave, rollover, assinar, verificar, atestar_clone, main = _mx_dnssec_hierarchy.nova_chave, _mx_dnssec_hierarchy.rollover, _mx_dnssec_hierarchy.assinar, _mx_dnssec_hierarchy.verificar, _mx_dnssec_hierarchy.atestar_clone, _mx_dnssec_hierarchy.main

HOJE = date(2026, 10, 23)


def par():
    c1, c2 = nova_chave("ZSK", "zsk-1", HOJE), nova_chave("ZSK", "zsk-2", HOJE)
    c1["state"] = "curr"
    return [c1, c2]


class TestRollover(unittest.TestCase):
    def test_ciclo(self):
        chaves = rollover(par(), HOJE, "zsk-3")
        estados = {c["id"]: c["state"] for c in chaves}
        self.assertEqual(estados, {"zsk-1": "old", "zsk-2": "curr",
                                   "zsk-3": "next"})

    def test_old_expirada_descartada(self):
        velha = nova_chave("ZSK", "zsk-0", HOJE - timedelta(days=60))
        velha["state"] = "curr"
        chaves = rollover([velha] + par(), HOJE, "zsk-9")
        ids = {c["id"] for c in chaves}
        self.assertNotIn("zsk-0", ids)


class TestAssinatura(unittest.TestCase):
    def test_assina_verifica(self):
        c = par()[0]
        sig = assinar(c, "abc123")
        self.assertTrue(verificar(c, "abc123", sig))
        self.assertFalse(verificar(c, "outro", sig))

    def test_so_curr_assina(self):
        with self.assertRaises(ValueError):
            assinar(par()[1], "x")


class TestAtestacao(unittest.TestCase):
    def test_atestado(self):
        r = atestar_clone(par(), "sha-do-clone", HOJE)
        self.assertEqual(r["veredito"], "ATESTADO")
        self.assertEqual(r["assinatura"]["key_id"], "zsk-1")

    def test_expirada(self):
        velhas = [dict(c, criada=(HOJE - timedelta(days=60)).isoformat())
                  for c in par()]
        r = atestar_clone(velhas, "sha", HOJE)
        self.assertIn("erro", r)


class TestCLI(unittest.TestCase):
    def test_fluxo(self):
        d = tempfile.mkdtemp()
        k1 = os.path.join(d, "k1.json")
        k2 = os.path.join(d, "k2.json")
        self.assertEqual(main(["init", "--hoje", "2026-10-23", "-o", k1]), 0)
        self.assertEqual(main(["rollover", k1, "--proxima", "zsk-3",
                               "--hoje", "2026-10-23", "-o", k2]), 0)
        dados = json.load(open(k2, encoding="utf-8"))
        estados = {c["id"]: c["state"] for c in dados["chaves"]}
        self.assertEqual(estados["zsk-2"], "curr")


if __name__ == "__main__":
    unittest.main()
