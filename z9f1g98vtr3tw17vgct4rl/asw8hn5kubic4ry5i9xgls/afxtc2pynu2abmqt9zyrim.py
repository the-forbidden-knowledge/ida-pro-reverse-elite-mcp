"""Testes do lab 07 — anomaly-scan.

Fixtures: blob sintético com S-box do AES e magic ZIP em offsets
conhecidos.
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
anomaly_scan = _loadmod("k8sa05ag6rpks3b4t5lkt7.py")

AES_SBOX = bytes.fromhex("63 7c 77 7b f2 6b 6f c5 30 01 67 2b fe d7 ab 76")


class TestAnomalyScan(unittest.TestCase):
    def _temp(self, dados):
        fd, caminho = tempfile.mkstemp()
        with os.fdopen(fd, "wb") as f:
            f.write(dados)
        self.addCleanup(os.unlink, caminho)
        return caminho

    def test_encontra_assinaturas(self):
        dados = b"\x00" * 100 + AES_SBOX + b"\x00" * 50 + b"PK\x03\x04"
        caminho = self._temp(dados)
        r = anomaly_scan.scan_anomalies(caminho)
        por_nome = {a["nome"]: a for a in r}
        self.assertEqual(por_nome["AES S-box"]["offset"], 100)
        self.assertEqual(por_nome["AES S-box"]["tipo"], "cripto")
        self.assertEqual(por_nome["magic ZIP"]["offset"], 166)
        self.assertEqual(por_nome["magic ZIP"]["tipo"], "formato")

    def test_ordenado(self):
        dados = b"PK\x03\x04" + b"\x00" * 10 + AES_SBOX
        caminho = self._temp(dados)
        r = anomaly_scan.scan_anomalies(caminho)
        offsets = [a["offset"] for a in r]
        self.assertEqual(offsets, sorted(offsets))
        self.assertEqual(offsets[0], 0)

    def test_limpo(self):
        caminho = self._temp(b"\x00" * 64 + b"ABCDEFGH" * 8)
        r = anomaly_scan.scan_anomalies(caminho)
        self.assertEqual(r, [])

    def test_multiplas_ocorrencias(self):
        dados = AES_SBOX + b"\x00" * 8 + AES_SBOX
        caminho = self._temp(dados)
        r = anomaly_scan.scan_anomalies(caminho)
        ocorrencias = [a for a in r if a["nome"] == "AES S-box"]
        self.assertEqual([a["offset"] for a in ocorrencias], [0, 24])

    def test_cli(self):
        caminho = self._temp(b"\x00" * 10 + AES_SBOX)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            codigo = anomaly_scan.main([caminho])
        self.assertEqual(codigo, 0)
        r = json.loads(buf.getvalue())
        self.assertEqual(r[0]["nome"], "AES S-box")
        self.assertEqual(r[0]["offset"], 10)


if __name__ == "__main__":
    unittest.main()
