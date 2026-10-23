#!/usr/bin/env python3
"""Snapshot dos policy stores do firewall Windows (fixtures sinteticas).

Stores: PersistentStore (visivel), RSOP (GPOs), StaticServiceStore (OCULTO --
regras "Windows Service Hardening", sem API oficial) e ConfigurableServiceStore
(OCULTO -- terceiros/apps). O snapshot enumera TODOS; inventario so' do
snap-in e' incompleto.

DIVERGENCIA DOCUMENTADA (bug real): o ActiveStore (regras vivas) deveria ser a
soma de todos os stores, mas na pratica so' inclui Persistent+RSOP. O analisador
nunca usa o ActiveStore como verdade.
"""
import argparse
import json

STORES = ["PersistentStore", "RSOP", "StaticServiceStore", "ConfigurableServiceStore"]
HIDDEN = {"StaticServiceStore", "ConfigurableServiceStore"}


def snapshot(state: dict) -> dict:
    stores = {s: state.get(s, []) for s in STORES}
    # Bug documentado: ActiveStore = Persistent + RSOP (deveria somar tudo)
    active = stores["PersistentStore"] + stores["RSOP"]
    return {
        "stores": stores,
        "hidden_stores_present": sorted(HIDDEN),
        "active_store_rule_count": len(active),
        "total_rules": sum(len(v) for v in stores.values()),
        "warning": ("ActiveStore ignora os stores ocultos "
                    "(bug documentado): nao usar como verdade"),
    }


def rule_sources(state: dict) -> dict:
    """De qual store veio cada regra (para diagnostico de precedencia)."""
    out = {}
    for s in STORES:
        for r in state.get(s, []):
            out[r["name"]] = s
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Snapshot dos stores do firewall")
    ap.add_argument("--state", default="fwstate.json")
    a = ap.parse_args(argv)
    with open(a.state, encoding="utf-8") as f:
        print(json.dumps(snapshot(json.load(f)), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
