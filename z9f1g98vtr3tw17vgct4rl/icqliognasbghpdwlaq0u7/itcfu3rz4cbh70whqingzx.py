"""Testes do lab 11 — library-filter.

Fixtures: lista sintética de funções e padrões de biblioteca.
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
library_filter = _loadmod("kjifdy5ei4ewouwqln20jx.py")

FUNCOES = [
    "sub_401000",
    "j_malloc",
    "std__vector_push",
    "main_logic",
    "decrypt_payload",
    "nullsub_1",
]
PADROES = [r"^j_", r"^sub_", r"^nullsub_", r"std__"]


class TestLibraryFilter(unittest.TestCase):
    def _temp(self, obj):
        fd, caminho = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f)
        self.addCleanup(os.unlink, caminho)
        return caminho

    def test_classificacao(self):
        r = library_filter.classify(FUNCOES, PADROES)
        self.assertEqual(
            sorted(r["biblioteca"]),
            ["j_malloc", "nullsub_1", "std__vector_push", "sub_401000"],
        )
        self.assertEqual(sorted(r["autor"]), ["decrypt_payload", "main_logic"])

    def test_dicts(self):
        funcs = [{"name": n} for n in FUNCOES]
        r = library_filter.classify(funcs, PADROES)
        self.assertEqual(len(r["autor"]), 2)

    def test_sem_padroes(self):
        r = library_filter.classify(FUNCOES, [])
        self.assertEqual(r["biblioteca"], [])
        self.assertEqual(sorted(r["autor"]), sorted(FUNCOES))

    def test_padroes_no_json(self):
        caminho = self._temp(
            {"functions": FUNCOES, "library_patterns": PADROES}
        )
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            codigo = library_filter.main([caminho])
        self.assertEqual(codigo, 0)
        r = json.loads(buf.getvalue())
        self.assertEqual(len(r["biblioteca"]), 4)

    def test_pattern_cli(self):
        caminho = self._temp({"functions": FUNCOES})
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            codigo = library_filter.main(
                [caminho, "--pattern", r"^j_", "--pattern", r"^sub_"]
            )
        self.assertEqual(codigo, 0)
        r = json.loads(buf.getvalue())
        self.assertEqual(sorted(r["biblioteca"]), ["j_malloc", "sub_401000"])


if __name__ == "__main__":
    unittest.main()
