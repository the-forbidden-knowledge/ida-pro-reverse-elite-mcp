"""Testes do gtbs546sxv6oa5wmwazir3 (fixtures sinteticas)."""

import importlib.util
import json
import os
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def load_module():
    spec = importlib.util.spec_from_file_location(
        "api_map_emit", os.path.join(HERE, "u4u8665mu3tq6orbfr1f6h.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = load_module()

MAPA = {"mapa": {
    "BEH-001": {"descricao": "abre socket", "funcoes": ["sub_401000"],
                "evidencias": [
                    {"id": "EV-001", "funcao": "sub_401000",
                     "descricao": "chama socket() e depois connect()"},
                    {"id": "EV-002", "funcao": "sub_401000",
                     "descricao": "grava log com WriteFileA"},
                ]},
    "BEH-002": {"descricao": "persiste no registro",
                "funcoes": ["sub_402000"],
                "evidencias": [
                    {"id": "EV-003", "funcao": "sub_402000",
                     "descricao": "RegOpenKeyExW e RegSetValueEx"},
                ]},
}}


class TestNormaliza(unittest.TestCase):
    def test_sufixo_aw(self):
        self.assertEqual(mod.normaliza_api("CreateFileA"), "createfile")
        self.assertEqual(mod.normaliza_api("RegSetValueExW"), "regsetvalue")

    def test_apis_no_texto(self):
        achadas = mod.apis_no_texto("chama socket() e connect()")
        self.assertIn("socket", achadas)
        self.assertIn("connect", achadas)

    def test_sem_falso_positivo(self):
        # "send" nao deve casar dentro de outra palavra
        self.assertNotIn("send", mod.apis_no_texto("o sender enviou"))


class TestEmite(unittest.TestCase):
    def test_templates_das_evidencias(self):
        t = mod.emite_templates(MAPA["mapa"])
        apis = [x["api"] for x in t]
        self.assertIn("socket", apis)
        self.assertIn("connect", apis)
        self.assertIn("WriteFile", apis)
        self.assertIn("RegOpenKeyEx", apis)
        self.assertIn("RegSetValueEx", apis)

    def test_vinculo_comportamento(self):
        t = mod.emite_templates(MAPA["mapa"])
        s = [x for x in t if x["api"] == "socket"][0]
        self.assertEqual(s["comportamento"], "BEH-001")
        self.assertEqual(s["evidencia"], "EV-001")
        self.assertEqual(s["origem"], "evidencia")

    def test_sem_duplicata(self):
        mapa2 = {"BEH-001": {"evidencias": [
            {"id": "EV-1", "funcao": "f", "descricao": "socket socket"}]}}
        t = mod.emite_templates(mapa2)
        self.assertEqual(len([x for x in t if x["api"] == "socket"]), 1)

    def test_apis_extras(self):
        t = mod.emite_templates({}, ["CreateMutexA"])
        self.assertEqual(len(t), 1)
        self.assertEqual(t[0]["api"], "CreateMutex")
        self.assertEqual(t[0]["origem"], "manual")

    def test_api_desconhecida_ignorada(self):
        t = mod.emite_templates({}, ["FuncaoInexistente123"])
        self.assertEqual(t, [])

    def test_codigo_nao_vazio(self):
        t = mod.emite_templates(MAPA["mapa"])
        for x in t:
            self.assertTrue(x["codigo"].strip())


class TestCli(unittest.TestCase):
    def test_json_e_snippet(self):
        with tempfile.TemporaryDirectory() as d:
            mp = os.path.join(d, "mapa.json")
            out = os.path.join(d, "tpl.json")
            snip = os.path.join(d, "trechos.py")
            with open(mp, "w", encoding="utf-8") as f:
                json.dump(MAPA, f)
            mod.main(["--map", mp, "--output", out, "--snippet", snip])
            with open(out, encoding="utf-8") as f:
                dados = json.load(f)
            self.assertTrue(dados["templates"])
            with open(snip, encoding="utf-8") as f:
                conteudo = f.read()
            compile(conteudo, snip, "exec")
            self.assertIn("# API: socket", conteudo)


if __name__ == "__main__":
    unittest.main()
