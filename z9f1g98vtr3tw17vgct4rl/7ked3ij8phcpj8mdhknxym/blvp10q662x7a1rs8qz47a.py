"""Testes do lab 02 — strings-extract.

Fixtures: bytes sintéticos gerados no próprio teste.
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
strings_extract = _loadmod("k2kkjnz1dcoa2jviigqdff.py")


class TestStringsExtract(unittest.TestCase):
    def _temp(self, dados):
        fd, caminho = tempfile.mkstemp()
        with os.fdopen(fd, "wb") as f:
            f.write(dados)
        self.addCleanup(os.unlink, caminho)
        return caminho

    def _dados(self):
        # offsets: "Teste" em UTF-16LE@2, ABCD@14, EFGHIJ@19
        # (a ordem evita que o \x00 após o ASCII forme par com o UTF-16LE)
        return (
            b"\x00\x01"
            + "Teste".encode("utf-16-le")
            + b"\x00\x01"
            + b"ABCD"
            + b"\x00"
            + b"EFGHIJ"
            + b"\x00\x00ab\x00"
        )

    def test_ascii_e_utf16(self):
        caminho = self._temp(self._dados())
        r = strings_extract.extract_strings(caminho)
        por_offset = {s["offset"]: s for s in r}
        self.assertEqual(por_offset[14]["text"], "ABCD")
        self.assertEqual(por_offset[14]["encoding"], "ascii")
        self.assertEqual(por_offset[19]["text"], "EFGHIJ")
        self.assertEqual(por_offset[2]["text"], "Teste")
        self.assertEqual(por_offset[2]["encoding"], "utf-16le")
        # "ab" tem 2 chars < min_len 4: não aparece
        self.assertNotIn(27, por_offset)

    def test_min_len(self):
        caminho = self._temp(self._dados())
        r = strings_extract.extract_strings(caminho, min_len=6)
        textos = [s["text"] for s in r]
        self.assertNotIn("ABCD", textos)
        self.assertIn("EFGHIJ", textos)

    def test_somente_ascii(self):
        caminho = self._temp(self._dados())
        r = strings_extract.extract_strings(caminho, encoding="ascii")
        self.assertTrue(all(s["encoding"] == "ascii" for s in r))
        self.assertEqual(len(r), 2)

    def test_somente_utf16(self):
        caminho = self._temp(self._dados())
        r = strings_extract.extract_strings(caminho, encoding="utf16")
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]["text"], "Teste")

    def test_ordenado_por_offset(self):
        caminho = self._temp(self._dados())
        r = strings_extract.extract_strings(caminho)
        offsets = [s["offset"] for s in r]
        self.assertEqual(offsets, sorted(offsets))

    def test_cli(self):
        caminho = self._temp(self._dados())
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            codigo = strings_extract.main(
                [caminho, "--min-len", "4", "--encoding", "both"]
            )
        self.assertEqual(codigo, 0)
        r = json.loads(buf.getvalue())
        self.assertEqual(len(r), 3)


if __name__ == "__main__":
    unittest.main()
