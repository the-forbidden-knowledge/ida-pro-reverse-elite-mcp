#!/usr/bin/env python3
"""Testes do k1zlgokezxoi94chw88qpu. Fixtures sinteticas geradas no proprio teste."""
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
_mx_unpack_compare = _loadmod("ojg3mycarz10qyln7fvo0m.py")
compare, load_report, main = _mx_unpack_compare.compare, _mx_unpack_compare.load_report, _mx_unpack_compare.main


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f)


class TestUnpackCompare(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.before = os.path.join(self.tmp.name, "before.json")
        self.after = os.path.join(self.tmp.name, "after.json")
        write_json(self.before, {
            "avg_entropy": 7.85, "imports": 12, "sections": 4, "size": 45056,
        })
        write_json(self.after, {
            "avg_entropy": 5.20, "imports": 186, "sections": 8, "size": 196608,
        })

    def tearDown(self):
        self.tmp.cleanup()

    def test_success_case(self):
        result = compare(load_report(self.before), load_report(self.after))
        self.assertTrue(result["unpacked"])
        self.assertGreaterEqual(result["score"], 3)
        self.assertGreater(result["metrics"]["entropy_drop"], 0)
        self.assertTrue(any("imports" in r for r in result["reasons"]))

    def test_failure_case(self):
        write_json(self.after, {
            "avg_entropy": 7.80, "imports": 12, "sections": 4, "size": 45056,
        })
        result = compare(load_report(self.before), load_report(self.after))
        self.assertFalse(result["unpacked"])
        self.assertEqual(result["reasons"], [])

    def test_partial_case(self):
        write_json(self.after, {
            "avg_entropy": 7.10, "imports": 30, "sections": 4, "size": 45056,
        })
        result = compare(load_report(self.before), load_report(self.after))
        self.assertFalse(result["unpacked"])
        self.assertGreater(result["score"], 0)

    def test_cli_stdout(self):
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main([self.before, self.after])
        self.assertEqual(rc, 0)
        data = json.loads(buf.getvalue())
        self.assertTrue(data["unpacked"])

    def test_cli_output_file(self):
        out = os.path.join(self.tmp.name, "out.json")
        rc = main([self.before, self.after, "--output", out])
        self.assertEqual(rc, 0)
        data = load_report(out)
        self.assertTrue(data["unpacked"])


if __name__ == "__main__":
    unittest.main()
