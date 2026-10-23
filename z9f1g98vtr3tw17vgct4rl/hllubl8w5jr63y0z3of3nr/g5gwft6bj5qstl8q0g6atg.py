#!/usr/bin/env python3
"""Seed DPAPI_SYSTEM da Master Key de maquina (fixtures sinteticas).

A Master Key de um computador deriva de material dos LSA Secrets de forma nao
documentada; a entrada `DPAPI_SYSTEM` e' a pista concreta mais citada como
parte do seed. Este lab modela a derivacao como KDF sobre o segredo.

DIVERGENCIA DECLARADA: o esquema real nao e' documentado; aqui usa-se
PBKDF2-HMAC-SHA512(segredo, b"machine-mk", 5600) como modelo de analise.
"""
import argparse
import hashlib
import json


def machine_mk_seed(dpapi_system_secret: bytes,
                    iterations: int = 5600) -> bytes:
    """Deriva o seed da Master Key de maquina (modelo, nao o algoritmo real)."""
    if not dpapi_system_secret:
        raise ValueError("segredo DPAPI_SYSTEM vazio")
    return hashlib.pbkdf2_hmac("sha512", dpapi_system_secret,
                               b"machine-mk-seed", iterations, dklen=32)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Seed DPAPI_SYSTEM (sintetico)")
    ap.add_argument("--secret", default="5f4d3c2b1a0987654321abcdef")
    a = ap.parse_args(argv)
    seed = machine_mk_seed(bytes.fromhex(a.secret))
    print(json.dumps({"seed_sha256": hashlib.sha256(seed).hexdigest()[:16],
                      "bytes": len(seed)}, indent=2))


if __name__ == "__main__":
    main()
