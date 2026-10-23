#!/usr/bin/env python3
"""Modelo de Type Enforcement do SELinux.

Parse de contextos `usuário:papel:tipo:nível`, matriz de regras allow e
transições de tipo — a camada MAC que `readelf`/`strace` sozinhos não dão.
"""

import argparse
import json
import re
import sys

RE_CTX = re.compile(
    r"^(?P<user>[^:]+):(?P<role>[^:]+):(?P<type>[^:]+):(?P<level>s\d+(-s\d+)?(:c\d+(\.c\d+)?)?)$"
)
RE_ALLOW = re.compile(
    r"allow\s+(?P<src>\w+)\s+(?P<tgt>[\w.]+)\s*:\s*(?P<class>\w+)\s+"
    r"\{\s*(?P<perms>[^}]+)\s*\}\s*;"
)
RE_TRANS = re.compile(
    r"type_transition\s+(?P<src>\w+)\s+(?P<tgt>[\w.]+)\s*:\s*"
    r"(?P<class>\w+)\s+(?P<novo>\w+)\s*;"
)


def parse_context(s):
    """Parse de `u:r:t:s0`. Retorna None se inválido."""
    m = RE_CTX.match(s.strip())
    if not m:
        return None
    d = m.groupdict()
    return {"user": d["user"], "role": d["role"], "type": d["type"],
            "level": d["level"] or "s0"}


def parse_allow(regra):
    """Parse de `allow src tgt:class { perms };`."""
    m = RE_ALLOW.match(regra.strip())
    if not m:
        return None
    d = m.groupdict()
    return {"src": d["src"], "tgt": d["tgt"], "class": d["class"],
            "perms": sorted(d["perms"].split())}


def parse_transition(regra):
    """Parse de `type_transition src tgt:class novo;`."""
    m = RE_TRANS.match(regra.strip())
    if not m:
        return None
    return m.groupdict()


def build_matrix(allows):
    """Matriz src -> tgt -> class -> set(perms)."""
    matriz = {}
    for a in allows:
        matriz.setdefault(a["src"], {}).setdefault(a["tgt"], {}) \
            .setdefault(a["class"], set()).update(a["perms"])
    return matriz


def check(matriz, src, tgt, cls, perm):
    """Tudo que não é explicitamente permitido é negado."""
    return perm in matriz.get(src, {}).get(tgt, {}).get(cls, set())


def aplicar_transicao(transicoes, src_type, tgt_exec_type, cls="process"):
    """Retorna o novo tipo após exec, ou o tipo atual se sem transição."""
    for t in transicoes:
        if (t["src"] == src_type and t["tgt"] == tgt_exec_type
                and t["class"] == cls):
            return t["novo"]
    return src_type  # herança: filho herda o contexto do pai


def relatorio(ctxs, allows, transicoes):
    matriz = build_matrix(allows)
    return {
        "contextos": [parse_context(c) for c in ctxs],
        "regras": len(allows),
        "transicoes": [parse_transition(t) for t in transicoes],
        "matriz": {s: {t: {c: sorted(p) for c, p in tc.items()}
                       for t, tc in tg.items()}
                   for s, tg in matriz.items()},
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Modelo TE do SELinux")
    ap.add_argument("--ctx", nargs="*", default=[],
                    help="contextos u:r:t:s0")
    ap.add_argument("--allow", nargs="*", default=[], help="regras allow")
    ap.add_argument("--trans", nargs="*", default=[],
                    help="regras type_transition")
    ap.add_argument("--check", nargs=4, metavar=("SRC", "TGT", "CLASS", "PERM"),
                    help="testa uma permissão")
    ap.add_argument("-o", "--saida", help="grava JSON neste arquivo")
    args = ap.parse_args(argv)
    allows = [a for a in (parse_allow(r) for r in args.allow) if a]
    trans = [t for t in (parse_transition(r) for r in args.trans) if t]
    matriz = build_matrix(allows)
    resultado = relatorio(args.ctx, allows, args.trans)
    if args.check:
        src, tgt, cls, perm = args.check
        resultado["check"] = {"permitido": check(matriz, src, tgt, cls, perm)}
    texto = json.dumps(resultado, indent=2, ensure_ascii=False)
    if args.saida:
        with open(args.saida, "w", encoding="utf-8") as f:
            f.write(texto)
    else:
        print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
