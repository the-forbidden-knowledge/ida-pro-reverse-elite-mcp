#!/usr/bin/env python3
"""class-dump: extrai classes/métodos Objective-C e gera headers .h.

Recebe descritores de classes (como os lidos das estruturas de runtime
do Mach-O) e reconstrói as declarações — o "mapa" do app: que classes
existem, que métodos expõem, que dados manipulam.
"""

import argparse
import json
import sys


def dump_ivar(ivar: dict) -> str:
    """Declara uma variável de instância: `Tipo * _nome;`."""
    tipo = ivar.get("tipo", "id")
    nome = ivar["nome"]
    if not tipo.endswith("*"):
        tipo += " *"
    return "    %s _%s;" % (tipo, nome)


def dump_method(method: dict) -> str:
    """Declara um método: `- (ret)nome:(tipo)arg ...;` ou `+ ...` para classe."""
    prefixo = "+" if method.get("kind") == "classe" else "-"
    retorno = method.get("retorno", "void")
    partes = method.get("partes", [])
    if not partes:
        return "%s (%s)%s;" % (prefixo, retorno, method["nome"])
    decl = "%s (%s)%s" % (prefixo, retorno, partes[0]["rotulo"])
    for parte in partes[1:]:
        decl += " %s:(%s)%s" % (parte["rotulo"], parte.get("tipo", "id"), parte.get("nome", "arg"))
    first = partes[0]
    if "nome" in first or "tipo" in first:
        decl += ":(%s)%s" % (first.get("tipo", "id"), first.get("nome", "arg"))
    return decl + ";"


def dump_class(cls: dict) -> str:
    """Gera o bloco @interface/@end de uma classe."""
    nome = cls["nome"]
    superclasse = cls.get("superclasse", "NSObject")
    protocolos = cls.get("protocolos", [])
    proto = " <%s>" % ", ".join(protocolos) if protocolos else ""
    linhas = ["@interface %s : %s%s" % (nome, superclasse, proto)]
    ivars = cls.get("ivars", [])
    if ivars:
        linhas.append("{")
        linhas.extend(dump_ivar(i) for i in ivars)
        linhas.append("}")
    for metodo in cls.get("metodos", []):
        linhas.append(dump_method(metodo))
    linhas.append("@end")
    return "\n".join(linhas)


def dump_all(classes: list) -> str:
    """Gera os headers de todas as classes, separados por linha em branco."""
    return "\n\n".join(dump_class(c) for c in classes) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="class-dump: gera headers .h de classes Obj-C.")
    ap.add_argument("entrada", help="JSON com a lista de classes")
    ap.add_argument("--saida", help="arquivo .h de saída (padrão: stdout)")
    args = ap.parse_args(argv)
    with open(args.entrada, encoding="utf-8") as f:
        classes = json.load(f)
    saida = dump_all(classes)
    if args.saida:
        with open(args.saida, "w", encoding="utf-8") as f:
            f.write(saida)
    else:
        print(saida, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
