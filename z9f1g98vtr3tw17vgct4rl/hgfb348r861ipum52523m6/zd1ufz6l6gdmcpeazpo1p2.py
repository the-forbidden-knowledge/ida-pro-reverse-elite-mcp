#!/usr/bin/env python3
"""Caça a vazamentos de Log.x() pós-ofuscação.

Encontra chamadas `Log.d/e/i/w/v()` em smali cujos argumentos são
const-strings — elas frequentemente vazam os nomes originais que o
ofuscador tentou esconder.
"""

import argparse
import json
import re
import sys

_CONST = re.compile(r'\s*const-string\s+(v\d+),\s*"((?:[^"\\]|\\.)*)"')
_INVOKE = re.compile(
    r"\s*invoke-static\s*\{([^}]*)\},\s*Landroid/util/Log;->([deivw])\("
)


def vazar_linhas(linhas):
    """Retorna [{linha, nivel, tag, msg}] para cada chamada de Log."""
    consts = {}
    vaz = []
    for i, ln in enumerate(linhas, 1):
        m = _CONST.match(ln)
        if m:
            consts[m.group(1)] = m.group(2)
            continue
        m = _INVOKE.match(ln)
        if m:
            regs = [r.strip() for r in m.group(1).split(",") if r.strip()]
            tag = consts.get(regs[0], "?") if regs else "?"
            msg = consts.get(regs[1], "?") if len(regs) > 1 else "?"
            vaz.append(
                {"linha": i, "nivel": m.group(2), "tag": tag, "msg": msg}
            )
    return vaz


def main(argv=None):
    ap = argparse.ArgumentParser(description="Encontra vazamentos de Log.x()")
    args = ap.parse_args(argv)
    _ = args
    demo = [
        '    const-string v0, "Rede"',
        '    const-string v1, "senha=segredo123"',
        "    invoke-static {v0, v1}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I",
        "    invoke-static {v0}, Ljava/lang/Math;->abs(I)I",
    ]
    json.dump(vazar_linhas(demo), sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
