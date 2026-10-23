#!/usr/bin/env python3
"""Testes do lab 94 — anti-ida-benchmark (fixtures sintéticas)."""

import os
import subprocess
import sys
import unittest

import importlib.util as _ilu
import os as _os
def _loadmod(_fname):
    _sp = _ilu.spec_from_file_location("_m", _os.path.join(_os.path.dirname(__file__), _fname))
    _mm = _ilu.module_from_spec(_sp); _sp.loader.exec_module(_mm)
    return _mm
_mx_anti_ida_benchmark = _loadmod("lzxks05a6s1et79l7q9m2z.py")
benchmark, format_table, tarefas_padrao = _mx_anti_ida_benchmark.benchmark, _mx_anti_ida_benchmark.format_table, _mx_anti_ida_benchmark.tarefas_padrao


class TestBenchmark(unittest.TestCase):
    def test_speedup(self):
        r = benchmark([{"nome": "t", "ida_segundos": 100, "baroque_segundos": 10}])
        self.assertEqual(r["tarefas"][0]["speedup"], 10.0)
        self.assertEqual(r["speedup_total"], 10.0)

    def test_totais(self):
        r = benchmark([
            {"nome": "a", "ida_segundos": 60, "baroque_segundos": 6},
            {"nome": "b", "ida_segundos": 40, "baroque_segundos": 4},
        ])
        self.assertEqual(r["total_ida"], 100.0)
        self.assertEqual(r["total_baroque"], 10.0)
        self.assertEqual(r["speedup_total"], 10.0)

    def test_marca_simulado(self):
        self.assertTrue(benchmark([])["simulado"])

    def test_vazio(self):
        r = benchmark([])
        self.assertEqual(r["tarefas"], [])
        self.assertEqual(r["speedup_total"], 0.0)

    def test_tempo_zero_erro(self):
        with self.assertRaises(ValueError):
            benchmark([{"nome": "t", "ida_segundos": 10, "baroque_segundos": 0}])


class TestFormatTable(unittest.TestCase):
    def test_cabecalho_e_total(self):
        r = benchmark([{"nome": "triagem", "ida_segundos": 100, "baroque_segundos": 10}])
        tabela = format_table(r)
        self.assertIn("tarefa", tabela)
        self.assertIn("TOTAL", tabela)
        self.assertIn("10.0x", tabela)


class TestTarefasPadrao(unittest.TestCase):
    def test_cinco_tarefas(self):
        self.assertEqual(len(tarefas_padrao()), 5)

    def test_cli(self):
        r = subprocess.run(
            [sys.executable, os.path.join(os.path.dirname(__file__),
                                          "lzxks05a6s1et79l7q9m2z.py")],
            capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)
        self.assertIn("TOTAL", r.stdout)
        self.assertIn("simulados", r.stdout)


if __name__ == "__main__":
    unittest.main()
