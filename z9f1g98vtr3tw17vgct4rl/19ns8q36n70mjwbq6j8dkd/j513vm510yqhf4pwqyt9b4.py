"""Testes do 19ns8q36n70mjwbq6j8dkd (fixtures sinteticas, sem binarios reais)."""

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
        "idc_generate", os.path.join(HERE, "kxq86vk9dq02q7psd4u9oj.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = load_module()


class TestParseAddr(unittest.TestCase):
    def test_hex_str(self):
        self.assertEqual(mod.parse_addr("0x401000"), 0x401000)

    def test_hex_upper(self):
        self.assertEqual(mod.parse_addr("0X404000"), 0x404000)

    def test_dec_str(self):
        self.assertEqual(mod.parse_addr("4198400"), 4198400)

    def test_int(self):
        self.assertEqual(mod.parse_addr(0x5000), 0x5000)


class TestGenerateIdc(unittest.TestCase):
    def test_estrutura_basica(self):
        out = mod.generate_idc({"0x401000": "CreateRemoteThread"})
        self.assertIn("#include <idc.idc>", out)
        self.assertIn("static main() {", out)
        self.assertIn('set_name(0x401000, "CreateRemoteThread");', out)
        self.assertTrue(out.rstrip().endswith("}"))

    def test_ordena_por_endereco(self):
        labels = {"0x404000": "VirtualAllocEx", "0x401000": "CreateRemoteThread"}
        out = mod.generate_idc(labels)
        self.assertLess(out.index("0x401000"), out.index("0x404000"))

    def test_formatos_mistos(self):
        labels = {"4198400": "A", 0x402000: "B", "0x403000": "C"}
        out = mod.generate_idc(labels)
        self.assertIn('set_name(0x401000, "A");', out)
        self.assertIn('set_name(0x402000, "B");', out)
        self.assertIn('set_name(0x403000, "C");', out)

    def test_aspas_no_nome(self):
        out = mod.generate_idc({"0x401000": 'weird"name'})
        self.assertIn("weird'name", out)
        self.assertNotIn('weird"name', out)


class TestCli(unittest.TestCase):
    def test_cli_stdout(self):
        with tempfile.TemporaryDirectory() as td:
            inp = os.path.join(td, "labels.json")
            with open(inp, "w", encoding="utf-8") as f:
                json.dump({"labels": {"0x401000": "IsDebuggerPresent"}}, f)
            r = subprocess.run(
                [sys.executable, os.path.join(HERE, "kxq86vk9dq02q7psd4u9oj.py"),
                 "--input", inp],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn('set_name(0x401000, "IsDebuggerPresent");', r.stdout)

    def test_cli_arquivo(self):
        with tempfile.TemporaryDirectory() as td:
            inp = os.path.join(td, "labels.json")
            outp = os.path.join(td, "out.idc")
            with open(inp, "w", encoding="utf-8") as f:
                json.dump({"0x5000": "Sleep"}, f)
            r = subprocess.run(
                [sys.executable, os.path.join(HERE, "kxq86vk9dq02q7psd4u9oj.py"),
                 "--input", inp, "--output", outp],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            with open(outp, encoding="utf-8") as f:
                corpo = f.read()
            self.assertIn('set_name(0x5000, "Sleep");', corpo)

    def test_cli_json_vazio_falha(self):
        with tempfile.TemporaryDirectory() as td:
            inp = os.path.join(td, "vazio.json")
            with open(inp, "w", encoding="utf-8") as f:
                json.dump({}, f)
            r = subprocess.run(
                [sys.executable, os.path.join(HERE, "kxq86vk9dq02q7psd4u9oj.py"),
                 "--input", inp],
                capture_output=True, text=True)
            self.assertNotEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
