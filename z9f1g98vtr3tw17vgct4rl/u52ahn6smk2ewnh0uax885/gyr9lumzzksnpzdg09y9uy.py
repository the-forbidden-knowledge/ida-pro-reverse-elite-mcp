#!/usr/bin/env python3
"""Testes sinteticos para 55kzhelx13j4h96x9xtxb0.py (rastreio inventado, sem binarios reais)."""

import json
import subprocess
import sys
import tempfile
import unittest

import importlib.util as _ilu
import os as _os
def _loadmod(_fname):
    _sp = _ilu.spec_from_file_location("_m", _os.path.join(_os.path.dirname(__file__), _fname))
    _mm = _ilu.module_from_spec(_sp)
    _sp.loader.exec_module(_mm)
    return _mm
dataflow_trace = _loadmod("55kzhelx13j4h96x9xtxb0.py")


def make_records():
    """Cadeia sintetizada: senha -> hash -> cmp -> flag -> global."""
    return [
        {"addr": 0x1000, "op": "assign", "target": "senha", "value": "input"},
        {"addr": 0x1010, "op": "write", "target": "hash", "value": "senha"},
        {"addr": 0x1020, "op": "compare", "target": "hash", "value": "esperado"},
        {"addr": 0x1030, "op": "assign", "target": "flag", "value": "hash"},
        {"addr": 0x1040, "op": "write", "target": "global", "value": "flag"},
        {"addr": 0x1050, "op": "write", "target": "outro", "value": "const"},  # ruído
    ]


class TestDataflowTrace(unittest.TestCase):
    def test_cadeia_completa(self):
        chain = dataflow_trace.trace(make_records(), 0x1040)["chain"]
        addrs = [r["addr"] for r in chain]
        self.assertEqual(addrs, [0x1000, 0x1010, 0x1020, 0x1030, 0x1040])

    def test_exclui_ruido(self):
        chain = dataflow_trace.trace(make_records(), 0x1040)["chain"]
        self.assertNotIn(0x1050, [r["addr"] for r in chain])

    def test_formato_da_saida(self):
        chain = dataflow_trace.trace(make_records(), 0x1040)["chain"]
        for item in chain:
            self.assertEqual(set(item.keys()), {"addr", "op", "detail"})
        self.assertEqual(chain[0]["op"], "assign")
        self.assertEqual(chain[-1]["op"], "write")

    def test_alvo_inexistente(self):
        self.assertEqual(dataflow_trace.trace(make_records(), 0x9999),
                         {"chain": []})

    def test_origem_unica(self):
        recs = [{"addr": 0x1000, "op": "write", "target": "g", "value": "1"}]
        chain = dataflow_trace.trace(recs, 0x1000)["chain"]
        self.assertEqual([r["addr"] for r in chain], [0x1000])

    def test_cli_end_to_end(self):
        payload = {"writes": make_records(), "reads": []}
        with tempfile.NamedTemporaryFile("w", suffix=".json",
                                         delete=False) as fh:
            json.dump(payload, fh)
            path = fh.name
        proc = subprocess.run([sys.executable, "55kzhelx13j4h96x9xtxb0.py", path,
                               "--target", "0x1040"],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        chain = json.loads(proc.stdout)["chain"]
        self.assertEqual(len(chain), 5)
        self.assertEqual(chain[-1]["detail"], "global <- flag")


if __name__ == "__main__":
    unittest.main()
