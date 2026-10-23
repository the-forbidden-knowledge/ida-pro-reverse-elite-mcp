#!/usr/bin/env python3
"""Inventario de privilegios por token (fixtures sinteticas).

Um token carrega privilegios (SeDebugPrivilege etc.) habilitados ou nao.
Este lab inventaria o token, sinaliza os perigosos habilitados e calcula
um score de exposicao. Entrada: JSON sintetico no formato do snapshot.
"""
import argparse
import json

DANGEROUS = {
    "SeDebugPrivilege": "depura qualquer processo (extrai segredos de memoria)",
    "SeImpersonatePrivilege": "impersona qualquer cliente (escalada classica)",
    "SeTcbPrivilege": "atua como parte do SO (logon arbitrario)",
    "SeBackupPrivilege": "le qualquer arquivo ignorando ACL",
    "SeRestorePrivilege": "escreve em qualquer arquivo ignorando ACL",
    "SeTakeOwnershipPrivilege": "toma posse de qualquer objeto",
    "SeLoadDriverPrivilege": "carrega driver no kernel",
    "SeCreateTokenPrivilege": "cria tokens arbitrarios",
}

WEIGHTS = {"enabled": 10, "disabled": 2, "removed": 0}


def inventory(token: dict) -> dict:
    privs = token.get("privileges", {})
    findings = []
    for name, state in privs.items():
        if name in DANGEROUS and state == "enabled":
            findings.append({"privilege": name, "why": DANGEROUS[name]})
    score = sum(WEIGHTS.get(privs.get(p, "removed"), 0) for p in DANGEROUS)
    return {
        "user": token.get("user", "?"),
        "integrity": token.get("integrity", "?"),
        "total_privileges": len(privs),
        "dangerous_enabled": findings,
        "exposure_score": score,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Inventario de token (sintetico)")
    ap.add_argument("--token", default="token.json")
    a = ap.parse_args(argv)
    with open(a.token, encoding="utf-8") as f:
        print(json.dumps(inventory(json.load(f)), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
