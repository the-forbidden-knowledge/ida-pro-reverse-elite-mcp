#!/usr/bin/env python3
"""Monta o projeto do clone: esqueleto (lab 49) + templates (lab 50).

Entrada: esqueleto .py do lab 49 e templates JSON do lab 50.
Saida: diretorio com clone.py (stubs preenchidos com os trechos das
       APIs mapeadas), README.md de montagem e montagem.json.
Funcoes sem template mantem o NotImplementedError (status "stub").
"""

import argparse
import json
import os
import re
import sys

RE_DEF = re.compile(r"^def\s+(\w+)\s*\(\s*\)\s*:")
RE_BEH = re.compile(r"beh_(\d+)", re.IGNORECASE)
RE_RAISE = re.compile(r"^(\s*)raise\s+NotImplementedError")


def beh_da_funcao(nome):
    """Extrai BEH-001 do nome beh_001_xxx."""
    m = RE_BEH.search(nome)
    return "BEH-%03d" % int(m.group(1)) if m else None


def monta(esqueleto, templates):
    """Retorna (linhas_clone, funcoes, nao_aplicados)."""
    por_beh = {}
    for t in templates or []:
        por_beh.setdefault(t.get("comportamento"), []).append(t)

    linhas_out = []
    funcoes = []
    atual = None  # {"nome":..., "beh":...}
    aplicados = set()

    for linha in esqueleto.splitlines():
        mdef = RE_DEF.match(linha)
        if mdef:
            atual = {"nome": mdef.group(1),
                     "beh": beh_da_funcao(mdef.group(1)),
                     "status": "stub", "templates": []}
            funcoes.append(atual)
            linhas_out.append(linha)
            continue
        mraise = RE_RAISE.match(linha)
        if mraise and atual is not None:
            tpl = por_beh.get(atual["beh"], [])
            if tpl:
                indent = mraise.group(1)
                for t in tpl:
                    aplicados.add(id(t))
                    atual["templates"].append(t["api"])
                    linhas_out.append(
                        "%s# --- template: %s (evidencia %s) ---"
                        % (indent, t["api"], t.get("evidencia") or "-"))
                    for cl in t["codigo"].splitlines():
                        linhas_out.append(indent + cl if cl.strip() else "")
                linhas_out.append(
                    "%s# TODO: validar o trecho acima contra as evidencias"
                    % indent)
                atual["status"] = "montada"
            else:
                linhas_out.append(linha)
            continue
        linhas_out.append(linha)

    nao_aplicados = [t for t in templates or [] if id(t) not in aplicados]
    return "\n".join(linhas_out) + "\n", funcoes, nao_aplicados


def gera_readme(funcoes, nao_aplicados):
    montadas = [f for f in funcoes if f["status"] == "montada"]
    stubs = [f for f in funcoes if f["status"] == "stub"]
    l = ["# Montagem do clone", "",
         "Funcoes montadas: %d | stubs pendentes: %d"
         % (len(montadas), len(stubs)), ""]
    if montadas:
        l.append("## Montadas")
        for f in montadas:
            l.append("- `%s` (%s): %s"
                    % (f["nome"], f["beh"], ", ".join(f["templates"])))
        l.append("")
    if stubs:
        l.append("## Stubs (implementar manualmente)")
        for f in stubs:
            l.append("- `%s` (%s)" % (f["nome"], f["beh"]))
        l.append("")
    if nao_aplicados:
        l.append("## Templates nao aplicados (sem funcao correspondente)")
        for t in nao_aplicados:
            l.append("- %s (comportamento %s)"
                    % (t["api"], t.get("comportamento")))
        l.append("")
    return "\n".join(l)


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Monta o projeto do clone (esqueleto + templates).")
    ap.add_argument("--skeleton", required=True, help="esqueleto .py do lab 49")
    ap.add_argument("--templates", required=True, help="templates JSON do lab 50")
    ap.add_argument("--outdir", required=True, help="diretorio de saida")
    ap.add_argument("--nome", default="clone.py", help="nome do arquivo do clone")
    args = ap.parse_args(argv)

    with open(args.skeleton, encoding="utf-8") as f:
        esqueleto = f.read()
    with open(args.templates, encoding="utf-8") as f:
        templates = json.load(f).get("templates", [])

    codigo, funcoes, nao_aplicados = monta(esqueleto, templates)

    os.makedirs(args.outdir, exist_ok=True)
    caminho = os.path.join(args.outdir, args.nome)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(codigo)
    with open(os.path.join(args.outdir, "README.md"), "w",
              encoding="utf-8") as f:
        f.write(gera_readme(funcoes, nao_aplicados))
    manifesto = {
        "funcoes": funcoes,
        "templates_nao_aplicados": [
            {"api": t["api"], "comportamento": t.get("comportamento")}
            for t in nao_aplicados],
        "resumo": {
            "montadas": sum(1 for f in funcoes if f["status"] == "montada"),
            "stubs": sum(1 for f in funcoes if f["status"] == "stub"),
        },
    }
    with open(os.path.join(args.outdir, "montagem.json"), "w",
              encoding="utf-8") as f:
        json.dump(manifesto, f, indent=2, ensure_ascii=False)
    sys.stdout.write("montado: %s (%d montadas, %d stubs)\n"
                     % (caminho, manifesto["resumo"]["montadas"],
                        manifesto["resumo"]["stubs"]))


if __name__ == "__main__":
    main()
