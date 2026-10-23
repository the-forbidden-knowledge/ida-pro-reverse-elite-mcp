#!/usr/bin/env python3
"""Loop de profiling comportamental: AVC -> allow -> macros.

Lê denials AVC, gera regras allow cruas e as clusteriza em macros de alto
nível (o mesmo shape do pipeline de clonagem: observar -> especificar ->
iterar até cobertura total).
"""

import argparse
import json
import re
import sys

RE_AVC = re.compile(
    r"avc:\s+denied\s+\{\s*(?P<perms>[\w\s]+?)\s*\}\s+for\s+.*?comm=\"(?P<comm>[^\"]+)\""
    r".*?scontext=(?P<sctx>\S+)\s+tcontext=(?P<tctx>\S+)\s+tclass=(?P<tclass>\w+)",
    re.IGNORECASE,
)


def _tipo(ctx):
    partes = ctx.split(":")
    return partes[2] if len(partes) >= 3 else ctx


def parse_avc(linha):
    """Parse de uma linha AVC. Retorna None se não for denial."""
    m = RE_AVC.search(linha)
    if not m:
        return None
    d = m.groupdict()
    return {"comm": d["comm"], "perms": sorted(d["perms"].split()),
            "src": _tipo(d["sctx"]), "tgt": _tipo(d["tctx"]),
            "tclass": d["tclass"]}


def to_allow(avc):
    """Regra allow crua a partir do denial."""
    return "allow %s %s:%s { %s };" % (
        avc["src"], avc["tgt"], avc["tclass"], " ".join(avc["perms"]))


# tclass + padrão do alvo -> macro de alto nível
MACROS = [
    (lambda a: a["tclass"] == "file" and a["tgt"].endswith("_log_t"),
     "logging_log_file"),
    (lambda a: a["tclass"] == "file" and "etc_t" in a["tgt"],
     "read_files_pattern"),
    (lambda a: a["tclass"] in ("tcp_socket", "udp_socket") and
     "name_bind" in a["perms"], "corenet_tcp_bind_all_ports"),
    (lambda a: a["tclass"] == "capability", "capability_macro"),
    (lambda a: a["tclass"] == "file" and a["tgt"].endswith("_var_lib_t"),
     "var_lib_pattern"),
]


def clusterizar(avcs):
    """Agrupa denials em clusters -> macro sugerida (sem regras cruas soltas)."""
    clusters = {}
    for avc in avcs:
        macro = "regra_crua"
        for cond, nome in MACROS:
            if cond(avc):
                macro = nome
                break
        chave = (macro, avc["src"], avc["tclass"])
        clusters.setdefault(chave, {"macro": macro, "src": avc["src"],
                                    "tclass": avc["tclass"],
                                    "alvos": set(), "perms": set()})
        clusters[chave]["alvos"].add(avc["tgt"])
        clusters[chave]["perms"].update(avc["perms"])
    saida = []
    for (macro, src, tclass), c in sorted(clusters.items()):
        saida.append({"macro": macro, "src": src, "tclass": tclass,
                      "alvos": sorted(c["alvos"]), "perms": sorted(c["perms"])})
    return saida


def profile_binary(texto_log):
    """Pipeline: parse AVCs -> allows cruas -> clusters em macros."""
    avcs = [a for a in (parse_avc(l) for l in texto_log.splitlines()) if a]
    return {
        "denials": len(avcs),
        "allows_cruas": [to_allow(a) for a in avcs],
        "clusters": clusterizar(avcs),
        "cobertura_total": len(avcs) > 0,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="AVC -> allow -> macros")
    ap.add_argument("log", help="arquivo com denials AVC")
    ap.add_argument("-o", "--saida", help="grava JSON neste arquivo")
    args = ap.parse_args(argv)
    with open(args.log, encoding="utf-8", errors="replace") as f:
        resultado = profile_binary(f.read())
    texto = json.dumps(resultado, indent=2, ensure_ascii=False)
    if args.saida:
        with open(args.saida, "w", encoding="utf-8") as f:
            f.write(texto)
    else:
        print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
