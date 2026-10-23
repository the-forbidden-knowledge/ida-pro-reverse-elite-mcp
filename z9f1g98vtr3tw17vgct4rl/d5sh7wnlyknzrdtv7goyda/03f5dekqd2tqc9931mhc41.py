#!/usr/bin/env python3
"""Lab 04 — entropy-scan: entropia de Shannon por seção + histograma.

Somente stdlib. Entropia alta (~7-8 bits/byte) numa seção executável é um
forte indício de código empacotado ou criptografado.
"""

import argparse
import json
import math
import struct
import sys


def _parse_secoes(data):
    if len(data) < 64 or data[0:2] != b"MZ":
        raise ValueError("assinatura MZ não encontrada")
    (e_lfanew,) = struct.unpack_from("<I", data, 0x3C)
    if data[e_lfanew : e_lfanew + 4] != b"PE\0\0":
        raise ValueError("assinatura PE não encontrada")
    coff = e_lfanew + 4
    (_m, num, _t, _p, _n, opt_size, _c) = struct.unpack_from(
        "<HHIIIHH", data, coff
    )
    secoes = []
    base = coff + 20 + opt_size
    for i in range(num):
        bruto = data[base + i * 40 : base + (i + 1) * 40]
        nome = bruto[0:8].split(b"\x00")[0].decode("ascii", "replace")
        vsize, vaddr, rawsize, rawptr = struct.unpack_from("<IIII", bruto, 8)
        secoes.append(
            {"name": nome, "rawsize": rawsize, "rawptr": rawptr}
        )
    return secoes


def shannon(data):
    """Entropia de Shannon em bits por byte (0 a 8)."""
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


def histograma(data):
    """Contagem de ocorrências de cada valor de byte (256 posições)."""
    freq = [0] * 256
    for b in data:
        freq[b] += 1
    return freq


def scan_entropy(path, threshold=7.0):
    """Calcula a entropia de cada seção do PE.

    Retorna {sections: [{name, size, entropy, alerta}], histogram: [...]}.
    """
    with open(path, "rb") as f:
        data = f.read()
    secoes = _parse_secoes(data)
    resultado = []
    for s in secoes:
        bloco = data[s["rawptr"] : s["rawptr"] + s["rawsize"]]
        ent = shannon(bloco)
        resultado.append(
            {
                "name": s["name"],
                "size": len(bloco),
                "entropy": round(ent, 4),
                "alerta": ent >= threshold,
            }
        )
    return {"sections": resultado, "histogram": histograma(data)}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Entropia de Shannon por seção de um PE."
    )
    parser.add_argument("arquivo", help="caminho do arquivo PE")
    parser.add_argument(
        "--threshold",
        type=float,
        default=7.0,
        help="limite de alerta de entropia (padrão: 7.0)",
    )
    parser.add_argument(
        "-o", "--saida", help="grava o JSON neste arquivo (padrão: stdout)"
    )
    args = parser.parse_args(argv)
    resultado = scan_entropy(args.arquivo, args.threshold)
    texto = json.dumps(resultado, indent=2)
    if args.saida:
        with open(args.saida, "w", encoding="utf-8") as f:
            f.write(texto + "\n")
    else:
        print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
