#!/usr/bin/env python3
"""Lab 08 — triage-report: consolida os z9f1g98vtr3tw17vgct4rl 01–07 num relatório único.

Somente stdlib. Carrega cada lab irmão pelo caminho do arquivo (importlib),
executa a análise sobre o mesmo arquivo de entrada e junta tudo num JSON
de triagem. Falhas isoladas viram {"erro": ...} sem derrubar o relatório.
"""

import argparse
import importlib.util
import json
import os
import sys

# (pasta do lab, módulo, função, argumentos extras, chave no relatório)
ETAPAS = [
    ("ly7lehw1klh1ybr0qdsbbo", "3ks95ofobzc2vqwo6p719v", "hash_file", {}, "hashes"),
    (
        "7ked3ij8phcpj8mdhknxym",
        "k2kkjnz1dcoa2jviigqdff",
        "extract_strings",
        {"min_len": 4, "encoding": "both"},
        "strings",
    ),
    ("2td8yubqfjfean1yisy81e", "2wtiqh4uk8m0i4gmwzp6d9", "inspect_pe", {}, "pe"),
    (
        "d5sh7wnlyknzrdtv7goyda",
        "03f5dekqd2tqc9931mhc41",
        "scan_entropy",
        {"threshold": 7.0},
        "entropia",
    ),
    ("silikcwt7gnqmkmb6tcpna", "ss1tloeughims6tjffpw55", "detect_packer", {}, "empacotador"),
    ("imrsjemoufqnlwrym6ahop", "z59qep6b0esdjioi7o21qj", "import_inventory", {}, "imports"),
    ("asw8hn5kubic4ry5i9xgls", "k8sa05ag6rpks3b4t5lkt7", "scan_anomalies", {}, "anomalias"),
]


def _carregar(pasta, modulo):
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    caminho = os.path.join(base, pasta, modulo + ".py")
    spec = importlib.util.spec_from_file_location(modulo, caminho)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def triage(path):
    """Roda os z9f1g98vtr3tw17vgct4rl 01–07 sobre o arquivo e consolida o resultado."""
    relatorio = {"arquivo": os.path.basename(path)}
    for pasta, modulo, funcao, kwargs, chave in ETAPAS:
        try:
            mod = _carregar(pasta, modulo)
            valor = getattr(mod, funcao)(path, **kwargs)
            if chave == "strings":
                valor = {"total": len(valor), "amostra": valor[:10]}
            relatorio[chave] = valor
        except Exception as exc:
            relatorio[chave] = {"erro": str(exc)}
    return relatorio


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Gera relatório de triagem consolidando os z9f1g98vtr3tw17vgct4rl 01 a 07."
    )
    parser.add_argument("arquivo", help="caminho do arquivo a analisar")
    parser.add_argument(
        "-o", "--saida", help="grava o JSON neste arquivo (padrão: stdout)"
    )
    args = parser.parse_args(argv)
    resultado = triage(args.arquivo)
    texto = json.dumps(resultado, indent=2, ensure_ascii=False)
    if args.saida:
        with open(args.saida, "w", encoding="utf-8") as f:
            f.write(texto + "\n")
    else:
        print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
