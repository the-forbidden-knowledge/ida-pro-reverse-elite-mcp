#!/usr/bin/env python3
"""Testes do ho34my4hrz5m5a5kipq3k1. Fixtures sinteticas geradas no proprio teste."""
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
_mx_decode_emulate = _loadmod("hzjr418t8gos1vsg2os9uq.py")
apply_op, emulate, rol_byte, ror_byte, main = _mx_decode_emulate.apply_op, _mx_decode_emulate.emulate, _mx_decode_emulate.rol_byte, _mx_decode_emulate.ror_byte, _mx_decode_emulate.main


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f)


class TestDecodeEmulate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.plain = b"the secret payload is hidden here!!" * 4
        # codifica: xor 0xAA depois add 3
        enc = bytes((b ^ 0xAA) for b in self.plain)
        self.cipher = bytes((b + 3) & 0xFF for b in enc)
        self.bin = os.path.join(self.tmp.name, "enc.bin")
        with open(self.bin, "wb") as f:
            f.write(self.cipher)
        self.dsl_path = os.path.join(self.tmp.name, "dsl.json")
        write_json(self.dsl_path, {"ops": [
            {"op": "sub", "key": 3},
            {"op": "xor", "key": 0xAA},
        ]})

    def tearDown(self):
        self.tmp.cleanup()

    def test_roundtrip(self):
        with open(self.dsl_path, encoding="utf-8") as f:
            dsl = json.load(f)
        self.assertEqual(emulate(self.cipher, dsl), self.plain)

    def test_partial_range(self):
        data = b"AAAA" + self.cipher + b"BBBB"
        dsl = {"ops": [{"op": "sub", "key": 3, "start": 4,
                        "length": len(self.cipher)},
                       {"op": "xor", "key": 0xAA, "start": 4,
                        "length": len(self.cipher)}]}
        out = emulate(data, dsl)
        self.assertEqual(out[:4], b"AAAA")
        self.assertEqual(out[-4:], b"BBBB")
        self.assertEqual(out[4:-4], self.plain)

    def test_rotl_rotr_inverse(self):
        data = bytes(range(256))
        self.assertEqual(ror_byte(rol_byte(0xB3, 3), 3), 0xB3)
        out = emulate(data, {"ops": [{"op": "rol", "key": 3},
                                     {"op": "ror", "key": 3}]})
        self.assertEqual(out, data)

    def test_unknown_op_raises(self):
        with self.assertRaises(ValueError):
            apply_op(b"abc", {"op": "mul", "key": 2})

    def test_cli(self):
        out = os.path.join(self.tmp.name, "dec.bin")
        rc = main([self.bin, self.dsl_path, "--output", out])
        self.assertEqual(rc, 0)
        with open(out, "rb") as f:
            self.assertEqual(f.read(), self.plain)


if __name__ == "__main__":
    unittest.main()
