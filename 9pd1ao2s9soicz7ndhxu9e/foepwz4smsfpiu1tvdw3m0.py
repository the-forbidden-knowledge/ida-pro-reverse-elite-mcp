#!/usr/bin/env python3
"""Testes do orquestrador CLONAR (9pd1ao2s9soicz7ndhxu9e/ni8imoj0zs33nddqo4cq01.py).

Fixtures 100% sinteticas: PE32 minimo montado byte a byte + export JSON
sintetico no formato do mrg3ynauhl4c6qu1go4jqo. Nenhum binario real.
"""

import importlib.util
import json
import os
import struct
import sys
import tempfile
import unittest

BASE = os.path.dirname(os.path.abspath(__file__))


def _carregar():
    caminho = os.path.join(BASE, "ni8imoj0zs33nddqo4cq01.py")
    spec = importlib.util.spec_from_file_location("clone_9pd1ao2s9soicz7ndhxu9e", caminho)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def pe_minimo():
    """Monta um PE32 minimo valido (1 secao .text com alguns bytes)."""
    dos = bytearray(0x40)
    dos[0:2] = b"MZ"
    struct.pack_into("<I", dos, 0x3C, 0x40)
    pe = b"PE\x00\x00"
    coff = struct.pack("<HHIIIHH", 0x14C, 1, 0, 0, 0, 0xE0, 0x010F)
    opt = bytearray(0xE0)
    struct.pack_into("<H", opt, 0, 0x10B)  # magic PE32
    sec = struct.pack("<8sIIIIIIHHI", b".text\x00\x00\x00", 0x200, 0x1000,
                      0x200, 0x200, 0, 0, 0, 0, 0x60000020)
    cabeca = bytes(dos) + pe + coff + bytes(opt) + sec
    cabeca = cabeca.ljust(0x200, b"\x00")
    corpo = b"hello world\x00http://example.com\x00" + b"\x90" * 400
    return cabeca + corpo


def export_sintetico():
    return {
        "functions": [
            {"name": "main", "addr": "0x401000",
             "calls": ["OpenProcess", "VirtualAllocEx"],
             "xrefs_to": ["0x402000"]},
            {"name": "inject", "addr": "0x401100",
             "calls": ["WriteProcessMemory", "CreateRemoteThread"],
             "xrefs_to": []},
        ],
        "strings": [
            {"text": "http://example.com", "addr": "0x40a000",
             "xrefs": ["0x401020"]},
            {"text": "cmd.exe", "addr": "0x40a020", "xrefs": []},
        ],
        "imports": {
            "kernel32.dll": ["OpenProcess", "VirtualAllocEx",
                             "WriteProcessMemory", "CreateRemoteThread",
                             "IsDebuggerPresent"],
            "advapi32.dll": ["RegOpenKeyExA"],
        },
    }


class TestPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cp = _carregar()

    def _rodar(self, com_export=True):
        tmp = tempfile.mkdtemp()
        alvo = os.path.join(tmp, "alvo.exe")
        with open(alvo, "wb") as f:
            f.write(pe_minimo())
        exp_path = None
        if com_export:
            exp_path = os.path.join(tmp, "export.json")
            with open(exp_path, "w", encoding="utf-8") as f:
                json.dump(export_sintetico(), f)
        saida = os.path.join(tmp, "out")
        self.cp.executar(alvo, exp_path, saida)
        return tmp, saida

    def test_arquivos_gerados(self):
        _, saida = self._rodar()
        for nome in ("triagem.json", "leitura.json", "desobfuscacao.json",
                     "injecao.json", "bypass.json", "reconstrucao.json",
                     "relatorio.json", "relatorio.md"):
            self.assertTrue(os.path.exists(os.path.join(saida, nome)), nome)

    def test_triagem_ok(self):
        _, saida = self._rodar()
        with open(os.path.join(saida, "triagem.json"), encoding="utf-8") as f:
            tri = json.load(f)
        self.assertIn("hashes", tri)
        self.assertEqual(tri["hashes"].get("erro", None), None)
        self.assertIn("strings", tri)

    def test_leitura_rastreia_api(self):
        _, saida = self._rodar()
        with open(os.path.join(saida, "leitura.json"), encoding="utf-8") as f:
            lei = json.load(f)
        rastros = lei.get("9d0trqr4ktimjrds7goieb") or {}
        self.assertIn("CreateRemoteThread", rastros)
        self.assertEqual(lei["resumo"]["funcoes"], 2)

    def test_injecao_detectada(self):
        _, saida = self._rodar()
        with open(os.path.join(saida, "injecao.json"), encoding="utf-8") as f:
            inj = json.load(f)
        self.assertTrue(inj["me3cvyro1kttvtrzo267a9"].get("detected"))

    def test_bypass_encontra_defesa(self):
        _, saida = self._rodar()
        with open(os.path.join(saida, "bypass.json"), encoding="utf-8") as f:
            byp = json.load(f)
        inv = byp["pft8rdap8iblilku7ni0y8"]
        apis = [d["api"] for d in inv.get("defesas", [])]
        self.assertIn("IsDebuggerPresent", apis)
        self.assertGreater(len(byp["r7vkuk0bo7khhekzv7to9p"]["patches"]), 0)

    def test_reconstrucao_gera_ledger_e_cobertura(self):
        _, saida = self._rodar()
        with open(os.path.join(saida, "reconstrucao.json"),
                  encoding="utf-8") as f:
            rec = json.load(f)
        comportamentos = rec["d9yen9lqdjkquwp3jjyxep"]
        self.assertIsInstance(comportamentos, list)
        self.assertGreater(len(comportamentos), 0)
        cobertura = rec["m49dd353e4mwmhzhwd1xcp"]
        self.assertNotIn("erro", cobertura)

    def test_relatorio_final(self):
        _, saida = self._rodar()
        with open(os.path.join(saida, "relatorio.json"), encoding="utf-8") as f:
            rel = json.load(f)
        self.assertEqual(rel["relatorio"], "CLONAR")
        self.assertIn("fases", rel)
        self.assertEqual(rel["fases"]["triagem"]["status"], "ok")
        with open(os.path.join(saida, "relatorio.md"), encoding="utf-8") as f:
            md = f.read()
        self.assertIn("CLONAR", md)

    def test_sem_ida_export_nao_derruba(self):
        _, saida = self._rodar(com_export=False)
        with open(os.path.join(saida, "leitura.json"), encoding="utf-8") as f:
            lei = json.load(f)
        self.assertIn("erro", lei)
        with open(os.path.join(saida, "relatorio.json"), encoding="utf-8") as f:
            rel = json.load(f)
        self.assertEqual(rel["relatorio"], "CLONAR")

    def test_alvo_invalido_vira_erro_isolado(self):
        tmp = tempfile.mkdtemp()
        alvo = os.path.join(tmp, "nada.bin")
        with open(alvo, "wb") as f:
            f.write(b"\x00" * 64)
        saida = os.path.join(tmp, "out")
        self.cp.executar(alvo, None, saida)  # nao deve levantar
        with open(os.path.join(saida, "triagem.json"), encoding="utf-8") as f:
            tri = json.load(f)
        # PE invalido: etapa pe/imports vira erro, mas o relatorio existe
        self.assertIn("hashes", tri)
        self.assertTrue(os.path.exists(os.path.join(saida, "relatorio.md")))


if __name__ == "__main__":
    unittest.main()
