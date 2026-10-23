#!/usr/bin/env python3
"""Lab 07 — anomaly-scan: procura constantes de cripto/compressão.

Somente stdlib. Varre os bytes do arquivo procurando assinaturas
conhecidas: S-boxes do AES, constantes do SHA-256, estado inicial do MD5,
constante delta do TEA e magic numbers de formatos (ZIP, RAR, 7z, gzip).
A presença dessas constantes indica rotinas de criptografia ou dados
comprimidos embutidos.
"""

import argparse
import json
import sys

ASSINATURAS = [
    (
        "AES S-box",
        "cripto",
        bytes.fromhex(
            "63 7c 77 7b f2 6b 6f c5 30 01 67 2b fe d7 ab 76"
        ),
    ),
    (
        "AES S-box inversa",
        "cripto",
        bytes.fromhex(
            "52 09 6a d5 30 36 a5 38 bf 40 a3 9e 81 f3 d7 fb"
        ),
    ),
    (
        "constantes SHA-256",
        "cripto",
        bytes.fromhex(
            "42 8a 2f 98 71 37 44 91 b5 c0 fb cf e9 b5 db a5"
        ),
    ),
    (
        "estado inicial MD5",
        "cripto",
        bytes.fromhex("01 23 45 67 89 ab cd ef fe dc ba 98 76 54 32 10"),
    ),
    ("constante delta TEA", "cripto", bytes.fromhex("9e 37 79 b9")),
    ("magic ZIP", "formato", b"PK\x03\x04"),
    ("magic RAR", "formato", b"Rar!\x1a\x07\x00"),
    ("magic 7z", "formato", b"7z\xbc\xaf\x27\x1c"),
    ("magic gzip", "formato", b"\x1f\x8b"),
    ("magic MZ", "formato", b"MZ"),
]


def scan_anomalies(path):
    """Procura as assinaturas no arquivo.

    Retorna lista de {offset, nome, tipo} ordenada por offset.
    """
    with open(path, "rb") as f:
        data = f.read()
    achados = []
    for nome, tipo, assinatura in ASSINATURAS:
        inicio = 0
        while True:
            pos = data.find(assinatura, inicio)
            if pos < 0:
                break
            achados.append(
                {"offset": pos, "nome": nome, "tipo": tipo}
            )
            inicio = pos + 1
    achados.sort(key=lambda a: a["offset"])
    return achados


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Procura constantes de cripto/compressão num arquivo."
    )
    parser.add_argument("arquivo", help="caminho do arquivo a analisar")
    parser.add_argument(
        "-o", "--saida", help="grava o JSON neste arquivo (padrão: stdout)"
    )
    args = parser.parse_args(argv)
    resultado = scan_anomalies(args.arquivo)
    texto = json.dumps(resultado, indent=2, ensure_ascii=False)
    if args.saida:
        with open(args.saida, "w", encoding="utf-8") as f:
            f.write(texto + "\n")
    else:
        print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
