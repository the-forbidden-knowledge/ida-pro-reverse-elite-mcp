"""Testes do lab 10 — strings-navigate.

Fixtures: exportação sintética com funções (addr/size) e strings com
xrefs, gerada no próprio teste.
"""

import contextlib
import io
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
    _mm = _ilu.module_from_spec(_sp)
    _sp.loader.exec_module(_mm)
    return _mm
strings_navigate = _loadmod("i3kcp6jz9krnhnzl52k04y.py")

EXPORT = {
    "functions": [
        {"name": "main", "addr": 0x401000, "size": 0x80},
        {"name": "decrypt", "addr": 0x401080, "size": 0x60},
        {"name": "send", "addr": 0x4010E0, "size": 0x40},
    ],
    "strings": [
        {"text": "cmd.exe", "addr": 0x402000, "xrefs": [0x401010, 0x4010E8]},
        {"text": "ok", "addr": 0x402010, "xrefs": [0x401090]},
    ],
}


class TestStringsNavigate(unittest.TestCase):
    def _temp(self, obj):
        fd, caminho = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f)
        self.addCleanup(os.unlink, caminho)
        return caminho

    def test_usos(self):
        r = strings_navigate.navigate("cmd.exe", EXPORT)
        self.assertEqual(r["string"], "cmd.exe")
        usos = sorted(r["usos"], key=lambda u: u["via"])
        self.assertEqual(len(usos), 2)
        self.assertEqual(usos[0]["funcao"], "main")
        self.assertEqual(usos[0]["via"], "0x401010")
        self.assertEqual(usos[1]["funcao"], "send")
        self.assertEqual(usos[1]["via"], "0x4010E8")

    def test_string_unica(self):
        r = strings_navigate.navigate("ok", EXPORT)
        self.assertEqual(len(r["usos"]), 1)
        self.assertEqual(r["usos"][0]["funcao"], "decrypt")

    def test_string_inexistente(self):
        r = strings_navigate.navigate("nao existe", EXPORT)
        self.assertEqual(r["usos"], [])

    def test_cli(self):
        caminho = self._temp(EXPORT)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            codigo = strings_navigate.main([caminho, "--string", "cmd.exe"])
        self.assertEqual(codigo, 0)
        r = json.loads(buf.getvalue())
        self.assertEqual(len(r["usos"]), 2)


if __name__ == "__main__":
    unittest.main()
