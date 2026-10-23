#!/usr/bin/env python3
"""Scoring de segurança de app (estilo MobSF).

Pontua o app a partir de permissões perigosas, componentes exportados
sem proteção e APIs arriscadas. Blueprint do motor de análise.
"""

import argparse
import json
import sys

PERIGOSAS = {
    "READ_SMS",
    "SEND_SMS",
    "READ_CONTACTS",
    "RECORD_AUDIO",
    "CAMERA",
    "ACCESS_FINE_LOCATION",
    "READ_CALL_LOG",
    "SYSTEM_ALERT_WINDOW",
}

APIS_ARRISCADAS = {
    "Cipher.getInstance(DES)",
    "WebView.setJavaScriptEnabled",
    "Runtime.exec",
}


def pontuar(manifest):
    """manifest: {permissoes, atividades, apis} -> score + achados."""
    pontos = 100
    achados = []
    for p in manifest.get("permissoes", []):
        if p in PERIGOSAS:
            pontos -= 8
            achados.append({"tipo": "permissao-perigosa", "valor": p})
    for a in manifest.get("atividades", []):
        if a.get("exportada") and not a.get("permissao"):
            pontos -= 10
            achados.append({"tipo": "atividade-exportada", "valor": a["nome"]})
    for api in manifest.get("apis", []):
        if api in APIS_ARRISCADAS:
            pontos -= 5
            achados.append({"tipo": "api-arriscada", "valor": api})
    pontos = max(0, pontos)
    nivel = "alto" if pontos >= 80 else "medio" if pontos >= 50 else "baixo"
    return {"score": pontos, "nivel": nivel, "achados": achados}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Scoring de app estilo MobSF")
    args = ap.parse_args(argv)
    _ = args
    demo = {
        "permissoes": ["INTERNET", "READ_SMS"],
        "atividades": [{"nome": "Main", "exportada": True, "permissao": ""}],
        "apis": ["Cipher.getInstance(DES)"],
    }
    json.dump(pontuar(demo), sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
