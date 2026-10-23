#!/usr/bin/env python3
"""Testes do lab 91 — multiformat-pipeline (fixtures sintéticas)."""

import hashlib
import json
import os
import struct
import sys
import tempfile
import unittest
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util as _ilu
import os as _os
def _loadmod(_fname):
    _sp = _ilu.spec_from_file_location("_m", _os.path.join(_os.path.dirname(__file__), _fname))
    _mm = _ilu.module_from_spec(_sp); _sp.loader.exec_module(_mm)
    return _mm
_mx_multiformat_pipeline = _loadmod("jv5g671l8nr533ospbozho.py")
analyze, detect_format, run_pipeline = _mx_multiformat_pipeline.analyze, _mx_multiformat_pipeline.detect_format, _mx_multiformat_pipeline.run_pipeline


def make_elf() -> bytes:
    e_ident = b"\x7fELF" + bytes([2, 1, 1, 0]) + bytes(8)
    ehdr = struct.pack("<16sHHIQQQIHHHHHH",
                       e_ident, 2, 62, 1, 0x401000, 64, 120, 0, 64, 56, 1, 64, 0, 0)
    return ehdr + bytes(200)


def make_fat() -> bytes:
    hdr = struct.pack(">II", 0xCAFEBABE, 1)
    arch = struct.pack(">IIIII", 0x0100000C, 0, 28, 32, 12)
    return hdr + arch + b"A" * 32


def make_dex() -> bytes:
    corpo = bytes(64)
    hdr = struct.pack("<8sI20s" + "I" * 20,
                      b"dex\n035\x00", 0, bytes(20), 112 + 64, 0x70, 0x12345678,
                      *((0,) * 15), 64, 112)
    blob = hdr + corpo
    blob = blob[:12] + hashlib.sha1(blob[32:]).digest() + blob[32:]
    blob = blob[:8] + struct.pack("<I", zlib.adler32(blob[12:]) & 0xFFFFFFFF) + blob[12:]
    return blob


def make_pe() -> bytes:
    dos = bytearray(64)
    dos[0:2] = b"MZ"
    struct.pack_into("<I", dos, 0x3C, 64)
    return bytes(dos) + b"PE\x00\x00" + bytes(32)


def grava(data: bytes, sufixo: str) -> str:
    f = tempfile.NamedTemporaryFile(suffix=sufixo, delete=False)
    f.write(data)
    f.close()
    return f.name


class TestDetectFormat(unittest.TestCase):
    def test_elf(self):
        self.assertEqual(detect_format(make_elf()), "elf64")

    def test_fat(self):
        self.assertEqual(detect_format(make_fat()), "macho-fat")

    def test_dex(self):
        self.assertEqual(detect_format(make_dex()), "dex")

    def test_pe(self):
        self.assertEqual(detect_format(make_pe()), "pe")

    def test_desconhecido(self):
        self.assertEqual(detect_format(b"????"), "desconhecido")
        self.assertEqual(detect_format(b""), "desconhecido")


class TestAnalyze(unittest.TestCase):
    def test_analyze_elf(self):
        caminho = grava(make_elf(), ".elf")
        try:
            r = analyze(caminho)
            self.assertEqual(r["formato"], "elf64")
            self.assertIn("resumo", r)
        finally:
            os.unlink(caminho)

    def test_analyze_fat(self):
        caminho = grava(make_fat(), ".fat")
        try:
            r = analyze(caminho)
            self.assertEqual(r["formato"], "macho-fat")
            self.assertEqual(r["resumo"]["arquiteturas"], ["arm64"])
        finally:
            os.unlink(caminho)

    def test_analyze_desconhecido(self):
        caminho = grava(b"????", ".bin")
        try:
            r = analyze(caminho)
            self.assertIn("erro", r)
        finally:
            os.unlink(caminho)


class TestRunPipeline(unittest.TestCase):
    def test_totais(self):
        caminhos = [grava(make_elf(), ".elf"), grava(make_fat(), ".fat"),
                    grava(make_dex(), ".dex"), grava(make_pe(), ".pe")]
        try:
            r = run_pipeline(caminhos)
            self.assertEqual(r["totais"], {"elf64": 1, "macho-fat": 1, "dex": 1, "pe": 1})
            self.assertEqual(r["analisados"], 4)
            self.assertEqual(r["falhas"], 0)
        finally:
            for c in caminhos:
                os.unlink(c)


if __name__ == "__main__":
    unittest.main()
