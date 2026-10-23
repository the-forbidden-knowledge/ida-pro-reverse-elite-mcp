"""Testes do lab 06 — import-inventory.

Fixtures: PE sintético com diretório de imports completo (descritor,
ILT/IAT, Hint/Name, nome da DLL), montado com struct no próprio teste.
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
import_inventory = _loadmod("z59qep6b0esdjioi7o21qj.py")


def montar_pe_imports():
    """PE com .text e .idata; importa CreateFileA, ReadFile e ordinal 5
    de kernel32.dll."""
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
    # diretório de imports -> RVA 0x2000 (.idata)
    struct.pack_into("<II", opt, 104, 0x2000, 0x28)

    idata = bytearray(0x200)
    # descritor 0: ILT=0x203C, nome=0x2080, IAT=0x2060
    struct.pack_into("<IIIII", idata, 0x00, 0x203C, 0, 0, 0x2080, 0x2060)
    # ILT e IAT: CreateFileA, ReadFile, ordinal 5
    for base in (0x3C, 0x60):
        struct.pack_into("<IIII", idata, base, 0x2090, 0x209E, 0x80000005, 0)
    idata[0x80 : 0x80 + 13] = b"kernel32.dll\x00"
    struct.pack_into("<H", idata, 0x90, 0)
    idata[0x92 : 0x92 + 12] = b"CreateFileA\x00"
    struct.pack_into("<H", idata, 0x9E, 0)
    idata[0xA0 : 0xA0 + 9] = b"ReadFile\x00"

    tabela = b""
    for nome, vaddr, rawptr in ((".text", 0x1000, 0x200), (".idata", 0x2000, 0x400)):
        rotulo = nome.encode("ascii")[:8].ljust(8, b"\x00")
        tabela += struct.pack(
            "<8sIIIIIIHHI", rotulo, 0x200, vaddr, 0x200, rawptr, 0, 0, 0, 0,
            0x60000020,
        )
    cabecalho = (
        bytes(dos) + b"PE\0\0" + coff + bytes(opt) + tabela
    ).ljust(0x200, b"\x00")
    return cabecalho + bytes(0x200) + bytes(idata)


def montar_pe_sem_imports():
    dos = bytearray(64)
    dos[0:2] = b"MZ"
    struct.pack_into("<I", dos, 0x3C, 0x40)
    coff = struct.pack("<HHIIIHH", 0x14C, 1, 0, 0, 0, 224, 0x010F)
    opt = bytearray(224)
    struct.pack_into("<H", opt, 0, 0x10B)
    struct.pack_into("<I", opt, 92, 16)
    tabela = struct.pack(
        "<8sIIIIIIHHI", b".text\x00\x00\x00", 0x200, 0x1000, 0x200, 0x200,
        0, 0, 0, 0, 0x60000020,
    )
    cabecalho = (bytes(dos) + b"PE\0\0" + coff + bytes(opt) + tabela).ljust(
        0x200, b"\x00"
    )
    return cabecalho + bytes(0x200)


class TestImportInventory(unittest.TestCase):
    def _temp(self, dados):
        fd, caminho = tempfile.mkstemp()
        with os.fdopen(fd, "wb") as f:
            f.write(dados)
        self.addCleanup(os.unlink, caminho)
        return caminho

    def test_imports(self):
        caminho = self._temp(montar_pe_imports())
        r = import_inventory.import_inventory(caminho)
        self.assertEqual(
            r["imports"],
            {"kernel32.dll": ["CreateFileA", "ReadFile", "ordinal_5"]},
        )
        self.assertEqual(r["total_dlls"], 1)
        self.assertEqual(r["total_funcoes"], 3)

    def test_sem_imports(self):
        caminho = self._temp(montar_pe_sem_imports())
        r = import_inventory.import_inventory(caminho)
        self.assertEqual(r["imports"], {})
        self.assertEqual(r["total_dlls"], 0)
        self.assertEqual(r["total_funcoes"], 0)

    def test_cli(self):
        caminho = self._temp(montar_pe_imports())
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            codigo = import_inventory.main([caminho])
        self.assertEqual(codigo, 0)
        r = json.loads(buf.getvalue())
        self.assertIn("kernel32.dll", r["imports"])
        self.assertIn("ReadFile", r["imports"]["kernel32.dll"])


if __name__ == "__main__":
    unittest.main()
