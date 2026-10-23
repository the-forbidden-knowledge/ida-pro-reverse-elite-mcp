#!/usr/bin/env python3
"""Testes do 5fmv8fp8wxqb3id6swfzdb. Fixtures sinteticas geradas no proprio teste."""
import json
import os
import tempfile
import unittest

import importlib.util as _ilu
import os as _os
def _loadmod(_fname):
    _sp = _ilu.spec_from_file_location("_m", _os.path.join(_os.path.dirname(__file__), _fname))
    _mm = _ilu.module_from_spec(_sp)
    _sp.loader.exec_module(_mm)
    return _mm
_mx_xor_key_recover = _loadmod("ou9wnph48mbw4l5uta83j2.py")
derive_key, recover, repeating_xor, main = _mx_xor_key_recover.derive_key, _mx_xor_key_recover.recover, _mx_xor_key_recover.repeating_xor, _mx_xor_key_recover.main


class TestXorKeyRecover(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.key = b"SECRET"
        self.plain = (b"http://example.com/config.dat\x00user=admin&mode=debug"
                      b" trailing data here for scoring purposes 12345" * 2)
        self.cipher = repeating_xor(self.plain, self.key)
        self.path = os.path.join(self.tmp.name, "enc.bin")
        with open(self.path, "wb") as f:
            f.write(self.cipher)

    def tearDown(self):
        self.tmp.cleanup()

    def test_recovers_key(self):
        result = recover(self.cipher, b"http://e", max_key=8)
        self.assertEqual(result["key_hex"], self.key.hex())
        self.assertEqual(result["key_ascii"], "SECRET")
        self.assertEqual(result["key_length"], 6)
        self.assertEqual(result["offset"], 0)

    def test_recovers_key_at_offset(self):
        data = b"\x00\xff\xab" + self.cipher
        result = recover(data, b"http://e", max_key=8)
        self.assertEqual(result["offset"], 3)
        # chave vem rotacionada pela fase do offset, mas decodifica certo
        key = bytes.fromhex(result["key_hex"])
        decoded = repeating_xor(data, key)
        self.assertEqual(decoded[3:], self.plain)

    def test_derive_inconsistent(self):
        # fragmento errado -> nao recupera a chave verdadeira
        result = recover(self.cipher, b"zzzzzzz", max_key=8)
        self.assertNotEqual(result["key_hex"], self.key.hex())

    def test_derive_key_direct(self):
        key = derive_key(self.cipher, b"http://e", 6, 0)
        self.assertEqual(key, self.key)

    def test_partial_coverage_rejected(self):
        # fragmento de 4 bytes nao cobre chave de 6 -> None
        self.assertIsNone(derive_key(self.cipher, b"http", 6, 0))

    def test_cli_decode(self):
        out = os.path.join(self.tmp.name, "dec.bin")
        js = os.path.join(self.tmp.name, "out.json")
        rc = main([self.path, "--plaintext", "http://e", "--max-key", "8",
                   "--decode", out, "--output", js])
        self.assertEqual(rc, 0)
        with open(out, "rb") as f:
            self.assertEqual(f.read(), self.plain)
        with open(js, encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["key_ascii"], "SECRET")
        self.assertEqual(data["decoded_to"], out)


if __name__ == "__main__":
    unittest.main()
