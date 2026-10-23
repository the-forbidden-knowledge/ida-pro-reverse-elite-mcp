#!/usr/bin/env python3
"""Recria devices (major/minor) que o alvo abre.

A partir de linhas `ls -l` (ex.: `crw-rw-rw- 1 root root 1, 3 /dev/null`),
extrai tipo/major/minor e gera o plano de `mknod` — sem precisar de root
para planejar.
"""

import argparse
import json
import re
import sys

RE_DEV = re.compile(
    r"^(?P<tipo>[cb])[rwxsStT-]{9}\s+\d+\s+\S+\s+\S+\s+"
    r"(?P<major>\d+),\s*(?P<minor>\d+)\s+(?P<path>\S+)"
)
RE_MODE = re.compile(r"^([cb])([rwxsStT-]{9})")


def parse_ls_device(linha):
    """Parse de uma linha `ls -l` de device. Retorna None se não for device."""
    m = RE_DEV.match(linha.strip())
    if not m:
        return None
    d = m.groupdict()
    return {
        "path": d["path"],
        "tipo": "char" if d["tipo"] == "c" else "block",
        "major": int(d["major"]),
        "minor": int(d["minor"]),
    }


def mknod_plan(devices):
    """Gera comandos `mknod` (placeholders relativos à jail)."""
    cmds = []
    for dev in devices:
        nome = dev["path"].lstrip("/")
        letra = "c" if dev["tipo"] == "char" else "b"
        cmds.append("mknod %s %s %d %d" % (nome, letra, dev["major"], dev["minor"]))
    return cmds


def devices_from_deps(deps):
    """Filtra caminhos /dev/* da lista de dependências do oráculo."""
    return [d["caminho"] for d in deps
            if d.get("tipo") == "dispositivo" and d.get("caminho")]


def main(argv=None):
    ap = argparse.ArgumentParser(description="Plano de mknod para devices")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--ls", help="arquivo com saída de `ls -l /dev`")
    g.add_argument("--deps", help="JSON de dependências (lab 71)")
    ap.add_argument("-o", "--saida", help="grava JSON neste arquivo")
    args = ap.parse_args(argv)
    if args.ls:
        with open(args.ls, encoding="utf-8") as f:
            devices = [d for d in (parse_ls_device(l) for l in f) if d]
    else:
        with open(args.deps, encoding="utf-8") as f:
            deps = json.load(f)
        if isinstance(deps, dict):
            deps = deps.get("dependencias", [])
        devices = [{"path": p, "tipo": "char", "major": None, "minor": None}
                   for p in devices_from_deps(deps)]
    resultado = {"devices": devices, "mknod": mknod_plan(
        [d for d in devices if d["major"] is not None])}
    texto = json.dumps(resultado, indent=2, ensure_ascii=False)
    if args.saida:
        with open(args.saida, "w", encoding="utf-8") as f:
            f.write(texto)
    else:
        print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
