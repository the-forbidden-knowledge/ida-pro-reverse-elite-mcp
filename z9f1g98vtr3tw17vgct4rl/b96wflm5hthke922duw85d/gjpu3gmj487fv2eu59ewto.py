"""Testes do b96wflm5hthke922duw85d (fixtures sinteticas)."""

import importlib.util
import json
import os
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def load_module():
    spec = importlib.util.spec_from_file_location(
        "spec_to_skeleton", os.path.join(HERE, "ytimej1cglr0ty5g4fwjq3.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = load_module()

SPEC = {"comportamentos": [
    {"id": "BEH-001", "descricao": "abre socket",
     "pre_condicoes": "rede disponivel", "efeitos": "conexao estabelecida"},
    {"id": "BEH-002", "descricao": "cria arquivo temporario",
     "pre_condicoes": "", "efeitos": ""},
]}

MAPA = {"mapa": {
    "BEH-001": {"descricao": "abre socket", "funcoes": ["sub_401000"],
                "evidencias": [{"id": "EV-001", "descricao": "chama socket()",
                                 "funcao": "sub_401000"}]},
    "BEH-002": {"descricao": "cria arquivo temporario", "funcoes": [],
                "evidencias": []},
}}


class TestSlug(unittest.TestCase):
    def test_basico(self):
        self.assertEqual(mod.slug("Abre Socket!"), "abre_socket")

    def test_vazio(self):
        self.assertEqual(mod.slug("!!!"), "sem_nome")

    def test_limite(self):
        self.assertTrue(len(mod.slug("a" * 100)) <= 40)


class TestNomeFuncao(unittest.TestCase):
    def test_unico(self):
        usados = set()
        n1 = mod.nome_funcao("BEH-001", "abre socket", usados)
        n2 = mod.nome_funcao("BEH-001", "abre socket", usados)
        self.assertEqual(n1, "beh_001_abre_socket")
        self.assertNotEqual(n1, n2)


class TestGeraEsqueleto(unittest.TestCase):
    def test_estrutura(self):
        out = mod.gera_esqueleto(SPEC["comportamentos"], MAPA["mapa"])
        self.assertIn("def beh_001_abre_socket():", out)
        self.assertIn("def beh_002_cria_arquivo_temporario():", out)
        self.assertIn("raise NotImplementedError", out)

    def test_docstring_com_evidencia(self):
        out = mod.gera_esqueleto(SPEC["comportamentos"], MAPA["mapa"])
        self.assertIn("EV-001", out)
        self.assertIn("sub_401000", out)
        self.assertIn("Pre-condicoes: rede disponivel", out)

    def test_sem_mapa(self):
        out = mod.gera_esqueleto(SPEC["comportamentos"], {})
        self.assertIn("def beh_001_abre_socket():", out)
        self.assertIn("sem evidencia vinculada", out)

    def test_spec_vazia(self):
        out = mod.gera_esqueleto([], {})
        self.assertIn("Esqueleto do clone", out)
        self.assertNotIn("def beh_", out)

    def test_arquivo_saida(self):
        with tempfile.TemporaryDirectory() as d:
            sp = os.path.join(d, "spec.json")
            mp = os.path.join(d, "mapa.json")
            saida = os.path.join(d, "esqueleto.py")
            with open(sp, "w", encoding="utf-8") as f:
                json.dump(SPEC, f)
            with open(mp, "w", encoding="utf-8") as f:
                json.dump(MAPA, f)
            mod.main(["--spec", sp, "--map", mp, "--output", saida])
            with open(saida, encoding="utf-8") as f:
                conteudo = f.read()
            self.assertIn("def beh_001_abre_socket():", conteudo)
            # o esqueleto gerado precisa ser Python valido
            compile(conteudo, saida, "exec")


if __name__ == "__main__":
    unittest.main()
