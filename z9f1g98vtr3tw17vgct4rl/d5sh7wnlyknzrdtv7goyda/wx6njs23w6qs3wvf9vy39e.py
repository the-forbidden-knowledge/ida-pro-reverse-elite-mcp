"""Testes do lab 04 — entropy-scan.

Fixtures: PE sintético montado com struct; seção de zeros (entropia 0)
e seção pseudoaleatória determinística (entropia alta).
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
entropy_scan = _loadmod("03f5dekqd2tqc9931mhc41.py")


def montar_pe_com_dados(secoes):
    """secoes: lista de (nome, bytes). Retorna os bytes do PE."""
    dos = bytearray(64)
    dos[0:2] = b"MZ"
    struct.pack_into("<I", dos, 0x3C, 0x40)
    coff = struct.pack("<HHIIIHH", 0x14C, len(secoes), 0, 0, 0, 224, 0x010F)
    cab = bytes(dos) + b"PE\0\0" + coff + bytes(224)
    tabela = b""
    corpos = b""
    ptr = 0x200  # dados brutos começam aqui
    for nome, conteudo in secoes:
        rotulo = nome.encode("ascii")[:8].ljust(8, b"\x00")
        tabela += struct.pack(
            "<8sIIIIIIHHI",
            rotulo,
            len(conteudo),
            0x1000,
            len(conteudo),
            ptr,
            0,
            0,
            0,
            0,
            0x60000020,
        )
        corpos += conteudo
        ptr += len(conteudo)
    cabecalho = (cab + tabela).ljust(0x200, b"\x00")
    return cabecalho + corpos


def pseudoaleatorio(n):
    return bytes((i * 37 + 11) % 256 for i in range(n))


class TestEntropyScan(unittest.TestCase):
    def _temp(self, dados):
        fd, caminho = tempfile.mkstemp()
        with os.fdopen(fd, "wb") as f:
            f.write(dados)
        self.addCleanup(os.unlink, caminho)
        return caminho

    def test_shannon_extremos(self):
        self.assertAlmostEqual(entropy_scan.shannon(b"\x00" * 100), 0.0)
        self.assertAlmostEqual(entropy_scan.shannon(b""), 0.0)
        # 256 símbolos equiprováveis -> 8 bits
        self.assertAlmostEqual(
            entropy_scan.shannon(bytes(range(256)) * 4), 8.0, places=2
        )

    def test_histograma(self):
        h = entropy_scan.histograma(b"\x00\x00\x41")
        self.assertEqual(h[0], 2)
        self.assertEqual(h[0x41], 1)
        self.assertEqual(len(h), 256)
        self.assertEqual(sum(h), 3)

    def test_por_secao(self):
        pe = montar_pe_com_dados(
            [(".text", b"\x00" * 512), (".dado", pseudoaleatorio(2048))]
        )
        caminho = self._temp(pe)
        r = entropy_scan.scan_entropy(caminho)
        secoes = {s["name"]: s for s in r["sections"]}
        self.assertAlmostEqual(secoes[".text"]["entropy"], 0.0)
        self.assertFalse(secoes[".text"]["alerta"])
        self.assertGreater(secoes[".dado"]["entropy"], 7.5)
        self.assertTrue(secoes[".dado"]["alerta"])
        self.assertEqual(len(r["histogram"]), 256)

    def test_threshold(self):
        pe = montar_pe_com_dados([(".dado", pseudoaleatorio(2048))])
        caminho = self._temp(pe)
        r = entropy_scan.scan_entropy(caminho, threshold=8.1)
        self.assertFalse(r["sections"][0]["alerta"])

    def test_cli(self):
        pe = montar_pe_com_dados([(".text", b"\x00" * 64)])
        caminho = self._temp(pe)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            codigo = entropy_scan.main([caminho, "--threshold", "7.0"])
        self.assertEqual(codigo, 0)
        r = json.loads(buf.getvalue())
        self.assertEqual(len(r["sections"]), 1)


if __name__ == "__main__":
    unittest.main()
