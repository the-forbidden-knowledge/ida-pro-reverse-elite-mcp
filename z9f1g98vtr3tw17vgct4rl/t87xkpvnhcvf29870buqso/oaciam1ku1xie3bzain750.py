"""Testes do lab 12 — symbolic-constants.

Fixtures: dump de disassembly sintético com imediatos conhecidos.
"""

import contextlib
import io
import json
import os
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
symbolic_constants = _loadmod("x58o4f9k4gko5a3pi5bvwc.py")

DUMP = """\
.text:00401000 push    80000001h
.text:00401005 push    offset SubKey
.text:0040100A call    RegOpenKeyExW
.text:00401010 mov     eax, 0xC0000005
.text:00401015 push    40h
.text:00401017 call    VirtualProtect
.text:0040101C mov     ecx, 1234h
"""


class TestSymbolicConstants(unittest.TestCase):
    def _temp(self, texto):
        fd, caminho = tempfile.mkstemp(suffix=".txt")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(texto)
        self.addCleanup(os.unlink, caminho)
        return caminho

    def test_resolve(self):
        r = symbolic_constants.resolve_dump(DUMP)
        por_valor = {a["valor"]: a for a in r}
        self.assertEqual(por_valor["0x80000001"]["nome"], "HKEY_CURRENT_USER")
        self.assertEqual(por_valor["0x80000001"]["linha"], 1)
        self.assertEqual(
            por_valor["0xC0000005"]["nome"], "STATUS_ACCESS_VIOLATION"
        )
        self.assertEqual(por_valor["0x40"]["nome"], "PAGE_EXECUTE_READWRITE")

    def test_desconhecido_ignorado(self):
        r = symbolic_constants.resolve_dump(DUMP)
        valores = [a["valor"] for a in r]
        self.assertNotIn("0x1234", valores)

    def test_sem_duplicar_na_linha(self):
        r = symbolic_constants.resolve_dump("push 80000001h ; 0x80000001\n")
        self.assertEqual(len(r), 1)

    def test_vazio(self):
        self.assertEqual(symbolic_constants.resolve_dump(""), [])

    def test_cli(self):
        caminho = self._temp(DUMP)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            codigo = symbolic_constants.main([caminho])
        self.assertEqual(codigo, 0)
        r = json.loads(buf.getvalue())
        self.assertEqual(len(r), 3)
        self.assertEqual(r[0]["linha"], 1)


if __name__ == "__main__":
    unittest.main()
