#!/usr/bin/env python3
"""Testes do lab 76 — audit2allow-loop (fixtures sintéticas)."""

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
    _mm = _ilu.module_from_spec(_sp); _sp.loader.exec_module(_mm)
    return _mm
_mx_audit2allow_loop = _loadmod("q05cre04wl0sxg2cqu8ap6.py")
parse_avc, to_allow, clusterizar, profile_binary, main = _mx_audit2allow_loop.parse_avc, _mx_audit2allow_loop.to_allow, _mx_audit2allow_loop.clusterizar, _mx_audit2allow_loop.profile_binary, _mx_audit2allow_loop.main

AVC1 = ('type=AVC msg=audit(1): avc: denied { read } for pid=100 '
        'comm="app" scontext=system_u:system_r:app_t:s0 '
        'tcontext=system_u:object_r:app_log_t:s0 tclass=file permissive=1')
AVC2 = ('type=AVC msg=audit(2): avc: denied { name_bind } for pid=101 '
        'comm="app" scontext=system_u:system_r:app_t:s0 '
        'tcontext=system_u:object_r:app_port_t:s0 tclass=tcp_socket permissive=1')
AVC3 = ('type=AVC msg=audit(3): avc: denied { getattr } for pid=102 '
        'comm="app" scontext=system_u:system_r:app_t:s0 '
        'tcontext=system_u:object_r:etc_t:s0 tclass=file permissive=1')
RUIM = 'type=SYSCALL msg=audit(4): arch=c000003e syscall=59 success=yes'


class TestParse(unittest.TestCase):
    def test_avc(self):
        a = parse_avc(AVC1)
        self.assertEqual(a["src"], "app_t")
        self.assertEqual(a["tgt"], "app_log_t")
        self.assertEqual(a["tclass"], "file")
        self.assertEqual(a["perms"], ["read"])

    def test_nao_avc(self):
        self.assertIsNone(parse_avc(RUIM))
        self.assertIsNone(parse_avc(""))


class TestAllow(unittest.TestCase):
    def test_regra(self):
        a = parse_avc(AVC1)
        self.assertEqual(to_allow(a), "allow app_t app_log_t:file { read };")


class TestCluster(unittest.TestCase):
    def test_macros(self):
        avcs = [parse_avc(x) for x in (AVC1, AVC2, AVC3)]
        clusters = clusterizar(avcs)
        macros = {c["macro"] for c in clusters}
        self.assertIn("logging_log_file", macros)
        self.assertIn("corenet_tcp_bind_all_ports", macros)
        self.assertIn("read_files_pattern", macros)

    def test_agrupa(self):
        avcs = [parse_avc(AVC1), parse_avc(AVC1)]
        clusters = clusterizar(avcs)
        self.assertEqual(len(clusters), 1)


class TestProfile(unittest.TestCase):
    def test_pipeline(self):
        r = profile_binary("\n".join([AVC1, AVC2, AVC3, RUIM]))
        self.assertEqual(r["denials"], 3)
        self.assertEqual(len(r["allows_cruas"]), 3)
        self.assertTrue(r["cobertura_total"])

    def test_vazio(self):
        r = profile_binary(RUIM)
        self.assertFalse(r["cobertura_total"])


class TestCLI(unittest.TestCase):
    def test_main(self):
        d = tempfile.mkdtemp()
        lp = os.path.join(d, "avc.log")
        out = os.path.join(d, "r.json")
        open(lp, "w").write("\n".join([AVC1, AVC2]))
        self.assertEqual(main([lp, "-o", out]), 0)
        dados = json.load(open(out, encoding="utf-8"))
        self.assertEqual(dados["denials"], 2)


if __name__ == "__main__":
    unittest.main()
