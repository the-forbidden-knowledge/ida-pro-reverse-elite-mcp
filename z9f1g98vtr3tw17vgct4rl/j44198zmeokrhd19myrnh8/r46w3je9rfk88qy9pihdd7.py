"""Testes do j44198zmeokrhd19myrnh8 (fixtures sinteticas)."""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def load_module():
    spec = importlib.util.spec_from_file_location(
        "memory_report", os.path.join(HERE, "2sdojr99he1lxpkaefruub.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = load_module()

RWX = {"suspect_regions": [
    {"base": "0x100000", "size": 4096, "protect": "RWX", "has_mz": True},
    {"base": "0x200000", "size": 8192, "protect": "RWX", "has_code": True},
]}
HOOKS = {"patched": [
    {"func": "CreateFileW", "addr": "0x7ff1000", "byte0": "0xE9"},
]}


class TestCountIdc(unittest.TestCase):
    def test_conta_set_name(self):
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "r.idc")
            with open(p, "w") as f:
                f.write('static main() {\n set_name(0x1, "A");\n set_name(0x2, "B");\n}\n')
            self.assertEqual(mod.count_idc_labels(p), 2)

    def test_arquivo_inexistente(self):
        self.assertEqual(mod.count_idc_labels("/nao/existe.idc"), 0)

    def test_none(self):
        self.assertEqual(mod.count_idc_labels(None), 0)


class TestBuildReport(unittest.TestCase):
    def test_consolida_tudo(self):
        rel = mod.build_report(RWX, HOOKS, None)
        self.assertEqual(rel["fase"], "memoria")
        self.assertEqual(rel["resumo"]["regioes_rwx"], 2)
        self.assertEqual(rel["resumo"]["prologos_patcheados"], 1)
        self.assertEqual(len(rel["rwx"]["regioes_suspeitas"]), 2)

    def test_entradas_ausentes(self):
        rel = mod.build_report(None, None, None)
        self.assertEqual(rel["resumo"]["regioes_rwx"], 0)
        self.assertEqual(rel["resumo"]["prologos_patcheados"], 0)
        self.assertEqual(rel["resumo"]["rotulos_idc"], 0)

    def test_so_rwx(self):
        rel = mod.build_report(RWX, None, None)
        self.assertEqual(rel["resumo"]["regioes_rwx"], 2)
        self.assertEqual(rel["resumo"]["prologos_patcheados"], 0)


class TestCli(unittest.TestCase):
    def _write(self, td, nome, obj):
        p = os.path.join(td, nome)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(obj, f)
        return p

    def test_cli_completo(self):
        with tempfile.TemporaryDirectory() as td:
            rwx = self._write(td, "rwx.json", RWX)
            hooks = self._write(td, "hooks.json", HOOKS)
            idc = os.path.join(td, "r.idc")
            with open(idc, "w") as f:
                f.write('set_name(0x1, "A");\n')
            out = os.path.join(td, "rel.json")
            r = subprocess.run(
                [sys.executable, os.path.join(HERE, "2sdojr99he1lxpkaefruub.py"),
                 "--rwx", rwx, "--hooks", hooks, "--idc", idc,
                 "--output", out],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            with open(out, encoding="utf-8") as f:
                rel = json.load(f)
            self.assertEqual(rel["resumo"]["regioes_rwx"], 2)
            self.assertEqual(rel["resumo"]["rotulos_idc"], 1)

    def test_cli_stdout(self):
        with tempfile.TemporaryDirectory() as td:
            rwx = self._write(td, "rwx.json", RWX)
            r = subprocess.run(
                [sys.executable, os.path.join(HERE, "2sdojr99he1lxpkaefruub.py"),
                 "--rwx", rwx],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            rel = json.loads(r.stdout)
            self.assertEqual(rel["fase"], "memoria")

    def test_cli_sem_entradas(self):
        r = subprocess.run(
            [sys.executable, os.path.join(HERE, "2sdojr99he1lxpkaefruub.py")],
            capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        rel = json.loads(r.stdout)
        self.assertEqual(rel["resumo"]["regioes_rwx"], 0)


if __name__ == "__main__":
    unittest.main()
