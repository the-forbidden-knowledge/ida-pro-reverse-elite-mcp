"""Testes do lab 03 — pe-inspect.

Fixtures: PE sintético montado com struct no próprio teste.
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
pe_inspect = _loadmod("2wtiqh4uk8m0i4gmwzp6d9.py")


def montar_pe(secoes, machine=0x14C, timestamp=0x65A1B2C3):
    """Monta um PE mínimo: DOS + PE + COFF + opcional(224) + seções."""
    dos = bytearray(64)
    dos[0:2] = b"MZ"
    struct.pack_into("<I", dos, 0x3C, 0x40)
    coff = struct.pack("<HHIIIHH", machine, len(secoes), timestamp, 0, 0, 224, 0x010F)
    opt = bytes(224)
    cabecalhos = bytes(dos) + b"PE\0\0" + coff + opt
    tabela = b""
    for nome, vsize, vaddr, rawsize, rawptr, chars in secoes:
        rotulo = nome.encode("ascii")[:8].ljust(8, b"\x00")
        tabela += struct.pack(
            "<8sIIIIIIHHI", rotulo, vsize, vaddr, rawsize, rawptr, 0, 0, 0, 0, chars
        )
    return cabecalhos + tabela


class TestPeInspect(unittest.TestCase):
    def _temp(self, dados):
        fd, caminho = tempfile.mkstemp()
        with os.fdopen(fd, "wb") as f:
            f.write(dados)
        self.addCleanup(os.unlink, caminho)
        return caminho

    def test_basico(self):
        secoes = [
            (".text", 0x1000, 0x1000, 0x200, 0x200, 0x60000020),
            (".data", 0x500, 0x2000, 0x200, 0x400, 0xC0000040),
        ]
        caminho = self._temp(montar_pe(secoes))
        r = pe_inspect.inspect_pe(caminho)
        self.assertEqual(r["machine"], 0x14C)
        self.assertEqual(r["machine_name"], "i386")
        self.assertEqual(r["number_of_sections"], 2)
        self.assertEqual(r["timestamp"], 0x65A1B2C3)
        self.assertEqual(r["sections"][0]["name"], ".text")
        self.assertEqual(r["sections"][0]["vsize"], 0x1000)
        self.assertEqual(r["sections"][0]["vaddr"], 0x1000)
        self.assertEqual(r["sections"][0]["rawsize"], 0x200)
        self.assertEqual(r["sections"][0]["characteristics"], 0x60000020)
        self.assertEqual(r["sections"][1]["name"], ".data")

    def test_x64(self):
        caminho = self._temp(montar_pe([], machine=0x8664))
        r = pe_inspect.inspect_pe(caminho)
        self.assertEqual(r["machine_name"], "x86-64")
        self.assertEqual(r["sections"], [])

    def test_nao_pe(self):
        caminho = self._temp(b"isto nao e um executavel")
        with self.assertRaises(ValueError):
            pe_inspect.inspect_pe(caminho)

    def test_cli(self):
        secoes = [(".text", 0x100, 0x1000, 0x200, 0x200, 0x60000020)]
        caminho = self._temp(montar_pe(secoes))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            codigo = pe_inspect.main([caminho])
        self.assertEqual(codigo, 0)
        r = json.loads(buf.getvalue())
        self.assertEqual(r["number_of_sections"], 1)
        self.assertEqual(r["sections"][0]["name"], ".text")


if __name__ == "__main__":
    unittest.main()
