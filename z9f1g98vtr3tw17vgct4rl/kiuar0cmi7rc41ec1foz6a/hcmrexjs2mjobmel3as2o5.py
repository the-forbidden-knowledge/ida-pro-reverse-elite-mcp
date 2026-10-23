#!/usr/bin/env python3
"""Pipeline de reempacotamento de APK.

Ordem correta: decode -> patch -> build -> sign -> zipalign.
Regra de ouro: o alinhamento (zipalign) SEMPRE depois da assinatura;
alinhar antes invalida a assinatura.
"""

import argparse
import json
import sys

ETAPAS = ["decode", "patch", "build", "sign", "zipalign"]


def decode(pacote):
    """Extrai o pacote num projeto editável (equivale ao apktool d)."""
    return {
        "arquivos": dict(pacote.get("arquivos", {})),
        "manifest": dict(pacote.get("manifest", {})),
    }


def patch_smali(projeto, patches):
    """Aplica patches (caminho, antigo, novo) nos arquivos do projeto."""
    arquivos = dict(projeto["arquivos"])
    aplicados = 0
    for caminho, antigo, novo in patches:
        if caminho in arquivos and antigo in arquivos[caminho]:
            arquivos[caminho] = arquivos[caminho].replace(antigo, novo)
            aplicados += 1
    saida = dict(projeto)
    saida["arquivos"] = arquivos
    saida["patches_aplicados"] = aplicados
    return saida


def build(projeto):
    """Remonta o pacote (equivale ao apktool b); ainda não assinado."""
    return {
        "arquivos": dict(projeto["arquivos"]),
        "manifest": dict(projeto["manifest"]),
        "assinado": False,
        "alinhado": False,
    }


def sign(pacote, alias="chave"):
    """Assina o pacote (adiciona META-INF)."""
    arquivos = dict(pacote["arquivos"])
    arquivos["META-INF/CERT.RSA"] = "assinatura:" + alias
    saida = dict(pacote)
    saida["arquivos"] = arquivos
    saida["assinado"] = True
    return saida


def zipalign(pacote):
    """Alinha recursos em 4 bytes. Só é válido depois da assinatura."""
    if not pacote.get("assinado"):
        raise ValueError("zipalign antes da assinatura invalida a assinatura")
    saida = dict(pacote)
    saida["alinhado"] = True
    return saida


def executar(pacote, ordem, patches=(), alias="chave"):
    """Executa as etapas na ordem dada, validando a sequência."""
    projeto = None
    atual = pacote
    for etapa in ordem:
        if etapa == "decode":
            projeto = decode(atual)
            atual = projeto
        elif etapa == "patch":
            base = projeto if projeto is not None else decode(atual)
            atual = patch_smali(base, patches)
            projeto = atual
        elif etapa == "build":
            base = projeto if projeto is not None else decode(atual)
            atual = build(base)
        elif etapa == "sign":
            atual = sign(atual, alias)
        elif etapa == "zipalign":
            atual = zipalign(atual)
        else:
            raise ValueError("etapa desconhecida: %s" % etapa)
    return atual


def pipeline(pacote, patches=(), alias="chave"):
    """Pipeline completo na ordem correta."""
    return executar(pacote, ETAPAS, patches, alias)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Pipeline de reempacotamento de APK")
    ap.add_argument("--alias", default="chave", help="alias da chave de assinatura")
    args = ap.parse_args(argv)
    demo = {
        "arquivos": {
            "smali/com/exemplo/a.smali": "const-string v0, \"x=1\"",
            "AndroidManifest.xml": "<manifest/>",
        },
        "manifest": {"pacote": "com.exemplo.app"},
    }
    resultado = pipeline(
        demo, [("smali/com/exemplo/a.smali", "x=1", "x=2")], args.alias
    )
    json.dump(
        {
            "assinado": resultado["assinado"],
            "alinhado": resultado["alinhado"],
            "arquivos": sorted(resultado["arquivos"]),
        },
        sys.stdout,
        ensure_ascii=False,
        indent=2,
    )
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
