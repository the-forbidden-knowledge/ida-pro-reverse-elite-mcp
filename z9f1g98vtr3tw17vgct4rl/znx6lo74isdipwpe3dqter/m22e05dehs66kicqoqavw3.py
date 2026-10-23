#!/usr/bin/env python3
"""Testes do znx6lo74isdipwpe3dqter. Fixtures sinteticas geradas no proprio teste."""
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
_mx_technique_map = _loadmod("fx2v25vmo0nauju9iegfj3.py")
classify, main = _mx_technique_map.classify, _mx_technique_map.main


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f)


class TestTechniqueMap(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "apis.json")

    def tearDown(self):
        self.tmp.cleanup()

    def test_injection_top(self):
        result = classify(["OpenProcess", "VirtualAllocEx", "WriteProcessMemory",
                           "CreateRemoteThread"])
        self.assertEqual(result["top"], "injecao")
        inj = result["techniques"][0]
        self.assertEqual(inj["name"], "injecao")
        self.assertAlmostEqual(inj["score"], 4 / 6, places=2)

    def test_keylogging(self):
        result = classify(["GetAsyncKeyState", "GetForegroundWindow",
                           "SetWindowsHookExW"])
        self.assertEqual(result["top"], "keylogging")

    def test_persistence(self):
        result = classify(["RegOpenKeyExA", "RegSetValueExA", "CreateServiceA"])
        names = [t["name"] for t in result["techniques"]]
        self.assertIn("persistencia", names)

    def test_empty(self):
        result = classify([])
        self.assertEqual(result["techniques"], [])
        self.assertIsNone(result["top"])

    def test_sorted_by_score(self):
        result = classify(["OpenProcess", "VirtualAllocEx", "WriteProcessMemory",
                           "CreateRemoteThread", "GetAsyncKeyState"])
        scores = [t["score"] for t in result["techniques"]]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_cli(self):
        write_json(self.path, {"apis": ["CreateProcessA", "WriteProcessMemory",
                                        "SetThreadContext", "ResumeThread"]})
        out = os.path.join(self.tmp.name, "out.json")
        rc = main([self.path, "--output", out])
        self.assertEqual(rc, 0)
        with open(out, encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["top"], "hollowing")


if __name__ == "__main__":
    unittest.main()
