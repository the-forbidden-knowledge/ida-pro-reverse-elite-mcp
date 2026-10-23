#!/usr/bin/env python3
"""Testes sinteticos para i72bqacdxje1wevomoisc9.py (dados inventados, sem binarios reais)."""

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
annotate_plan = _loadmod("i72bqacdxje1wevomoisc9.py")


def make_payload():
    return {
        "functions": [
            {"addr": 0x401000, "name": "funcao_principal"},
            {"addr": 0x401200, "name": "decodifica_payload"},
        ],
        "comments": [
            {"addr": 0x401010, "text": "chave xor derivada do relogio"},
        ],
    }


class TestAnnotatePlan(unittest.TestCase):
    def test_nomes_e_enderecos_no_idc(self):
        script = annotate_plan.generate(
            make_payload()["functions"], make_payload()["comments"])
        self.assertIn('MakeName(0x401000, "funcao_principal");', script)
        self.assertIn('MakeName(0x401200, "decodifica_payload");', script)

    def test_comentarios_no_idc(self):
        script = annotate_plan.generate(
            make_payload()["functions"], make_payload()["comments"])
        self.assertIn('MakeComm(0x401010, "chave xor derivada do relogio");',
                      script)

    def test_escape_de_aspas(self):
        script = annotate_plan.generate(
            [{"addr": 0x400000, "name": 'f"o"o'}], [])
        self.assertIn('MakeName(0x400000, "f\\"o\\"o");', script)

    def test_entradas_vazias(self):
        script = annotate_plan.generate([], [])
        self.assertIn("static main()", script)
        self.assertNotIn("MakeName", script)
        self.assertNotIn("MakeComm", script)

    def test_addr_como_string(self):
        script = annotate_plan.generate(
            [{"addr": "0x401000", "name": "x"}], [])
        self.assertIn('MakeName(0x401000, "x");', script)

    def test_cli_end_to_end(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json",
                                         delete=False) as fh:
            json.dump(make_payload(), fh)
            path = fh.name
        proc = subprocess.run([sys.executable, "i72bqacdxje1wevomoisc9.py", path],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("MakeName", proc.stdout)
        self.assertIn("MakeComm", proc.stdout)
        self.assertIn("0x401000", proc.stdout)


if __name__ == "__main__":
    unittest.main()
