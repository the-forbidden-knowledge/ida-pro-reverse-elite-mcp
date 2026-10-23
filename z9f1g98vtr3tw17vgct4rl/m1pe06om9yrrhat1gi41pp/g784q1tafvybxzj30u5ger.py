"""Testes do m1pe06om9yrrhat1gi41pp (fixtures sinteticas)."""

import importlib.util
import json
import os
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def load_module():
    spec = importlib.util.spec_from_file_location(
        "clone_verify", os.path.join(HERE, "f0y1cl3d7nbg2h9nrzx0dw.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = load_module()

ORIG = [
    {"id": "BEH-001", "descricao": "abre socket",
     "pre_condicoes": "", "efeitos": ""},
    {"id": "BEH-002", "descricao": "cria arquivo temporario",
     "pre_condicoes": "", "efeitos": ""},
]
CLONE_OK = [
    {"id": "C-1", "descricao": "Abre   Socket",  # case/espaco variam
     "pre_condicoes": "", "efeitos": ""},
    {"id": "C-2", "descricao": "cria arquivo temporario",
     "pre_condicoes": "", "efeitos": ""},
]
CLONE_GAP = [
    {"id": "C-1", "descricao": "abre socket",
     "pre_condicoes": "", "efeitos": ""},
]
CLONE_EXTRA = ORIG + [
    {"id": "C-9", "descricao": "faz algo a mais",
     "pre_condicoes": "", "efeitos": ""},
]


class TestCompara(unittest.TestCase):
    def test_clonado_100(self):
        cob, fal, ext = mod.compara(ORIG, CLONE_OK)
        self.assertEqual(len(cob), 2)
        self.assertEqual(fal, [])
        self.assertEqual(ext, [])
        self.assertEqual(mod.veredito(fal, ext), "CLONADO 100%")

    def test_gap(self):
        cob, fal, ext = mod.compara(ORIG, CLONE_GAP)
        self.assertEqual(len(cob), 1)
        self.assertEqual(len(fal), 1)
        self.assertEqual(fal[0]["id"], "BEH-002")
        self.assertIn("GAPS", mod.veredito(fal, ext))

    def test_extra(self):
        cob, fal, ext = mod.compara(ORIG, CLONE_EXTRA)
        self.assertEqual(len(ext), 1)
        self.assertEqual(ext[0]["descricao"], "faz algo a mais")
        self.assertIn("DIVERGENCIAS", mod.veredito(fal, ext))

    def test_normaliza(self):
        self.assertEqual(mod.normaliza("  Abre\tSocket "), "abre socket")

    def test_listas_vazias(self):
        cob, fal, ext = mod.compara([], [])
        self.assertEqual((cob, fal, ext), ([], [], []))
        self.assertEqual(mod.veredito(fal, ext), "CLONADO 100%")


class TestArtefatos(unittest.TestCase):
    def test_hash_arquivo_e_dir(self):
        with tempfile.TemporaryDirectory() as d:
            a = os.path.join(d, "a.txt")
            sub = os.path.join(d, "sub")
            os.makedirs(sub)
            b = os.path.join(sub, "b.txt")
            with open(a, "w") as f:
                f.write("ola")
            with open(b, "w") as f:
                f.write("mundo")
            arts = mod.coleta_artefatos([a, sub])
            self.assertEqual(len(arts), 2)
            for x in arts:
                self.assertEqual(len(x["sha256"]), 64)
            # deterministico
            arts2 = mod.coleta_artefatos([a, sub])
            self.assertEqual(arts, arts2)

    def test_inexistente_ignorado(self):
        self.assertEqual(mod.coleta_artefatos(["/nao/existe"]), [])


class TestCli(unittest.TestCase):
    def test_relatorio(self):
        with tempfile.TemporaryDirectory() as d:
            so = os.path.join(d, "orig.json")
            sc = os.path.join(d, "clone.json")
            art = os.path.join(d, "clone.py")
            out = os.path.join(d, "rel.json")
            with open(so, "w", encoding="utf-8") as f:
                json.dump({"comportamentos": ORIG}, f)
            with open(sc, "w", encoding="utf-8") as f:
                json.dump({"comportamentos": CLONE_OK}, f)
            with open(art, "w", encoding="utf-8") as f:
                f.write("# clone\n")
            mod.main(["--original", so, "--clone", sc,
                      "--artefatos", art, "--output", out])
            with open(out, encoding="utf-8") as f:
                rel = json.load(f)
            self.assertEqual(rel["veredito"], "CLONADO 100%")
            self.assertEqual(rel["cobertura_pct"], 100.0)
            self.assertEqual(len(rel["artefatos"]), 1)


if __name__ == "__main__":
    unittest.main()
