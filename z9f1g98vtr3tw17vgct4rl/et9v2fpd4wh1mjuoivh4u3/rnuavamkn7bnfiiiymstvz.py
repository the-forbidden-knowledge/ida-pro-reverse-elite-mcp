#!/usr/bin/env python3
"""Detecção de frameworks híbridos em apps.

Identifica PhoneGap/Cordova (assets/www/cordova.js) e Xamarin
(assemblies/*.dll, NOTICE) na lista de arquivos do pacote — base do
dispatcher multi-framework do motor.
"""

import argparse
import json
import sys


def detectar(arquivos):
    """arquivos: lista de caminhos do pacote -> framework + evidências."""
    evidencias = []
    frameworks = []
    if "assets/www/cordova.js" in arquivos:
        frameworks.append("phonegap")
        evidencias.append("assets/www/cordova.js")
    dlls = sorted(
        a for a in arquivos if a.startswith("assemblies/") and a.endswith(".dll")
    )
    if dlls or "NOTICE" in arquivos:
        frameworks.append("xamarin")
        evidencias.extend(dlls if dlls else ["NOTICE"])
    return {
        "framework": "+".join(frameworks) if frameworks else "nativo",
        "evidencias": evidencias,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Detecta frameworks híbridos")
    args = ap.parse_args(argv)
    _ = args
    demo = [
        "assets/www/cordova.js",
        "assets/www/index.html",
        "AndroidManifest.xml",
    ]
    json.dump(detectar(demo), sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
