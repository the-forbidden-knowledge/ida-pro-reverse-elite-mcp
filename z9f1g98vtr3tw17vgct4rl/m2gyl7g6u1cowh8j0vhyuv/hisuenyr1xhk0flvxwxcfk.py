#!/usr/bin/env python3
"""Testes do lab 60 -- credhist-unwind (fixtures sinteticas)."""
import hashlib
import importlib.util
import os
import unittest

_AQUI = os.path.dirname(os.path.abspath(__file__))


def _load():
    spec = importlib.util.spec_from_file_location(
        "credhist_unwind", os.path.join(_AQUI, "g1uwz0q4weipm3zzuczrld.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


mod = _load()


class TestCredhist(unittest.TestCase):
    def test_unwind_full(self):
        pws = ["senha-antiga-1", "senha-antiga-2", "senha-atual"]
        entries = mod.build_chain(pws)
        rec = mod.unwind(pws[-1], entries)
        self.assertEqual(len(rec), 2)
        self.assertEqual(rec[0], hashlib.sha512(pws[1].encode()).hexdigest())
        self.assertEqual(rec[1], hashlib.sha512(pws[0].encode()).hexdigest())

    def test_single_previous(self):
        entries = mod.build_chain(["velha", "nova"])
        rec = mod.unwind("nova", entries)
        self.assertEqual(rec, [hashlib.sha512(b"velha").hexdigest()])

    def test_wrong_current_password(self):
        entries = mod.build_chain(["velha", "nova"])
        with self.assertRaises(ValueError):
            mod.unwind("outra", entries)

    def test_tampered_entry(self):
        entries = mod.build_chain(["velha", "nova"])
        entries[0]["blob"] = "00" + entries[0]["blob"][2:]
        with self.assertRaises(ValueError):
            mod.unwind("nova", entries)

    def test_chain_length(self):
        pws = [f"pw{i}" for i in range(6)]
        entries = mod.build_chain(pws)
        self.assertEqual(len(entries), 5)
        rec = mod.unwind(pws[-1], entries)
        self.assertEqual(len(rec), 5)


if __name__ == "__main__":
    unittest.main()
