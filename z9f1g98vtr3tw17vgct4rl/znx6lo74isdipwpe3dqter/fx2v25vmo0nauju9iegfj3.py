#!/usr/bin/env python3
"""Mapeia conjunto de APIs para classificacao da tecnica.

Somente stdlib. Entrada: JSON {"apis": [...]}. Tabela embutida associa
grupos de APIs a tecnicas (injecao, hooking, hollowing, keylogging,
persistencia); a pontuacao e a fracao de APIs do grupo encontradas.
"""
import argparse
import json
import sys

TABLE = {
    "injecao": ["openprocess", "virtualalloc", "writeprocessmemory",
                "createremotethread", "rtlcreateuserthread",
                "ntmapviewofsection"],
    "hooking": ["virtualprotect", "writeprocessmemory", "readprocessmemory",
                "setwindowshookex", "flushinstructioncache"],
    "hollowing": ["createprocess", "writeprocessmemory", "setthreadcontext",
                  "resumethread", "ntunmapviewofsection"],
    "keylogging": ["getasynckeystate", "getkeystate", "setwindowshookex",
                   "getforegroundwindow", "getkeyboardstate"],
    "persistencia": ["regopenkey", "regsetvalue", "regcreatekey",
                     "createservice", "schtasks", "copyfile"],
}


def clean(name):
    n = name.lower()
    if n.endswith("ex"):
        n = n[:-2]
    if n[-1:] in ("a", "w") and len(n) > 4:
        n = n[:-1]
    return n


def classify(apis):
    have = set()
    for a in apis:
        c = clean(a)
        have.add(c)
        # permite prefixo: "createprocessinternalw" casa "createprocess"
        for tech, group in TABLE.items():
            for g in group:
                if c.startswith(g) and c != g:
                    have.add(g)
    techniques = []
    for tech, group in TABLE.items():
        matched = sorted({g for g in group if g in have})
        score = len(matched) / len(group)
        if matched:
            techniques.append({
                "name": tech,
                "matched": matched,
                "score": round(score, 3),
            })
    techniques.sort(key=lambda t: t["score"], reverse=True)
    return {
        "techniques": techniques,
        "top": techniques[0]["name"] if techniques else None,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Classifica a tecnica a partir das APIs."
    )
    ap.add_argument("input", help='JSON com {"apis": [...]}')
    ap.add_argument("--output", "-o", help="arquivo de saida JSON")
    args = ap.parse_args(argv)

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)
    result = classify(data.get("apis", []))
    out = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
