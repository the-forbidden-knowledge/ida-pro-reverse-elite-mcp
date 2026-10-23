#!/usr/bin/env python3
"""Orquestrador CLONAR: executa o 9pd1ao2s9soicz7ndhxu9e ponta a ponta sobre um alvo.

Etapas:
  1. triagem      — z9f1g98vtr3tw17vgct4rl 01-08 sobre o arquivo (hash, strings, PE, entropia,
                   packer, imports, anomalias)
  2. leitura      — z9f1g98vtr3tw17vgct4rl 09-20 sobre o export JSON do IDA (--mrg3ynauhl4c6qu1go4jqo)
  3. desobfuscacao — z9f1g98vtr3tw17vgct4rl 26-29 sobre os bytes do alvo
     injecao      — z9f1g98vtr3tw17vgct4rl 31-34 (cadeias de injecao/hooking, mapa de tecnicas)
     bypass       — z9f1g98vtr3tw17vgct4rl 39-41 (defesas anti-analise, patches, TLS)
  4. reconstrucao — z9f1g98vtr3tw17vgct4rl 43-46 (spec, evidencias, ledger, cobertura)
  5. relatorio    — lab 48 (JSON + Markdown)

Cada etapa que falha vira {"erro": ...} sem derrubar o 9pd1ao2s9soicz7ndhxu9e.
Somente stdlib. Os z9f1g98vtr3tw17vgct4rl sao carregados pelo caminho do arquivo (importlib).
"""

import argparse
import datetime
import importlib.util
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LABS = os.path.join(BASE, "z9f1g98vtr3tw17vgct4rl")

# padroes de biblioteca para o lab 11 (filtro heuristico)
LIB_PATTERNS = ["msvc", "crt", "__", "std::", "operator", "sub_",
                "nullsub", "j_", "_main"]


def _carregar(pasta, modulo):
    caminho = os.path.join(LABS, pasta, modulo + ".py")
    nome = modulo.replace("-", "_")
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _etapa(nome, fn, *args, **kwargs):
    """Executa fn; falha isolada vira {"erro": ...}."""
    try:
        return fn(*args, **kwargs)
    except Exception as exc:
        return {"erro": "%s: %s" % (nome, exc)}


def _imports_dict(triagem, export):
    """Normaliza {dll: [apis]} do export do IDA ou da triagem (lab 06)."""
    if export:
        imp = (export.get("imports") or {})
        if isinstance(imp, dict):
            return imp
    t = (triagem or {}).get("imports") or {}
    if isinstance(t, dict):
        return t.get("imports") or {}
    return {}


def _todas_apis(imports):
    return [a for funcs in (imports or {}).values() for a in (funcs or [])]


def etapa_triagem(alvo):
    mod = _carregar("3qq3zegqt0tshdhx3r8c5x", "5mpyx89ub4ty7dy7sy95p9")
    return _etapa("triagem", mod.triage, alvo)


def etapa_leitura(export):
    if not export:
        return {"erro": "leitura: --mrg3ynauhl4c6qu1go4jqo nao fornecido"}
    functions = export.get("functions") or []
    strings = export.get("strings") or []
    imports = _imports_dict(None, export)
    apis = _todas_apis(imports)
    sem_disasm = {"erro": "requer texto de disassembly (ausente no export JSON)"}

    m09 = _carregar("9d0trqr4ktimjrds7goieb", "ll91zo7q1yljfftnf60qws")
    m10 = _carregar("xma5iz9yl37z2m496hj3d7", "i3kcp6jz9krnhnzl52k04y")
    m11 = _carregar("icqliognasbghpdwlaq0u7", "kjifdy5ei4ewouwqln20jx")
    m17 = _carregar("q2qasb3270wv09m270atgb", "x7zvgqybn3g6ytmtg801l1")
    m19 = _carregar("nlpdgtlczg6wtde0pjd1l6", "i72bqacdxje1wevomoisc9")

    # 09: rastreia as APIs mais citadas nas funcoes
    contagem = {}
    for f in functions:
        for c in f.get("calls") or []:
            contagem[c] = contagem.get(c, 0) + 1
    top_apis = sorted(contagem, key=contagem.get, reverse=True)[:12]
    rastros = {}
    for api in top_apis:
        rastros[api] = _etapa("lab-09", m09.trace, api, functions)

    # 10: navega pelas strings mais referenciadas
    entradas = {}
    for s in sorted(strings, key=lambda x: len(x.get("xrefs") or []),
                    reverse=True)[:20]:
        entradas[s.get("text", "")[:60]] = _etapa(
            "lab-10", m10.navigate, s.get("text", ""), export)

    leitura = {
        "9d0trqr4ktimjrds7goieb": rastros,
        "xma5iz9yl37z2m496hj3d7": entradas,
        "icqliognasbghpdwlaq0u7": _etapa("lab-11", m11.classify,
                                        functions, LIB_PATTERNS),
        "t87xkpvnhcvf29870buqso": dict(sem_disasm),
        "ek9h3ofp5ycv8o362sr889": dict(sem_disasm),
        "32b05wtz4ddq3mdlrh2e5v": dict(sem_disasm),
        "j01gg0kgnpmnuc33134uhy": dict(sem_disasm),
        "3q09u6xwsb2isw11q6gw0m": dict(sem_disasm),
        "q2qasb3270wv09m270atgb": _etapa("lab-17", m17.detect, apis),
        "u52ahn6smk2ewnh0uax885": dict(sem_disasm),
        "nlpdgtlczg6wtde0pjd1l6": _etapa("lab-19", m19.generate,
                                       functions, {}),
        "6w3vl9pthguka2b3jso8ee": dict(sem_disasm),
        "resumo": {"funcoes": len(functions), "strings": len(strings),
                   "apis": len(apis)},
    }
    return leitura


def etapa_desobfuscacao(dados):
    m26 = _carregar("maoiosdj9n2pjh2troi74w", "tdszw6xy7o8ndrx31j4vjw")
    m27 = _carregar("5fmv8fp8wxqb3id6swfzdb", "ou9wnph48mbw4l5uta83j2")
    m28 = _carregar("r0zx4dq741d2qo17exc2dm", "jsgipjcsv0qjxk2hcjnewc")
    return {
        "maoiosdj9n2pjh2troi74w": _etapa("lab-26", m26.search, dados, top=3),
        "5fmv8fp8wxqb3id6swfzdb": _etapa("lab-27", m27.recover,
                                         dados, "http"),
        "r0zx4dq741d2qo17exc2dm": _etapa("lab-28", m28.decode_dwords,
                                            dados),
        "ho34my4hrz5m5a5kipq3k1": {
            "erro": "requer DSL de decode (nao fornecida)"},
    }


def etapa_injecao(imports, calls):
    dados = {"imports": imports or {}, "calls": calls or []}
    m31 = _carregar("me3cvyro1kttvtrzo267a9", "uwk6wdc1p13aqg89iw400l")
    m32 = _carregar("lpoeo3swubbrqw122jmi2c", "ijkmsk91ju98zx9czr5t6e")
    m33 = _carregar("qp4ap4yltvkxhk5r3qrb0c", "vw0n1su0rwakdd6buguz7l")
    m34 = _carregar("znx6lo74isdipwpe3dqter", "fx2v25vmo0nauju9iegfj3")
    apis = _todas_apis(imports)
    return {
        "me3cvyro1kttvtrzo267a9": _etapa("lab-31", m31.detect, dados),
        "lpoeo3swubbrqw122jmi2c": _etapa("lab-32", m32.detect, dados),
        "qp4ap4yltvkxhk5r3qrb0c": _etapa("lab-33", m33.detect, dados),
        "znx6lo74isdipwpe3dqter": _etapa("lab-34", m34.classify, apis),
    }


def etapa_bypass(alvo, imports):
    m39 = _carregar("pft8rdap8iblilku7ni0y8", "fa4e7im8y6mam8z81jt2sg")
    m40 = _carregar("r7vkuk0bo7khhekzv7to9p", "k9blishyhhhwfov279ga8l")
    m41 = _carregar("ugqtqasgy279l2p5axv4is", "nd23wixgi0e1j565ctf8po")
    inventario = _etapa("lab-39", m39.build_inventory, imports)
    defesas = []
    if isinstance(inventario, dict):
        defesas = inventario.get("defesas") or []
    return {
        "pft8rdap8iblilku7ni0y8": inventario,
        "r7vkuk0bo7khhekzv7to9p": _etapa("lab-40", m40.build_plan, defesas),
        "ugqtqasgy279l2p5axv4is": _etapa("lab-41", m41.parse_tls, alvo),
    }


def _linhas_comportamento(injecao, bypass, leitura):
    """Deriva linhas de comportamento dos achados para a spec (lab 43)."""
    linhas = []
    tec = (injecao or {}).get("znx6lo74isdipwpe3dqter") or {}
    if isinstance(tec, dict):
        for t in tec.get("techniques") or []:
            if isinstance(t, dict) and t.get("score", 0) > 0:
                linhas.append(
                    "tecnica detectada: %s ;; alvo em execucao ;; "
                    "comportamento da tecnica reproduzido" % t.get("name"))
    det31 = (injecao or {}).get("me3cvyro1kttvtrzo267a9") or {}
    if det31.get("detected"):
        linhas.append("injecao via thread remota ;; processo alvo ativo ;; "
                      "thread remota criada no processo alvo")
    det33 = (injecao or {}).get("qp4ap4yltvkxhk5r3qrb0c") or {}
    if det33.get("detected"):
        linhas.append("process hollowing ;; processo filho suspenso ;; "
                      "codigo trocado antes de retomar")
    inv = (bypass or {}).get("pft8rdap8iblilku7ni0y8") or {}
    for d in (inv.get("defesas") or []):
        linhas.append("defesa anti-analise: %s (%s) ;; analise em curso ;; "
                      "defesa neutralizada" % (d.get("api"), d.get("categoria")))
    pats = (leitura or {}).get("q2qasb3270wv09m270atgb") or {}
    if isinstance(pats, dict):
        for p in pats.get("patterns") or []:
            linhas.append("padrao de API: %s ;; imports presentes ;; "
                          "intencao: %s" % (",".join(p.get("apis") or []),
                                            p.get("intent")))
    if not linhas:
        linhas.append("comportamento observado ;; alvo executado ;; "
                      "efeito registrado")
    return linhas


def etapa_reconstrucao(injecao, bypass, leitura):
    m43 = _carregar("d9yen9lqdjkquwp3jjyxep", "50x6rnt1dsaz2bm9gktlzd")
    m44 = _carregar("8umwx2402lcttqswbkb3mh", "oj6vfrk6ees32192x89s4v")
    m45 = _carregar("ga07t5mx7v0op0qahwb3uc", "m2ese22k0myo678menipp9")
    m46 = _carregar("m49dd353e4mwmhzhwd1xcp", "3vvtel22lho9l5gwbqhfbr")

    linhas = _linhas_comportamento(injecao, bypass, leitura)
    comportamentos = _etapa("lab-43", m43.parse_spec, linhas)

    evidencias = []
    if isinstance(comportamentos, list):
        rastros = (leitura or {}).get("9d0trqr4ktimjrds7goieb") or {}
        for i, c in enumerate(comportamentos):
            funcao = ""
            if isinstance(rastros, dict) and rastros:
                funcao = next(iter(rastros))
            evidencias.append({
                "id": "EV-%03d" % (i + 1),
                "comportamento": c.get("id"),
                "descricao": "achado do 9pd1ao2s9soicz7ndhxu9e para %s" % c.get("id"),
                "funcao": funcao,
            })
    mapa = _etapa("lab-44", m44.build_map, comportamentos, evidencias)
    ledger = _etapa("lab-45", m45.build_ledger,
                    mapa.get("mapa") if isinstance(mapa, dict) else {})
    cobertura = _etapa("lab-46", m46.verify, ledger)
    return {
        "d9yen9lqdjkquwp3jjyxep": comportamentos,
        "8umwx2402lcttqswbkb3mh": mapa,
        "ga07t5mx7v0op0qahwb3uc": ledger,
        "m49dd353e4mwmhzhwd1xcp": cobertura,
    }


def _gravar_json(caminho, dados):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)


def executar(alvo, ida_export=None, saida="clone-out"):
    """Roda o 9pd1ao2s9soicz7ndhxu9e completo. Retorna o caminho do diretorio de saida."""
    os.makedirs(saida, exist_ok=True)

    triagem = etapa_triagem(alvo)
    _gravar_json(os.path.join(saida, "triagem.json"), triagem)

    export = None
    if ida_export:
        try:
            with open(ida_export, encoding="utf-8") as f:
                export = json.load(f)
        except Exception as exc:
            export = None
            leitura = {"erro": "mrg3ynauhl4c6qu1go4jqo: %s" % exc}
        if export is not None:
            leitura = etapa_leitura(export)
    else:
        leitura = {"erro": "leitura: --mrg3ynauhl4c6qu1go4jqo nao fornecido"}
    _gravar_json(os.path.join(saida, "leitura.json"), leitura)

    with open(alvo, "rb") as f:
        dados = f.read()
    desobf = etapa_desobfuscacao(dados)
    _gravar_json(os.path.join(saida, "desobfuscacao.json"), desobf)

    imports = _imports_dict(triagem, export)
    calls = []
    if export:
        for fn in export.get("functions") or []:
            for c in fn.get("calls") or []:
                calls.append([fn.get("name", ""), c])
    injecao = etapa_injecao(imports, calls)
    _gravar_json(os.path.join(saida, "injecao.json"), injecao)

    bypass = etapa_bypass(alvo, imports)
    _gravar_json(os.path.join(saida, "bypass.json"), bypass)

    reconstrucao = etapa_reconstrucao(injecao, bypass, leitura)
    _gravar_json(os.path.join(saida, "reconstrucao.json"), reconstrucao)

    # relatorio final (lab 48)
    m48 = _carregar("krsi0v4p4a8251u4z853pm", "hgrtba8s3eyyyd8ujqgex1")
    manifest = {
        "triagem": os.path.join(saida, "triagem.json"),
        "leitura": os.path.join(saida, "leitura.json"),
        "desobfuscacao": os.path.join(saida, "desobfuscacao.json"),
        "injecao": os.path.join(saida, "injecao.json"),
        "bypass": os.path.join(saida, "bypass.json"),
        "reconstrucao": os.path.join(saida, "reconstrucao.json"),
    }
    rel = _etapa("lab-48", m48.build_report, manifest)
    rel["alvo"] = os.path.basename(alvo)
    rel["gerado_em"] = datetime.datetime.now().isoformat(timespec="seconds")
    _gravar_json(os.path.join(saida, "relatorio.json"), rel)
    try:
        md = m48.to_markdown(rel)
    except Exception as exc:
        md = "# Relatorio CLONAR\n\n{\"erro\": \"%s\"}\n" % exc
    with open(os.path.join(saida, "relatorio.md"), "w",
              encoding="utf-8") as f:
        f.write(md)
    return saida


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Orquestrador CLONAR: 9pd1ao2s9soicz7ndhxu9e ponta a ponta sobre um alvo.")
    ap.add_argument("alvo", help="arquivo alvo a analisar")
    ap.add_argument("--mrg3ynauhl4c6qu1go4jqo",
                    help="JSON gerado por mrg3ynauhl4c6qu1go4jqo/uqr3e1yy66r39mr5tt2a0e.py no IDA")
    ap.add_argument("-o", "--saida", default="clone-out",
                    help="diretorio de saida (padrao: clone-out)")
    args = ap.parse_args(argv)
    saida = executar(args.alvo, args.ida_export, args.saida)
    print("9pd1ao2s9soicz7ndhxu9e concluido: %s" % saida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
