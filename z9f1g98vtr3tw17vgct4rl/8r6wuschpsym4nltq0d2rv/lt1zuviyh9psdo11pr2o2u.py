#!/usr/bin/env python3
"""Testes do lab 71 — strace-oracle (fixtures sintéticas, sem binários reais)."""

import json
import os
import subprocess
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
_mx_strace_oracle = _loadmod("lnm973nenrih4q4wl7l0xm.py")
parse_strace, enoents_fatais, classificar, oraculo_dependencias, main = _mx_strace_oracle.parse_strace, _mx_strace_oracle.enoents_fatais, _mx_strace_oracle.classificar, _mx_strace_oracle.oraculo_dependencias, _mx_strace_oracle.main

LOG = """\
1234 openat(AT_FDCWD, "/etc/app/config.ini", O_RDONLY) = -1 ENOENT (No such file or directory)
1234 openat(AT_FDCWD, "/usr/lib/libaux.so.1", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
1234 openat(AT_FDCWD, "/dev/tpm0", O_RDWR) = -1 ENOENT (No such file or directory)
1234 execve("/usr/bin/helper", ["helper"], 0x7ffd) = -1 ENOENT (No such file or directory)
1234 openat(AT_FDCWD, "/lib/x86_64-linux-gnu/libc.so.6", O_RDONLY|O_CLOEXEC) = 3
1234 exit_group(1)                           = ?
1234 +++ exited with 1 +++
"""


class TestParse(unittest.TestCase):
    def test_eventos(self):
        evs = parse_strace(LOG)
        calls = [e for e in evs if e["tipo"] == "call"]
        self.assertEqual(len(calls), 5)
        self.assertEqual(calls[0]["syscall"], "openat")
        self.assertEqual(calls[0]["caminho"], "/etc/app/config.ini")
        self.assertEqual(calls[0]["errno"], "ENOENT")

    def test_exit(self):
        evs = parse_strace(LOG)
        self.assertTrue(any(e["tipo"] == "exit" for e in evs))


class TestFatais(unittest.TestCase):
    def test_ultimo_enoent(self):
        evs = parse_strace(LOG)
        fatais = enoents_fatais(evs)
        self.assertEqual(len(fatais), 4)
        # o último ENOENT antes do exit é o execve do helper
        self.assertEqual(fatais[-1]["syscall"], "execve")

    def test_janela(self):
        evs = parse_strace(LOG)
        fatais = enoents_fatais(evs, janela=3)
        self.assertEqual(len(fatais), 2)


class TestClassificar(unittest.TestCase):
    def test_tipos(self):
        casos = [
            ({"syscall": "execve", "caminho": "/usr/bin/x"}, "binario"),
            ({"syscall": "openat", "caminho": "/dev/null"}, "dispositivo"),
            ({"syscall": "openat", "caminho": "/lib/liba.so.2"}, "biblioteca"),
            ({"syscall": "openat", "caminho": "/etc/hosts"}, "arquivo"),
        ]
        for ev, esperado in casos:
            self.assertEqual(classificar(ev)["tipo"], esperado)


class TestOraculo(unittest.TestCase):
    def test_pipeline(self):
        r = oraculo_dependencias(LOG)
        self.assertEqual(len(r["dependencias"]), 4)
        tipos = {d["tipo"] for d in r["dependencias"]}
        self.assertEqual(tipos, {"arquivo", "biblioteca", "dispositivo", "binario"})
        self.assertEqual(r["fatal"]["caminho"], "/usr/bin/helper")

    def test_sem_enoent(self):
        r = oraculo_dependencias('1234 exit_group(0) = ?\n')
        self.assertEqual(r["dependencias"], [])
        self.assertIsNone(r["fatal"])


class TestCLI(unittest.TestCase):
    def test_main_json(self):
        with tempfile.NamedTemporaryFile("w", suffix=".log", delete=False) as f:
            f.write(LOG)
            path = f.name
        try:
            out = os.path.join(tempfile.mkdtemp(), "r.json")
            self.assertEqual(main([path, "-o", out]), 0)
            dados = json.load(open(out, encoding="utf-8"))
            self.assertEqual(len(dados["dependencias"]), 4)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
