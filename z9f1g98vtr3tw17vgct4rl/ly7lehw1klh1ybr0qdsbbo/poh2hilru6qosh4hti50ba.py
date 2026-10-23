"""Testes do lab 01 — hash-identify.

Fixtures: arquivos temporários com bytes sintéticos gerados no próprio teste.
"""

import contextlib
import hashlib
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
hash_identify = _loadmod("3ks95ofobzc2vqwo6p719v.py")


class TestHashIdentify(unittest.TestCase):
    def _temp(self, dados):
        fd, caminho = tempfile.mkstemp()
        with os.fdopen(fd, "wb") as f:
            f.write(dados)
        self.addCleanup(os.unlink, caminho)
        return caminho

    def test_hashes_conhecidos(self):
        dados = b"conteudo sintetico para teste de hash 0123456789"
        caminho = self._temp(dados)
        r = hash_identify.hash_file(caminho)
        self.assertEqual(r["md5"], hashlib.md5(dados).hexdigest())
        self.assertEqual(r["sha1"], hashlib.sha1(dados).hexdigest())
        self.assertEqual(r["sha256"], hashlib.sha256(dados).hexdigest())
        self.assertEqual(r["size"], len(dados))

    def test_arquivo_vazio(self):
        caminho = self._temp(b"")
        r = hash_identify.hash_file(caminho)
        self.assertEqual(r["md5"], "d41d8cd98f00b204e9800998ecf8427e")
        self.assertEqual(
            r["sha1"], "da39a3ee5e6b4b0d3255bfef95601890afd80709"
        )
        self.assertEqual(
            r["sha256"],
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        )
        self.assertEqual(r["size"], 0)

    def test_cli_stdout(self):
        dados = b"saida json no stdout"
        caminho = self._temp(dados)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            codigo = hash_identify.main([caminho])
        self.assertEqual(codigo, 0)
        r = json.loads(buf.getvalue())
        self.assertEqual(r["size"], len(dados))
        self.assertEqual(r["sha256"], hashlib.sha256(dados).hexdigest())

    def test_cli_arquivo_saida(self):
        dados = b"saida em arquivo"
        caminho = self._temp(dados)
        saida = caminho + ".json"
        self.addCleanup(
            lambda: os.path.exists(saida) and os.unlink(saida)
        )
        codigo = hash_identify.main([caminho, "-o", saida])
        self.assertEqual(codigo, 0)
        with open(saida, encoding="utf-8") as f:
            r = json.load(f)
        self.assertEqual(r["md5"], hashlib.md5(dados).hexdigest())


if __name__ == "__main__":
    unittest.main()
