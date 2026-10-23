#!/usr/bin/env python3
"""Testes do qp4ap4yltvkxhk5r3qrb0c. Fixtures sinteticas geradas no proprio teste."""
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
_mx_hollowing_detect = _loadmod("vw0n1su0rwakdd6buguz7l.py")
detect, main = _mx_hollowing_detect.detect, _mx_hollowing_detect.main


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f)


FULL = {
    "apis": ["CreateProcessA", "WriteProcessMemory", "SetThreadContext",
             "ResumeThread", "VirtualAllocEx"],
    "flags": [{"value": 4, "name": "CREATE_SUSPENDED",
               "context": "CreateProcessA dwCreationFlags"}],
}


class TestHollowingDetect(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "trace.json")
        write_json(self.path, FULL)

    def tearDown(self):
        self.tmp.cleanup()

    def test_full_detected(self):
        result = detect(FULL)
        self.assertTrue(result["detected"])
        self.assertGreaterEqual(len(result["indicators"]), 3)

    def test_no_suspended_flag(self):
        data = {"apis": FULL["apis"], "flags": []}
        result = detect(data)
        self.assertFalse(result["detected"])

    def test_no_createprocess(self):
        data = {"apis": ["WriteProcessMemory"], "flags": FULL["flags"]}
        result = detect(data)
        self.assertFalse(result["detected"])

    def test_unmap_variant(self):
        data = {"apis": ["CreateProcessW", "NtUnmapViewOfSection"],
                "flags": [{"value": 0x4, "name": "0x4",
                           "context": "CreateProcessW flags"}]}
        result = detect(data)
        self.assertTrue(result["detected"])

    def test_flag_by_name(self):
        data = {"apis": ["CreateProcessA", "WriteProcessMemory"],
                "flags": [{"value": 4, "name": "CREATE_SUSPENDED",
                           "context": "desconhecido"}]}
        result = detect(data)
        self.assertTrue(result["detected"])

    def test_cli(self):
        out = os.path.join(self.tmp.name, "out.json")
        rc = main([self.path, "--output", out])
        self.assertEqual(rc, 0)
        with open(out, encoding="utf-8") as f:
            data = json.load(f)
        self.assertTrue(data["detected"])


if __name__ == "__main__":
    unittest.main()
