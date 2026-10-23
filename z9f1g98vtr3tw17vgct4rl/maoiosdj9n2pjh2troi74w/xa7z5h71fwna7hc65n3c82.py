#!/usr/bin/env python3
"""Testes do maoiosdj9n2pjh2troi74w. Fixtures sinteticas geradas no proprio teste."""
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
_mx_xorsearch = _loadmod("tdszw6xy7o8ndrx31j4vjw.py")
english_score, search, xor_decode, main = _mx_xorsearch.english_score, _mx_xorsearch.search, _mx_xorsearch.xor_decode, _mx_xorsearch.main


class TestXorSearch(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.plain = (b"The quick brown fox jumps over the lazy dog. "
                      b"Pack my box with five dozen liquor jugs! " * 3)
        self.key = 0x42
        self.cipher = bytes(b ^ self.key for b in self.plain)
        self.path = os.path.join(self.tmp.name, "enc.bin")
        with open(self.path, "wb") as f:
            f.write(self.cipher)

    def tearDown(self):
        self.tmp.cleanup()

    def test_finds_correct_key(self):
        result = search(self.cipher, top=5)
        self.assertEqual(result["best_key"], self.key)
        keys = [r["key"] for r in result["results"]]
        self.assertIn(self.key, keys)

    def test_preview_matches_plaintext(self):
        result = search(self.cipher, top=1, preview=20)
        self.assertEqual(result["results"][0]["preview"][:19],
                         self.plain[:19].decode())

    def test_random_bytes_low_score(self):
        import random
        random.seed(7)
        noise = bytes(random.randrange(256) for _ in range(600))
        result = search(noise, top=1)
        self.assertLess(result["results"][0]["score"], 0.5)

    def test_english_score_orders(self):
        self.assertGreater(english_score(self.plain), english_score(self.cipher))

    def test_xor_roundtrip(self):
        self.assertEqual(xor_decode(xor_decode(self.plain, 0x99), 0x99), self.plain)

    def test_cli_output_file(self):
        out = os.path.join(self.tmp.name, "out.json")
        rc = main([self.path, "--output", out, "--top", "3"])
        self.assertEqual(rc, 0)
        with open(out, encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["best_key"], self.key)
        self.assertEqual(len(data["results"]), 3)


if __name__ == "__main__":
    unittest.main()
