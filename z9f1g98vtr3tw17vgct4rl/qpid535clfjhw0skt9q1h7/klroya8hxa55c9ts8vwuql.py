#!/usr/bin/env python3
"""Testes do lab 73 — chroot-jail (fixtures sintéticas, /tmp apenas)."""

import json
import os
import stat
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
_mx_chroot_jail = _loadmod("wj6z64cyfoaykrbwpmn9pd.py")
plan_jail, build_jail, verify_jail, main = _mx_chroot_jail.plan_jail, _mx_chroot_jail.build_jail, _mx_chroot_jail.verify_jail, _mx_chroot_jail.main

DEPS = [
    {"tipo": "biblioteca", "caminho": "/lib/x86_64/libc.so.6"},
    {"tipo": "arquivo", "caminho": "/etc/app/config.ini"},
    {"tipo": "dispositivo", "caminho": "/dev/null"},
]


class TestPlan(unittest.TestCase):
    def test_modos(self):
        m = plan_jail(DEPS)
        por_path = {i["path"]: i for i in m}
        self.assertEqual(por_path["lib/x86_64/libc.so.6"]["mode"], "0o555")
        self.assertEqual(por_path["etc/app/config.ini"]["mode"], "0o444")
        self.assertEqual(por_path["lib"]["mode"], "0o111")

    def test_shadow_banido(self):
        m = plan_jail([{"tipo": "arquivo", "caminho": "/etc/shadow"}])
        self.assertEqual(m, [])

    def test_traversal_banido(self):
        m = plan_jail([{"tipo": "arquivo", "caminho": "/etc/../x"}])
        for i in m:
            self.assertNotIn("..", i["path"])


class TestBuild(unittest.TestCase):
    def test_monta_e_verifica(self):
        raiz = tempfile.mkdtemp()
        m = plan_jail(DEPS)
        build_jail(raiz, m)
        self.assertEqual(verify_jail(raiz, m), [])
        modo = stat.S_IMODE(os.lstat(os.path.join(raiz, "lib")).st_mode)
        self.assertEqual(modo, 0o111)

    def test_detecta_problema(self):
        raiz = tempfile.mkdtemp()
        m = plan_jail(DEPS)
        probs = verify_jail(raiz, m)  # sem build: tudo ausente
        self.assertTrue(all(p["erro"] == "ausente" for p in probs))
        self.assertEqual(len(probs), len(m))


class TestCLI(unittest.TestCase):
    def test_main(self):
        d = tempfile.mkdtemp()
        depp = os.path.join(d, "deps.json")
        json.dump(DEPS, open(depp, "w"))
        destino = os.path.join(d, "jail")
        self.assertEqual(main([depp, destino]), 0)
        self.assertTrue(os.path.isdir(os.path.join(destino, "lib")))


if __name__ == "__main__":
    unittest.main()
