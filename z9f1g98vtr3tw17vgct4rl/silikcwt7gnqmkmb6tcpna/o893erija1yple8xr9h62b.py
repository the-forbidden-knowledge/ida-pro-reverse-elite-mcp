"""Testes do lab 05 — packer-detect.

Fixtures: dois PEs sintéticos — um "empacotado" (seções UPX0/UPX1 com
entropia alta, sem imports) e um normal (.text/.idata, 2 descritores).
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
packer_detect = _loadmod("ss1tloeughims6tjffpw55.py")


def pseudoaleatorio(n):
    return bytes((i * 37 + 11) % 256 for i in range(n))


def montar_pe(nomes, conteudos, n_descritores):
    """Monta PE com 2 seções; a segunda pode carregar N descritores."""
    dos = bytearray(64)
    dos[0:2] = b"MZ"
    struct.pack_into("<I", dos, 0x3C, 0x40)
    coff = struct.pack("<HHIIIHH", 0x14C, 2, 0, 0, 0, 224, 0x010F)
    opt = bytearray(224)
    struct.pack_into("<H", opt, 0, 0x10B)
    struct.pack_into("<I", opt, 28, 0x400000)
    struct.pack_into("<I", opt, 32, 0x1000)
    struct.pack_into("<I", opt, 36, 0x200)
    struct.pack_into("<I", opt, 92, 16)
    if n_descritores:
        # diretório de imports -> segunda seção (RVA 0x2000)
        struct.pack_into("<II", opt, 104, 0x2000, 0x100)
    # corpo da segunda seção: N descritores + terminador + nomes de DLL
    idata = b""
    nomes_dll = b""
    for i in range(n_descritores):
        idata += struct.pack("<IIIII", 0, 0, 0, 0x2000 + 0x100 + len(nomes_dll), 0)
        nomes_dll += ("dll%d.dll" % i).encode("ascii") + b"\x00"
    idata += b"\x00" * 20 + nomes_dll
    corpos = [conteudos[0], idata]
    tabela = b""
    ptr = 0x200
    for idx, nome in enumerate(nomes):
        rotulo = nome.encode("ascii")[:8].ljust(8, b"\x00")
        tabela += struct.pack(
            "<8sIIIIIIHHI",
            rotulo,
            len(corpos[idx]),
            0x1000 + idx * 0x1000,
            len(corpos[idx]),
            ptr,
            0,
            0,
            0,
            0,
            0x60000020,
        )
        ptr += len(corpos[idx])
    cabecalho = (bytes(dos) + b"PE\0\0" + coff + bytes(opt) + tabela).ljust(
        0x200, b"\x00"
    )
    return cabecalho + b"".join(corpos)


class TestPackerDetect(unittest.TestCase):
    def _temp(self, dados):
        fd, caminho = tempfile.mkstemp()
        with os.fdopen(fd, "wb") as f:
            f.write(dados)
        self.addCleanup(os.unlink, caminho)
        return caminho

    def test_empacotado(self):
        pe = montar_pe(
            ["UPX0", "UPX1"], [pseudoaleatorio(1024), pseudoaleatorio(1024)], 0
        )
        caminho = self._temp(pe)
        r = packer_detect.detect_packer(caminho)
        self.assertTrue(r["packed"])
        self.assertGreaterEqual(len(r["reasons"]), 2)
        self.assertEqual(r["import_descriptors"], 0)
        motivos = " ".join(r["reasons"])
        self.assertIn("UPX0", motivos)
        self.assertIn("entropia alta", motivos)

    def test_normal(self):
        pe = montar_pe([".text", ".idata"], [b"\x00" * 1024, b""], 2)
        caminho = self._temp(pe)
        r = packer_detect.detect_packer(caminho)
        self.assertFalse(r["packed"])
        self.assertEqual(r["reasons"], [])
        self.assertEqual(r["import_descriptors"], 2)

    def test_cli(self):
        pe = montar_pe(["UPX0", "UPX1"], [pseudoaleatorio(512)] * 2, 0)
        caminho = self._temp(pe)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            codigo = packer_detect.main([caminho])
        self.assertEqual(codigo, 0)
        r = json.loads(buf.getvalue())
        self.assertTrue(r["packed"])


if __name__ == "__main__":
    unittest.main()
