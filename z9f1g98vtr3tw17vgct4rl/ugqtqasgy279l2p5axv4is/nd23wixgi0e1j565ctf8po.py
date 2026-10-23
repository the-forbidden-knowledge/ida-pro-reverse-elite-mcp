#!/usr/bin/env python3
"""Parse do TLS Directory do PE: lista os callbacks registrados.

Entrada: caminho de um arquivo PE (32 ou 64 bits).
Saida: JSON {"tls_presente": bool, "callbacks": [{va, rva}], "total_callbacks": N}.
"""

import argparse
import json
import struct
import sys

TLS_DIR_INDEX = 9


def rva_para_offset(secoes, rva):
    """Converte RVA em offset de arquivo usando as secoes."""
    for nome, vaddr, vsize, rawsize, rawptr in secoes:
        fim = vaddr + max(vsize, rawsize)
        if vaddr <= rva < fim:
            return rva - vaddr + rawptr
    return None


def parse_tls(caminho):
    with open(caminho, "rb") as f:
        dados = f.read()

    if dados[0:2] != b"MZ":
        raise ValueError("nao e um executavel MZ")
    e_lfanew = struct.unpack_from("<I", dados, 0x3C)[0]
    if dados[e_lfanew:e_lfanew + 4] != b"PE\x00\x00":
        raise ValueError("assinatura PE invalida")

    coff = e_lfanew + 4
    machine, nsec, _, _, _, tam_opt, _ = struct.unpack_from("<HHIIIHH", dados, coff)
    opt = coff + 20
    magic = struct.unpack_from("<H", dados, opt)[0]
    is64 = magic == 0x20B
    if magic not in (0x10B, 0x20B):
        raise ValueError("optional header desconhecido: 0x%X" % magic)

    image_base = (struct.unpack_from("<Q", dados, opt + 24)[0] if is64
                  else struct.unpack_from("<I", dados, opt + 28)[0])
    off_dir = opt + (112 if is64 else 96)
    n_dirs = struct.unpack_from("<I", dados, off_dir - 4)[0]

    tls_rva, tls_size = 0, 0
    if n_dirs > TLS_DIR_INDEX:
        tls_rva, tls_size = struct.unpack_from("<II", dados, off_dir + 8 * TLS_DIR_INDEX)

    secoes = []
    base_sec = opt + tam_opt
    for i in range(nsec):
        s = base_sec + 40 * i
        nome, vsize, vaddr, rawsize, rawptr = struct.unpack_from("<8sIIII", dados, s)
        secoes.append((nome.rstrip(b"\x00"), vaddr, vsize, rawsize, rawptr))

    resultado = {
        "tls_presente": False,
        "bits": 64 if is64 else 32,
        "machine": "0x%04X" % machine,
        "image_base": "0x%X" % image_base,
        "callbacks": [],
        "total_callbacks": 0,
    }
    if not tls_rva or not tls_size:
        return resultado

    off = rva_para_offset(secoes, tls_rva)
    if off is None or off + (40 if is64 else 24) > len(dados):
        return resultado

    if is64:
        vals = struct.unpack_from("<QQQQII", dados, off)
    else:
        vals = struct.unpack_from("<IIIIII", dados, off)
    (raw_start, raw_end, addr_index, addr_callbacks, zero_fill, chars) = vals
    resultado["diretorio"] = {
        "rva": "0x%X" % tls_rva,
        "tamanho": tls_size,
        "start_of_raw": "0x%X" % raw_start,
        "end_of_raw": "0x%X" % raw_end,
        "address_of_callbacks": "0x%X" % addr_callbacks,
        "characteristics": "0x%X" % chars,
    }

    # array de callbacks: ponteiros terminados em NULL
    cb_rva = addr_callbacks - image_base
    cb_off = rva_para_offset(secoes, cb_rva)
    if cb_off is not None:
        passo = 8 if is64 else 4
        fmt = "<Q" if is64 else "<I"
        cbs = []
        pos = cb_off
        while pos + passo <= len(dados):
            (ptr,) = struct.unpack_from(fmt, dados, pos)
            if ptr == 0:
                break
            cbs.append({"va": "0x%X" % ptr, "rva": "0x%X" % (ptr - image_base)})
            pos += passo
            if len(cbs) > 1024:  # trava de seguranca
                break
        resultado["callbacks"] = cbs
        resultado["total_callbacks"] = len(cbs)
        resultado["tls_presente"] = True

    return resultado


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Lista callbacks do TLS Directory de um PE.")
    ap.add_argument("--input", required=True, help="arquivo PE")
    ap.add_argument("--output", default=None, help="arquivo de saida (padrao: stdout)")
    args = ap.parse_args(argv)

    try:
        rel = parse_tls(args.input)
    except (ValueError, struct.error) as e:
        raise SystemExit("erro: %s" % e)

    texto = json.dumps(rel, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(texto + "\n")
    else:
        sys.stdout.write(texto + "\n")


if __name__ == "__main__":
    main()
