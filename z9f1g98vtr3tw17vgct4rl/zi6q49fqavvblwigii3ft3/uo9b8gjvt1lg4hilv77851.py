#!/usr/bin/env python3
"""Testes do lab 75 — selinux-te (fixtures sintéticas)."""

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
_mx_selinux_te = _loadmod("tzgwbrbvp2ol9eocodc95r.py")
parse_context, parse_allow, parse_transition, build_matrix, check, aplicar_transicao, main = _mx_selinux_te.parse_context, _mx_selinux_te.parse_allow, _mx_selinux_te.parse_transition, _mx_selinux_te.build_matrix, _mx_selinux_te.check, _mx_selinux_te.aplicar_transicao, _mx_selinux_te.main

ALLOWS = [
    "allow httpd_t httpd_log_t:file { read write append };",
    "allow httpd_t http_port_t:tcp_socket { name_bind };",
]
TRANS = ["type_transition init_t httpd_exec_t:process httpd_t;"]


class TestContext(unittest.TestCase):
    def test_parse(self):
        c = parse_context("system_u:system_r:httpd_t:s0")
        self.assertEqual(c, {"user": "system_u", "role": "system_r",
                             "type": "httpd_t", "level": "s0"})

    def test_nivel_complexo(self):
        c = parse_context("u:r:app_t:s0-s1:c0.c5")
        self.assertEqual(c["level"], "s0-s1:c0.c5")

    def test_invalido(self):
        self.assertIsNone(parse_context("só-dois:campos"))
        self.assertIsNone(parse_context(""))


class TestAllow(unittest.TestCase):
    def test_parse(self):
        a = parse_allow(ALLOWS[0])
        self.assertEqual(a["src"], "httpd_t")
        self.assertEqual(a["tgt"], "httpd_log_t")
        self.assertEqual(a["class"], "file")
        self.assertEqual(a["perms"], ["append", "read", "write"])

    def test_invalida(self):
        self.assertIsNone(parse_allow("deny tudo;"))


class TestMatrix(unittest.TestCase):
    def test_check(self):
        m = build_matrix([parse_allow(a) for a in ALLOWS])
        self.assertTrue(check(m, "httpd_t", "httpd_log_t", "file", "read"))
        self.assertTrue(check(m, "httpd_t", "http_port_t", "tcp_socket", "name_bind"))
        # default deny
        self.assertFalse(check(m, "httpd_t", "httpd_log_t", "file", "execute"))
        self.assertFalse(check(m, "outro_t", "httpd_log_t", "file", "read"))


class TestTransicao(unittest.TestCase):
    def test_transicao(self):
        ts = [parse_transition(t) for t in TRANS]
        self.assertEqual(aplicar_transicao(ts, "init_t", "httpd_exec_t"), "httpd_t")

    def test_heranca(self):
        ts = [parse_transition(t) for t in TRANS]
        self.assertEqual(aplicar_transicao(ts, "init_t", "outro_exec_t"), "init_t")


class TestCLI(unittest.TestCase):
    def test_main(self):
        out = os.path.join(tempfile.mkdtemp(), "r.json")
        rc = main(["--ctx", "system_u:system_r:httpd_t:s0",
                   "--allow"] + ALLOWS +
                  ["--trans"] + TRANS +
                  ["--check", "httpd_t", "httpd_log_t", "file", "read",
                   "-o", out])
        self.assertEqual(rc, 0)
        dados = json.load(open(out, encoding="utf-8"))
        self.assertTrue(dados["check"]["permitido"])
        self.assertEqual(dados["regras"], 2)


if __name__ == "__main__":
    unittest.main()
