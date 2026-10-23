#!/usr/bin/env python3
"""Lab 05 — packer-detect: heurísticas para detectar executável empacotado.

Somente stdlib. Combina três sinais:
  1. entropia alta (>= 7.2) em alguma seção — código comprimido/criptografado;
  2. poucos descritores de importação (< 2) — o loader real está escondido;
  3. nomes de seção típicos de empacotadores (UPX, ASPack, Themida...).

Veredito: packed=true se houver 2 ou mais motivos.
"""

import argparse
import json
import math
import struct
import sys

ENTROPY_THRESHOLD = 7.2
NOMES_SUSPEITOS = (
    "upx",
    "aspack",
    "themida",
    "vmp",
    "enigma",
    "petite",
    "mpress",
    "winlice",
    "ccg",
    "sforce",
    "svkp",
    "pecompact",
    "pec2",
    "neolite",
    "yoda",
    "rlpack",
    "kkrunchy",
)


def _shannon(data):
    if not data:
        return 0.0
    freq = [0] * 256
    for b in data:
        freq[b] += 1
    n = len(data)
    ent = 0.0
    for c in freq:
        if c:
            p = c / n
            ent -= p * math.log2(p)
    return ent


def _rva_para_offset(secoes, rva):
    for s in secoes:
        if s["vaddr"] <= rva < s["vaddr"] + max(s["vsize"], s["rawsize"], 1):
            return rva - s["vaddr"] + s["rawptr"]
    raise ValueError("RVA fora das seções: 0x%X" % rva)


def _parse(data):
    if len(data) < 64 or data[0:2] != b"MZ":
        raise ValueError("assinatura MZ não encontrada")
    (e_lfanew,) = struct.unpack_from("<I", data, 0x3C)
    if data[e_lfanew : e_lfanew + 4] != b"PE\0\0":
        raise ValueError("assinatura PE não encontrada")
    coff = e_lfanew + 4
    (_m, num, _t, _p, _n, opt_size, _c) = struct.unpack_from(
        "<HHIIIHH", data, coff
    )
    opt = coff + 20
    (magic,) = struct.unpack_from("<H", data, opt)
    if magic == 0x10B:  # PE32
        dd_off, nrva_off = opt + 96, opt + 92
    elif magic == 0x20B:  # PE32+
        dd_off, nrva_off = opt + 112, opt + 108
    else:
        raise ValueError("optional header desconhecido")
    (num_rva,) = struct.unpack_from("<I", data, nrva_off)
    import_rva = 0
    if num_rva > 1:
        (import_rva, _sz) = struct.unpack_from("<II", data, dd_off + 8)
    secoes = []
    base = coff + 20 + opt_size
    for i in range(num):
        bruto = data[base + i * 40 : base + (i + 1) * 40]
        nome = bruto[0:8].split(b"\x00")[0].decode("ascii", "replace")
        vsize, vaddr, rawsize, rawptr = struct.unpack_from("<IIII", bruto, 8)
        secoes.append(
            {"name": nome, "vsize": vsize, "vaddr": vaddr,
             "rawsize": rawsize, "rawptr": rawptr}
        )
    ndesc = 0
    if import_rva:
        off = _rva_para_offset(secoes, import_rva)
        while True:
            desc = data[off : off + 20]
            if len(desc) < 20 or desc == b"\x00" * 20:
                break
            ndesc += 1
            off += 20
    return secoes, ndesc


def detect_packer(path, entropy_threshold=ENTROPY_THRESHOLD):
    """Aplica as heurísticas e retorna {packed, reasons, import_descriptors}."""
    with open(path, "rb") as f:
        data = f.read()
    secoes, ndesc = _parse(data)
    reasons = []
    for s in secoes:
        bloco = data[s["rawptr"] : s["rawptr"] + s["rawsize"]]
        ent = _shannon(bloco)
        if ent >= entropy_threshold:
            reasons.append(
                "entropia alta na seção %s (%.2f)" % (s["name"], ent)
            )
        nome_baixo = s["name"].lower()
        if any(x in nome_baixo for x in NOMES_SUSPEITOS):
            reasons.append("nome de seção suspeito: %s" % s["name"])
    if ndesc < 2:
        reasons.append("poucos descritores de importação (%d)" % ndesc)
    return {
        "packed": len(reasons) >= 2,
        "reasons": reasons,
        "import_descriptors": ndesc,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Detecta empacotamento em um executável PE."
    )
    parser.add_argument("arquivo", help="caminho do arquivo PE")
    parser.add_argument(
        "--threshold",
        type=float,
        default=ENTROPY_THRESHOLD,
        help="limite de entropia (padrão: 7.2)",
    )
    parser.add_argument(
        "-o", "--saida", help="grava o JSON neste arquivo (padrão: stdout)"
    )
    args = parser.parse_args(argv)
    resultado = detect_packer(args.arquivo, args.threshold)
    texto = json.dumps(resultado, indent=2, ensure_ascii=False)
    if args.saida:
        with open(args.saida, "w", encoding="utf-8") as f:
            f.write(texto + "\n")
    else:
        print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
