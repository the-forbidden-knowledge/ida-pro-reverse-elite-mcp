#!/usr/bin/env python3
"""Testes do lab 74 — mknod-devices (fixtures sintéticas)."""

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
_mx_mknod_devices = _loadmod("m69fo3tbe5rm6xrmmzlmqm.py")
parse_ls_device, mknod_plan, devices_from_deps, main = _mx_mknod_devices.parse_ls_device, _mx_mknod_devices.mknod_plan, _mx_mknod_devices.devices_from_deps, _mx_mknod_devices.main

LS = """\
crw-rw-rw- 1 root root 1, 3 /dev/null
crw-rw-rw- 1 root root 1, 9 /dev/urandom
brw-rw---- 1 root disk 8, 0 /dev/sda
-rw-r--r-- 1 root root 1024 /etc/hosts
"""


class TestParse(unittest.TestCase):
    def test_char(self):
        d = parse_ls_device("crw-rw-rw- 1 root root 1, 3 /dev/null")
        self.assertEqual(d, {"path": "/dev/null", "tipo": "char",
                             "major": 1, "minor": 3})

    def test_block(self):
        d = parse_ls_device("brw-rw---- 1 root disk 8, 0 /dev/sda")
        self.assertEqual(d["tipo"], "block")
        self.assertEqual((d["major"], d["minor"]), (8, 0))

    def test_nao_device(self):
        self.assertIsNone(parse_ls_device("-rw-r--r-- 1 root root 5 x"))
        self.assertIsNone(parse_ls_device(""))


class TestPlan(unittest.TestCase):
    def test_comandos(self):
        devs = [{"path": "/dev/null", "tipo": "char", "major": 1, "minor": 3},
                {"path": "/dev/sda", "tipo": "block", "major": 8, "minor": 0}]
        self.assertEqual(mknod_plan(devs),
                         ["mknod dev/null c 1 3", "mknod dev/sda b 8 0"])


class TestDeps(unittest.TestCase):
    def test_filtro(self):
        deps = [{"tipo": "dispositivo", "caminho": "/dev/urandom"},
                {"tipo": "arquivo", "caminho": "/etc/hosts"}]
        self.assertEqual(devices_from_deps(deps), ["/dev/urandom"])


class TestCLI(unittest.TestCase):
    def test_ls(self):
        d = tempfile.mkdtemp()
        lsp = os.path.join(d, "ls.txt")
        out = os.path.join(d, "r.json")
        open(lsp, "w").write(LS)
        self.assertEqual(main(["--ls", lsp, "-o", out]), 0)
        dados = json.load(open(out, encoding="utf-8"))
        self.assertEqual(len(dados["devices"]), 3)
        self.assertEqual(len(dados["mknod"]), 3)

    def test_deps(self):
        d = tempfile.mkdtemp()
        depp = os.path.join(d, "deps.json")
        out = os.path.join(d, "r.json")
        json.dump({"dependencias": [{"tipo": "dispositivo",
                                     "caminho": "/dev/null"}]},
                  open(depp, "w"))
        self.assertEqual(main(["--deps", depp, "-o", out]), 0)
        dados = json.load(open(out, encoding="utf-8"))
        self.assertEqual(dados["devices"][0]["path"], "/dev/null")
        self.assertEqual(dados["mknod"], [])  # sem major/minor: só lista


if __name__ == "__main__":
    unittest.main()
