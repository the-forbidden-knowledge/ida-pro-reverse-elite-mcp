"""Testes do lab 09 — xref-trace.

Fixtures: grafo de chamadas sintético em JSON, gerado no próprio teste.
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
xref_trace = _loadmod("ll91zo7q1yljfftnf60qws.py")

EXPORT = {
    "functions": [
        {"name": "main", "calls": ["init", "run"]},
        {"name": "init", "calls": []},
        {"name": "run", "calls": ["CreateFileW", "WriteFile"]},
        {"name": "helper", "calls": ["CreateFileW"]},
    ]
}


class TestXrefTrace(unittest.TestCase):
    def _temp(self, obj):
        fd, caminho = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f)
        self.addCleanup(os.unlink, caminho)
        return caminho

    def test_cadeias(self):
        r = xref_trace.trace("CreateFileW", EXPORT["functions"])
        self.assertEqual(r["alvo"], "CreateFileW")
        cadeias = sorted(r["cadeias"])
        self.assertEqual(
            cadeias,
            [["helper", "CreateFileW"], ["main", "run", "CreateFileW"]],
        )

    def test_cadeia_unica(self):
        r = xref_trace.trace("WriteFile", EXPORT["functions"])
        self.assertEqual(r["cadeias"], [["main", "run", "WriteFile"]])

    def test_alvo_inexistente(self):
        r = xref_trace.trace("APIInexistente", EXPORT["functions"])
        self.assertEqual(r["cadeias"], [])

    def test_sem_ciclo_infinito(self):
        funcs = [
            {"name": "a", "calls": ["b"]},
            {"name": "b", "calls": ["a", "Alvo"]},
        ]
        r = xref_trace.trace("Alvo", funcs)
        # 'a' e 'b' se chamam: nenhuma é raiz -> sem cadeias, mas sem travar
        self.assertEqual(r["cadeias"], [])

    def test_cli(self):
        caminho = self._temp(EXPORT)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            codigo = xref_trace.main([caminho, "--api", "CreateFileW"])
        self.assertEqual(codigo, 0)
        r = json.loads(buf.getvalue())
        self.assertEqual(len(r["cadeias"]), 2)


if __name__ == "__main__":
    unittest.main()
