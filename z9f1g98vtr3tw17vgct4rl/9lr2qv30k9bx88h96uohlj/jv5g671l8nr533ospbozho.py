#!/usr/bin/env python3
"""Pipeline multi-formato: PE + ELF + Mach-O + DEX num fluxo único de clonagem.

Detecta o formato de cada alvo pelo magic e despacha para o parser do
lab correspondente (labs 53–56, carregados por caminho). PE é detectado
(MZ + assinatura PE) mas não parseado aqui — detecção apenas.
"""

import argparse
import importlib.util
import json
import os
import struct
import sys

LABS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ELF_MAGIC = b"\x7fELF"
FAT_MAGIC = b"\xca\xfe\xba\xbe"
DEX_MAGIC = b"dex\n"
MZ_MAGIC = b"MZ"


def _load(modulo: str, pasta: str, arquivo: str):
    caminho = os.path.join(LABS, pasta, arquivo)
    spec = importlib.util.spec_from_file_location(modulo, caminho)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def detect_format(data: bytes) -> str:
    """Identifica o formato pelo magic. PE = detecção apenas."""
    if len(data) < 4:
        return "desconhecido"
    if data[:4] == ELF_MAGIC:
        return "elf64"
    if data[:4] == FAT_MAGIC:
        return "macho-fat"
    if data[:4] == DEX_MAGIC:
        return "dex"
    if data[:2] == MZ_MAGIC and len(data) >= 64:
        (e_lfanew,) = struct.unpack_from("<I", data, 0x3C)
        if 0 < e_lfanew < len(data) - 4 and data[e_lfanew:e_lfanew + 4] == b"PE\x00\x00":
            return "pe"
    return "desconhecido"


def analyze(caminho: str) -> dict:
    """Analisa um alvo com o parser do formato detectado."""
    with open(caminho, "rb") as f:
        data = f.read()
    formato = detect_format(data)
    resultado = {"arquivo": os.path.basename(caminho), "formato": formato}
    try:
        if formato == "elf64":
            mod = _load("dgwlbz9flx1esgdgsrzd7b", "e1nf6idkidpszk6j8ged6a", "dgwlbz9flx1esgdgsrzd7b.py")
            resultado["resumo"] = mod.summarize(mod.parse_elf(data))
        elif formato == "macho-fat":
            mod = _load("ak6f2jsqerwx4g7hodx44g", "wx9s0rp1raviau549xf7d3", "ak6f2jsqerwx4g7hodx44g.py")
            parsed = mod.parse_fat(data)
            resultado["resumo"] = {
                "arquiteturas": [a["cputype_nome"] for a in parsed["arquiteturas"]]}
        elif formato == "dex":
            mod = _load("kn3sau0500meaywgcjemld", "lsjpj02vdypbvpzen5d9go", "kn3sau0500meaywgcjemld.py")
            parsed = mod.parse_dex_header(data)
            resultado["resumo"] = {
                "string_ids": parsed["string_ids"]["quantidade"],
                "checksum_ok": parsed["checksum_ok"]}
        elif formato == "pe":
            resultado["resumo"] = {"nota": "detecção apenas; parse PE em lab dedicado"}
        else:
            resultado["erro"] = "formato não suportado"
    except Exception as exc:  # noqa: BLE001 — falha isolada por alvo
        resultado["erro"] = str(exc)
    return resultado


def run_pipeline(caminhos: list) -> dict:
    """Roda o pipeline sobre vários alvos e totaliza por formato."""
    alvos = [analyze(c) for c in caminhos]
    totais = {}
    for a in alvos:
        totais[a["formato"]] = totais.get(a["formato"], 0) + 1
    return {
        "alvos": alvos,
        "totais": totais,
        "analisados": sum(1 for a in alvos if "erro" not in a),
        "falhas": sum(1 for a in alvos if "erro" in a),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Pipeline multi-formato de clonagem.")
    ap.add_argument("alvos", nargs="+", help="arquivos-alvo")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    relatorio = run_pipeline(args.alvos)
    if args.json:
        print(json.dumps(relatorio, indent=2, ensure_ascii=False))
    else:
        for a in relatorio["alvos"]:
            status = a.get("erro", "ok")
            print("%-20s %-10s %s" % (a["arquivo"], a["formato"], status))
        print("totais: %s" % relatorio["totais"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
