#!/usr/bin/env python3
"""Privilegios por servico, estilo `sc qprivs` (fixtures sinteticas).

Cada servico pode ter lista propria de privilegios, independente da politica
global. O lab captura o inventario e sinaliza: privilegios perigosos em
servicos que nao deveriam te-los, e divergencia contra um baseline.
"""
import argparse
import json

DANGEROUS = {"SeDebugPrivilege", "SeImpersonatePrivilege", "SeTcbPrivilege",
             "SeBackupPrivilege", "SeRestorePrivilege", "SeLoadDriverPrivilege",
             "SeCreateTokenPrivilege"}


def inventory(services: dict) -> dict:
    out = {}
    for name, svc in services.items():
        privs = set(svc.get("privileges", []))
        perigosos = sorted(privs & DANGEROUS)
        out[name] = {
            "identity": svc.get("identity", "?"),
            "privileges": sorted(privs),
            "dangerous": perigosos,
            "risk": "HIGH" if perigosos else "LOW",
        }
    return out


def diff_vs_baseline(current: dict, baseline: dict) -> list:
    """Divergencias de privilegios contra o baseline (deteccao de anomalia)."""
    divs = []
    for name, svc in current.items():
        base = set(baseline.get(name, {}).get("privileges", []))
        atual = set(svc.get("privileges", []))
        for p in sorted(atual - base):
            divs.append({"service": name, "added": p,
                         "dangerous": p in DANGEROUS})
        for p in sorted(base - atual):
            divs.append({"service": name, "removed": p, "dangerous": False})
    return divs


def main(argv=None):
    ap = argparse.ArgumentParser(description="qprivs-like (sintetico)")
    ap.add_argument("--services", default="services.json")
    a = ap.parse_args(argv)
    with open(a.services, encoding="utf-8") as f:
        print(json.dumps(inventory(json.load(f)), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
