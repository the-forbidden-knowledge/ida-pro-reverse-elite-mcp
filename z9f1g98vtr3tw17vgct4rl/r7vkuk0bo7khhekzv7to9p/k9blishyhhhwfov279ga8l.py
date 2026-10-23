#!/usr/bin/env python3
"""Gera plano de patch para neutralizar defesas anti-analise.

Entrada: JSON do inventario (lab 39) ou lista simples de nomes de API.
Saida: JSON {"patches": [{alvo, categoria, tipo, descricao, bytes}]}.
Tipos de patch: forcar-retorno | nop | inverter-salto | zerar-flag | manual.
"""

import argparse
import json
import sys

# api (minuscula) -> plano de patch
PATCHES = {
    "isdebuggerpresent": {
        "tipo": "forcar-retorno",
        "descricao": "Fazer a funcao sempre retornar 0 (nao ha debugger)",
        "bytes": "B8 00 00 00 00 C3",
        "detalhe": "patch no prologo: mov eax,0; ret",
    },
    "checkremotedebuggerpresent": {
        "tipo": "zerar-flag",
        "descricao": "Zerar *pbDebuggerPresent na saida da chamada",
        "bytes": "C7 01 00 00 00 00",
        "detalhe": "apos a chamada: mov dword ptr [rcx],0",
    },
    "ntqueryinformationprocess": {
        "tipo": "forcar-retorno",
        "descricao": "Retornar STATUS_SUCCESS com DebugPort = 0",
        "bytes": "33 C0 C3",
        "detalhe": "xor eax,eax; ret (cuidado com a convencao de chamada)",
    },
    "outputdebugstringa": {
        "tipo": "nop",
        "descricao": "Neutralizar chamada (sem efeito colateral)",
        "bytes": "90 90 90 90 90",
        "detalhe": "NOPs sobre a chamada",
    },
    "outputdebugstringw": {
        "tipo": "nop",
        "descricao": "Neutralizar chamada (sem efeito colateral)",
        "bytes": "90 90 90 90 90",
        "detalhe": "NOPs sobre a chamada",
    },
    "gettickcount": {
        "tipo": "forcar-retorno",
        "descricao": "Retornar contador fixo (acelera checagens de sleep)",
        "bytes": "B8 00 10 00 00 C3",
        "detalhe": "mov eax,0x1000; ret",
    },
    "gettickcount64": {
        "tipo": "forcar-retorno",
        "descricao": "Retornar contador fixo de 64 bits",
        "bytes": "48 C7 C0 00 10 00 00 C3",
        "detalhe": "mov rax,0x1000; ret",
    },
    "queryperformancecounter": {
        "tipo": "forcar-retorno",
        "descricao": "Retornar valor fixo e TRUE",
        "bytes": "48 31 C0 48 FF C0 C3",
        "detalhe": "xor rax,rax; inc rax; ret",
    },
    "rdtsc": {
        "tipo": "nop",
        "descricao": "Substituir RDTSC por instrucoes neutras",
        "bytes": "90 90",
        "detalhe": "0F 31 (2 bytes) -> 90 90",
    },
    "sleep": {
        "tipo": "forcar-retorno",
        "descricao": "Pular a espera (retorno imediato)",
        "bytes": "C3",
        "detalhe": "ret no prologo",
    },
    "getcursorpos": {
        "tipo": "forcar-retorno",
        "descricao": "Simular movimento do mouse (retornar TRUE)",
        "bytes": "B8 01 00 00 00 C3",
        "detalhe": "mov eax,1; ret",
    },
    "cpuid": {
        "tipo": "manual",
        "descricao": "Mascarar bits de hypervisor exige emulacao; analisar caso a caso",
        "bytes": "",
        "detalhe": "verificar ECX bit 31 apos a chamada",
    },
}


def plan_for(api, categoria=None):
    """Devolve o plano de patch para uma API (fallback: manual)."""
    chave = str(api).lower()
    base = PATCHES.get(chave)
    if base:
        plano = dict(base)
    else:
        plano = {
            "tipo": "manual",
            "descricao": "Sem plano automatico; analisar o contexto da chamada",
            "bytes": "",
            "detalhe": "",
        }
    plano["alvo"] = str(api)
    if categoria:
        plano["categoria"] = categoria
    return plano


def build_plan(defesas):
    """defesas: lista de {api, categoria?} -> {'patches': [...]}."""
    return {"patches": [plan_for(d.get("api"), d.get("categoria")) for d in defesas]}


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Gera plano de patch contra defesas anti-analise.")
    ap.add_argument("--input", required=True,
                    help="JSON do inventario (lab 39) ou lista de APIs")
    ap.add_argument("--output", default=None,
                    help="arquivo de saida (padrao: stdout)")
    args = ap.parse_args(argv)

    with open(args.input, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "defesas" in data:
        defesas = data["defesas"]
    elif isinstance(data, list):
        defesas = [{"api": a} for a in data]
    elif isinstance(data, dict):
        defesas = [{"api": a} for a in data.get("apis", [])]
    else:
        raise SystemExit("erro: formato de entrada nao reconhecido")

    plano = build_plan(defesas)
    texto = json.dumps(plano, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(texto + "\n")
    else:
        sys.stdout.write(texto + "\n")


if __name__ == "__main__":
    main()
