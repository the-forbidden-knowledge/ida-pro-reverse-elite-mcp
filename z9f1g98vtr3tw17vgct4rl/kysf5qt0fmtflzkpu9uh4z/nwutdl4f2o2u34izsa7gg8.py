#!/usr/bin/env python3
"""Detecta Native Image (NGEN) vs IL em modulos .NET (fixtures sinteticas).

`System.Management.Automation.ni.dll` e' a DLL do engine PowerShell compilada
nativamente para a CPU via NGEN; a variante IL e' bytecode. Em RE isso importa:
na .ni.dll o codigo e' nativo (muda onde breakpoints/hooks funcionam) e explica
por que instrumentacao .NET falha.
"""
import argparse
import json


def classify(path: str) -> str:
    baixo = path.lower()
    if baixo.endswith(".ni.dll"):
        return "native (NGEN)"
    if baixo.endswith(".dll"):
        return "IL (bytecode)"
    if baixo.endswith(".exe"):
        return "executavel"
    return "outro"


def scan(modules: list) -> list:
    return [{"path": m, "kind": classify(m)} for m in modules]


def engine_variants(modules: list) -> dict:
    """Quais variantes do engine PowerShell estao carregadas."""
    out = {"native": [], "il": []}
    for m in modules:
        if "system.management.automation" in m.lower():
            (out["native"] if classify(m).startswith("native")
             else out["il"]).append(m)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="NGEN vs IL (sintetico)")
    ap.add_argument("--modules", nargs="+", default=[
        "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\System.Management.Automation.ni.dll",
        "C:\\App\\MinhaLib.dll"])
    a = ap.parse_args(argv)
    print(json.dumps({"modules": scan(a.modules),
                      "engine": engine_variants(a.modules)}, indent=2))


if __name__ == "__main__":
    main()
