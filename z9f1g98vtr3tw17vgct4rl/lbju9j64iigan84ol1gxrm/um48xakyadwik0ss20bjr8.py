#!/usr/bin/env python3
"""Geração de scripts Frida para instrumentação dinâmica.

A partir de alvos (classe, método, tipos), gera o script com
`Java.use` + `implementation` que intercepta a chamada e repassa
ao original — base da extração de segredos em runtime.
"""

import argparse
import json
import sys


def gerar_script(alvos):
    """alvos: [(classe, metodo, [tipos])] -> código JS do Frida."""
    linhas = ["Java.perform(function() {"]
    for classe, metodo, tipos in alvos:
        overload = ""
        if tipos:
            overload = ".overload(" + ", ".join('"%s"' % t for t in tipos) + ")"
        linhas.append('  var K = Java.use("%s");' % classe)
        linhas.append('  K["%s"]%s.implementation = function() {' % (metodo, overload))
        linhas.append('    console.log("[*] %s.%s chamado");' % (classe, metodo))
        linhas.append(
            '    return this["%s"]%s.apply(this, arguments);' % (metodo, overload)
        )
        linhas.append("  };")
    linhas.append("});")
    return "\n".join(linhas)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Gera script Frida de hooks")
    args = ap.parse_args(argv)
    _ = args
    demo = [
        ("com.exemplo.Login", "autenticar", ["java.lang.String", "java.lang.String"]),
        ("com.exemplo.Cripto", "decifrar", []),
    ]
    print(gerar_script(demo))
    return 0


if __name__ == "__main__":
    sys.exit(main())
