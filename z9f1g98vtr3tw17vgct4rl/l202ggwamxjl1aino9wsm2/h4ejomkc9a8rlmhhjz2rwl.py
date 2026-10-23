"""Testes do l202ggwamxjl1aino9wsm2 (fixtures sinteticas)."""

import importlib.util
import json
import os
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def load_module():
    spec = importlib.util.spec_from_file_location(
        "clone_assemble", os.path.join(HERE, "22c0lopwh84k1l6gfvp25e.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = load_module()

ESQUELETO = '''"""Esqueleto."""
def beh_001_abre_socket():
    """abre socket."""
    # TODO: implementar
    raise NotImplementedError("BEH-001: pendente")


def beh_002_cria_arquivo():
    """cria arquivo."""
    # TODO: implementar
    raise NotImplementedError("BEH-002: pendente")
'''

TEMPLATES = [
    {"api": "socket", "categoria": "rede", "comportamento": "BEH-001",
     "funcao": "sub_401000", "evidencia": "EV-001",
     "codigo": "import socket\ns = socket.socket()"},
    {"api": "CreateFileA", "categoria": "arquivo",
     "comportamento": "BEH-999", "funcao": "", "evidencia": "",
     "codigo": "open(caminho)"},
]


class TestBehDaFuncao(unittest.TestCase):
    def test_extracao(self):
        self.assertEqual(mod.beh_da_funcao("beh_001_abre_socket"), "BEH-001")
        self.assertEqual(mod.beh_da_funcao("beh_042_x"), "BEH-042")

    def test_sem_beh(self):
        self.assertIsNone(mod.beh_da_funcao("funcao_comum"))


class TestMonta(unittest.TestCase):
    def test_injecao(self):
        codigo, funcoes, nao = mod.monta(ESQUELETO, TEMPLATES)
        self.assertIn("s = socket.socket()", codigo)
        self.assertIn("# --- template: socket (evidencia EV-001) ---", codigo)
        self.assertNotIn('raise NotImplementedError("BEH-001', codigo)

    def test_stub_mantido(self):
        codigo, funcoes, nao = mod.monta(ESQUELETO, TEMPLATES)
        self.assertIn('raise NotImplementedError("BEH-002: pendente")', codigo)
        st = {f["beh"]: f["status"] for f in funcoes}
        self.assertEqual(st["BEH-001"], "montada")
        self.assertEqual(st["BEH-002"], "stub")

    def test_nao_aplicados(self):
        codigo, funcoes, nao = mod.monta(ESQUELETO, TEMPLATES)
        self.assertEqual(len(nao), 1)
        self.assertEqual(nao[0]["api"], "CreateFileA")

    def test_codigo_valido(self):
        codigo, funcoes, nao = mod.monta(ESQUELETO, TEMPLATES)
        compile(codigo, "<clone>", "exec")

    def test_sem_templates(self):
        codigo, funcoes, nao = mod.monta(ESQUELETO, [])
        self.assertIn("NotImplementedError", codigo)
        self.assertTrue(all(f["status"] == "stub" for f in funcoes))


class TestCli(unittest.TestCase):
    def test_outdir(self):
        with tempfile.TemporaryDirectory() as d:
            sk = os.path.join(d, "esq.py")
            tp = os.path.join(d, "tpl.json")
            out = os.path.join(d, "clone")
            with open(sk, "w", encoding="utf-8") as f:
                f.write(ESQUELETO)
            with open(tp, "w", encoding="utf-8") as f:
                json.dump({"templates": TEMPLATES}, f)
            mod.main(["--skeleton", sk, "--templates", tp, "--outdir", out])
            for nome in ("clone.py", "README.md", "montagem.json"):
                self.assertTrue(os.path.isfile(os.path.join(out, nome)),
                                nome)
            with open(os.path.join(out, "montagem.json"),
                      encoding="utf-8") as f:
                man = json.load(f)
            self.assertEqual(man["resumo"], {"montadas": 1, "stubs": 1})
            with open(os.path.join(out, "README.md"),
                      encoding="utf-8") as f:
                self.assertIn("beh_002_cria_arquivo", f.read())


if __name__ == "__main__":
    unittest.main()
