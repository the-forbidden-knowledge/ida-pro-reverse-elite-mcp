#!/usr/bin/env python3
"""Lab 01 — hash-identify: calcula MD5, SHA-1 e SHA-256 de um arquivo.

Somente stdlib. A leitura é feita em blocos para não carregar o arquivo
inteiro na memória.
"""

import argparse
import hashlib
import json
import sys


def hash_file(path, chunk_size=65536):
    """Calcula MD5, SHA-1 e SHA-256 de um arquivo.

    Retorna dict {md5, sha1, sha256, size}.
    """
    digests = {nome: hashlib.new(nome) for nome in ("md5", "sha1", "sha256")}
    size = 0
    with open(path, "rb") as f:
        while True:
            bloco = f.read(chunk_size)
            if not bloco:
                break
            size += len(bloco)
            for d in digests.values():
                d.update(bloco)
    return {
        "md5": digests["md5"].hexdigest(),
        "sha1": digests["sha1"].hexdigest(),
        "sha256": digests["sha256"].hexdigest(),
        "size": size,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Calcula MD5, SHA-1 e SHA-256 de um arquivo."
    )
    parser.add_argument("arquivo", help="caminho do arquivo a analisar")
    parser.add_argument(
        "-o", "--saida", help="grava o JSON neste arquivo (padrão: stdout)"
    )
    args = parser.parse_args(argv)
    resultado = hash_file(args.arquivo)
    texto = json.dumps(resultado, indent=2)
    if args.saida:
        with open(args.saida, "w", encoding="utf-8") as f:
            f.write(texto + "\n")
    else:
        print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
