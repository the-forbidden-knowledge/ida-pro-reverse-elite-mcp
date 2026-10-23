#!/usr/bin/env python3
"""Testes do lab 89 — log-leak. Fixtures 100% sintéticas."""

import importlib.util
import os
import unittest

_AQUI = os.path.dirname(os.path.abspath(__file__))


def _carregar():
    spec = importlib.util.spec_from_file_location(
        "log_leak", os.path.join(_AQUI, "zd1ufz6l6gdmcpeazpo1p2.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = _carregar()


class TestLogLeak(unittest.TestCase):
    def test_encontra_log_d(self):
        linhas = [
            '    const-string v0, "TAG"',
            '    const-string v1, "valor=42"',
            "    invoke-static {v0, v1}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I",
        ]
        r = mod.vazar_linhas(linhas)
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]["nivel"], "d")
        self.assertEqual(r[0]["tag"], "TAG")
        self.assertEqual(r[0]["msg"], "valor=42")
        self.assertEqual(r[0]["linha"], 3)

    def test_todos_os_niveis(self):
        linhas = []
        for n in "deivw":
            linhas.append("    const-string v0, \"t\"")
            linhas.append("    const-string v1, \"m\"")
            linhas.append(
                "    invoke-static {v0, v1}, Landroid/util/Log;->%s(Ljava/lang/String;Ljava/lang/String;)I"
                % n
            )
        r = mod.vazar_linhas(linhas)
        self.assertEqual([x["nivel"] for x in r], list("deivw"))

    def test_ignora_nao_log(self):
        linhas = [
            "    invoke-static {v0}, Ljava/lang/Math;->abs(I)I",
        ]
        self.assertEqual(mod.vazar_linhas(linhas), [])

    def test_registrador_desconhecido_vira_interrogacao(self):
        linhas = [
            "    invoke-static {v9, v1}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I",
        ]
        r = mod.vazar_linhas(linhas)
        self.assertEqual(r[0]["tag"], "?")

    def test_vazio(self):
        self.assertEqual(mod.vazar_linhas([]), [])


if __name__ == "__main__":
    unittest.main()
