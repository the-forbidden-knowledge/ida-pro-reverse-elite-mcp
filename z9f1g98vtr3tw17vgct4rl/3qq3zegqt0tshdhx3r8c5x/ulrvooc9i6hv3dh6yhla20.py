"""Testes do lab 08 — triage-report.

Fixtures: PE sintético com seção .text, strings e S-box do AES, montado
com struct no próprio teste. Exige os z9f1g98vtr3tw17vgct4rl 01–07 presentes no diretório
z9f1g98vtr3tw17vgct4rl/ irmão.
"""

import contextlib
import io
import json
import os
import struct
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
triage_report = _loadmod("5mpyx89ub4ty7dy7sy95p9.py")

AES_SBOX = bytes.fromhex("63 7c 77 7b f2 6b 6f c5 30 01 67 2b fe d7 ab 76")


def montar_pe():
    dos = bytearray(64)
    dos[0:2] = b"MZ"
    struct.pack_into("<I", dos, 0x3C, 0x40)
    coff = struct.pack("<HHIIIHH", 0x14C, 1, 0x1234, 0, 0, 224, 0x010F)
    opt = bytearray(224)
    struct.pack_into("<H", opt, 0, 0x10B)
    struct.pack_into("<I", opt, 92, 16)
    corpo = b"CreateFileW\x00" + AES_SBOX + b"\x00" * 400
    rotulo = b".text\x00\x00\x00"
    tabela = struct.pack(
        "<8sIIIIIIHHI", rotulo, len(corpo), 0x1000, len(corpo), 0x200,
        0, 0, 0, 0, 0x60000020,
    )
    cabecalho = (bytes(dos) + b"PE\0\0" + coff + bytes(opt) + tabela).ljust(
        0x200, b"\x00"
    )
    return cabecalho + corpo


class TestTriageReport(unittest.TestCase):
    def _temp(self, dados):
        fd, caminho = tempfile.mkstemp()
        with os.fdopen(fd, "wb") as f:
            f.write(dados)
        self.addCleanup(os.unlink, caminho)
        return caminho

    def test_consolidacao(self):
        caminho = self._temp(montar_pe())
        r = triage_report.triage(caminho)
        for chave in (
            "hashes",
            "strings",
            "pe",
            "entropia",
            "empacotador",
            "imports",
            "anomalias",
        ):
            self.assertIn(chave, r, "chave ausente: %s" % chave)
            self.assertNotIn("erro", r[chave], "etapa falhou: %s" % chave)
        self.assertEqual(r["pe"]["number_of_sections"], 1)
        self.assertEqual(r["pe"]["sections"][0]["name"], ".text")
        self.assertGreater(r["strings"]["total"], 0)
        textos = [s["text"] for s in r["strings"]["amostra"]]
        self.assertIn("CreateFileW", textos)
        nomes = [a["nome"] for a in r["anomalias"]]
        self.assertIn("AES S-box", nomes)
        self.assertIn("size", r["hashes"])

    def test_cli(self):
        caminho = self._temp(montar_pe())
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            codigo = triage_report.main([caminho])
        self.assertEqual(codigo, 0)
        r = json.loads(buf.getvalue())
        self.assertEqual(r["arquivo"], os.path.basename(caminho))
        self.assertIn("empacotador", r)


if __name__ == "__main__":
    unittest.main()
