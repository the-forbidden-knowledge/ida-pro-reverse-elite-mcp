#!/usr/bin/env python3
"""jumptable-resolve: resolve uma jump table a partir de um hex dump.

Le os bytes brutos da tabela, interpreta cada entrada como um deslocamento
(RVA) e soma ao endereco base, produzindo o alvo de cada case do switch.

Uso: python3 et7kucclfz81q4w51d8rcs.py --base 0x401000 --count 4 --ptrsize 4 tabela.hex
Saida: JSON {"cases": [{"index", "target"}]} na stdout.
"""

import argparse
import json
import re
import struct
import sys


def parse_hex_dump(text):
    """Extrai bytes de um hex dump.

    Aceita: bytes separados por espaco, string hex continua, linhas estilo
    xxd (offset + bytes + coluna ASCII). A coluna ASCII apos '|' e ignorada.
    """
    data = bytearray()
    for raw in text.splitlines():
        line = raw.split("|", 1)[0].strip()
        if not line:
            continue
        toks = line.split()
        # descarta token de offset no inicio da linha (xxd)
        if (len(toks) > 1
                and re.fullmatch(r"(0x)?[0-9A-Fa-f]{3,}:?", toks[0])):
            toks = toks[1:]
        chunk = "".join(toks)
        chunk = chunk.replace("0x", "").replace("0X", "")
        chunk = re.sub(r"[^0-9A-Fa-f]", "", chunk)
        if not chunk:
            continue
        if len(chunk) % 2:
            raise ValueError(f"nibble solitario na linha: {raw.strip()!r}")
        data += bytes.fromhex(chunk)
    return bytes(data)


def resolve(data, base, count, ptrsize):
    fmt = "<I" if ptrsize == 4 else "<Q"
    need = count * ptrsize
    if len(data) < need:
        raise ValueError(
            f"bytes insuficientes: precisa de {need}, tem {len(data)}")
    cases = []
    for i in range(count):
        (rva,) = struct.unpack_from(fmt, data, i * ptrsize)
        cases.append({"index": i, "target": hex(base + rva)})
    return cases


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="arquivo com o hex dump da tabela")
    parser.add_argument("--base", required=True,
                        help="endereco base em hex (ex.: 0x401000)")
    parser.add_argument("--count", required=True, type=int,
                        help="numero de entradas da tabela")
    parser.add_argument("--ptrsize", type=int, choices=(4, 8), default=4,
                        help="tamanho do ponteiro: 4 ou 8 (padrao 4)")
    args = parser.parse_args(argv)

    base = int(args.base, 16)
    with open(args.input, "r", encoding="utf-8", errors="replace") as fh:
        data = parse_hex_dump(fh.read())
    try:
        cases = resolve(data, base, args.count, args.ptrsize)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps({"cases": cases}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
