#!/usr/bin/env python3
"""Testes sinteticos para x7zvgqybn3g6ytmtg801l1.py (fixtures inventadas, sem binarios reais)."""

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
api_patterns = _loadmod("x7zvgqybn3g6ytmtg801l1.py")


class TestApiPatterns(unittest.TestCase):
    def test_injecao_processo(self):
        data = {"apis": ["OpenProcess", "VirtualAllocEx", "WriteProcessMemory",
                         "CreateRemoteThread", "CloseHandle"]}
        out = api_patterns.detect(data["apis"])
        intents = {p["intent"] for p in out["patterns"]}
        self.assertIn("injecao-processo", intents)

    def test_multiplos_padroes(self):
        data = {"apis": ["RegOpenKeyEx", "RegSetValueEx", "socket", "connect",
                         "send", "recv", "GetProcAddress"]}
        intents = {p["intent"] for p in api_patterns.detect(data["apis"])["patterns"]}
        self.assertEqual(intents, {"persistencia-registro", "comunicacao-rede"})

    def test_case_insensitive(self):
        data = {"apis": ["createfile", "WRITEFILE"]}
        intents = {p["intent"] for p in api_patterns.detect(data["apis"])["patterns"]}
        self.assertIn("escrita-arquivo", intents)

    def test_grupo_incompleto_nao_detecta(self):
        data = {"apis": ["IsDebuggerPresent"]}  # falta GetTickCount
        intents = {p["intent"] for p in api_patterns.detect(data["apis"])["patterns"]}
        self.assertNotIn("anti-analise", intents)

    def test_vazio(self):
        self.assertEqual(api_patterns.detect([]), {"patterns": []})

    def test_cli_end_to_end(self):
        payload = {"apis": ["CryptEncrypt", "CryptDecrypt"]}
        with tempfile.NamedTemporaryFile("w", suffix=".json",
                                         delete=False) as fh:
            json.dump(payload, fh)
            path = fh.name
        proc = subprocess.run([sys.executable, "x7zvgqybn3g6ytmtg801l1.py", path],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        out = json.loads(proc.stdout)
        self.assertEqual([p["intent"] for p in out["patterns"]],
                         ["criptografia"])


if __name__ == "__main__":
    unittest.main()
