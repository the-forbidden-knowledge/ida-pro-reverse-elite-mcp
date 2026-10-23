#!/usr/bin/env python3
"""Inventário de capacidades: frameworks/APIs linkadas → o que o app pode fazer.

Dado o inventário de imports (como o `otool -L` no iOS ou a tabela de
imports no PE/ELF), mapeia cada framework/biblioteca para capacidades
(rede, cripto, localização, câmera...) — o mapa barato e rápido que
direciona a análise profunda.
"""

import argparse
import json
import sys

CAPS = {
    # iOS / macOS
    "CFNetwork": ["rede"], "Network": ["rede"],
    "CoreLocation": ["localizacao"], "CoreMotion": ["sensores"],
    "AddressBook": ["contatos"], "Contacts": ["contatos"],
    "Security": ["cripto"], "CommonCrypto": ["cripto"],
    "AVFoundation": ["camera", "microfone"], "CoreAudio": ["microfone"],
    "HealthKit": ["saude"], "HomeKit": ["iot"],
    "CoreBluetooth": ["bluetooth"], "CoreNFC": ["nfc"],
    "WebKit": ["rede", "web"], "SafariServices": ["web"],
    "CoreData": ["persistencia"], "CloudKit": ["nuvem"],
    "CryptoKit": ["cripto"],
    # Windows
    "wininet": ["rede"], "urlmon": ["rede"], "ws2_32": ["rede"],
    "crypt32": ["cripto"], "bcrypt": ["cripto"],
    "advapi32": ["registro", "persistencia"], "shell32": ["sistema"],
    "wtsapi32": ["sistema"], "psapi": ["processos"],
    # Linux / multiplataforma
    "libcurl": ["rede"], "libssl": ["cripto"], "libcrypto": ["cripto"],
    "libpcap": ["rede", "sniffing"], "libusb": ["usb"],
    "libsqlite3": ["persistencia"], "libdbus": ["ipc"],
}


def _chave(item: str) -> str:
    """Normaliza 'CFNetwork.framework/CFNetwork' → 'CFNetwork'."""
    base = item.split("/")[-1]
    for sufixo in (".framework", ".dylib", ".dll", ".so"):
        if base.endswith(sufixo):
            base = base[: -len(sufixo)]
    return base


def inventory(itens: list) -> dict:
    """Mapeia cada item linkado para suas capacidades (ou ['desconhecida'])."""
    return {item: CAPS.get(_chave(item), ["desconhecida"]) for item in itens}


def summarize(inv: dict) -> dict:
    """Conta capacidades e calcula um escore de exposição (0–100)."""
    contagem = {}
    for caps in inv.values():
        for cap in caps:
            contagem[cap] = contagem.get(cap, 0) + 1
    sensiveis = {"localizacao", "camera", "microfone", "contatos", "saude", "sniffing"}
    expostas = sum(1 for c in contagem if c in sensiveis)
    escore = min(100, expostas * 20 + (10 if "rede" in contagem else 0))
    return {"por_capacidade": contagem, "escore_exposicao": escore,
            "total_itens": len(inv)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Inventário de capacidades por imports.")
    ap.add_argument("arquivo", help="JSON com a lista de frameworks/APIs")
    args = ap.parse_args(argv)
    with open(args.arquivo, encoding="utf-8") as f:
        itens = json.load(f)
    inv = inventory(itens)
    print(json.dumps({"inventario": inv, "resumo": summarize(inv)},
                     indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
