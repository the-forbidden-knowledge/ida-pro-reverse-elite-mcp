#!/usr/bin/env python3
"""Derivacao da cadeia de chaves do DPAPI -- analise com fixtures sinteticas.

Cadeia modelada (honesta, simplificada):
  1. PBKDF2-HMAC-SHA512(passphrase, salt128, iteracoes) -> MKPK (32 bytes).
     Iteracoes default 5600; o valor real e' lido do "registry" simulado.
  2. Arquivo de Master Key (sintetico): GUID em claro, salt em claro,
     iteration count em claro, blob cifrado, HMAC-SHA-512 de integridade
     calculado com a MKPK.
  3. Session Key derivada da Master Key descriptografada.

DIVERGENCIA DECLARADA: o algoritmo exato do CryptDeriveKey/CryptHashData nao
e' documentado; a Session Key aqui usa SHA-512(MK || contexto) truncado, apenas
como modelo de analise. O AES real e' substituido por keystream SHA-512 em modo
contador (stand-in documentado). Nenhum segredo real; tudo sintetico.
"""
import argparse
import hashlib
import hmac
import json
import sys

DEFAULT_ITERATIONS = 5600


def derive_mkp(passphrase: bytes, salt: bytes, iterations: int = DEFAULT_ITERATIONS) -> bytes:
    """PBKDF2-HMAC-SHA512 -> MKPK de 32 bytes."""
    if not isinstance(iterations, int) or iterations < 1:
        raise ValueError("iteracoes deve ser inteiro >= 1")
    return hashlib.pbkdf2_hmac("sha512", passphrase, salt, iterations, dklen=32)


def _keystream(key: bytes, nonce: bytes, n: int) -> bytes:
    out = b""
    c = 0
    while len(out) < n:
        out += hashlib.sha512(key + nonce + c.to_bytes(8, "big")).digest()
        c += 1
    return out[:n]


def _xor(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def seal_master_key(master_key: bytes, mkpk: bytes, guid: str,
                    salt: bytes, iterations: int) -> dict:
    """Cria um arquivo de Master Key sintetico (formato parcialmente em claro)."""
    nonce = hashlib.sha256(guid.encode()).digest()[:16]
    blob = _xor(master_key, _keystream(mkpk, nonce, len(master_key)))
    mac = hmac.new(mkpk, guid.encode() + salt + blob, hashlib.sha512).hexdigest()
    return {"guid": guid, "salt": salt.hex(), "iterations": iterations,
            "blob": blob.hex(), "hmac": mac, "preferred": True}


def open_master_key(mkfile: dict, mkpk: bytes) -> bytes:
    """Verifica o HMAC e descriptografa a Master Key. Erro se passphrase errada."""
    blob = bytes.fromhex(mkfile["blob"])
    salt = bytes.fromhex(mkfile["salt"])
    mac = hmac.new(mkpk, mkfile["guid"].encode() + salt + blob,
                   hashlib.sha512).hexdigest()
    if not hmac.compare_digest(mac, mkfile["hmac"]):
        raise ValueError("HMAC invalido: passphrase errada ou arquivo adulterado")
    nonce = hashlib.sha256(mkfile["guid"].encode()).digest()[:16]
    return _xor(blob, _keystream(mkpk, nonce, len(blob)))


def derive_session_key(master_key: bytes, context: bytes = b"dpapi-session") -> bytes:
    """DIVERGENCIA: modelo simplificado; o algoritmo real nao e' documentado."""
    return hashlib.sha512(master_key + context).digest()[:32]


def main(argv=None):
    ap = argparse.ArgumentParser(description="Modelo da cadeia de derivacao do DPAPI")
    ap.add_argument("--password", default="SenhaSintetica123")
    ap.add_argument("--iterations", type=int, default=DEFAULT_ITERATIONS)
    a = ap.parse_args(argv)
    salt = hashlib.sha256(b"salt-sintetico").digest()[:16]
    mkpk = derive_mkp(a.password.encode(), salt, a.iterations)
    mk = os.urandom(64) if False else hashlib.sha256(b"master-key-sintetica").digest() * 2
    mk = mk[:64]
    mkfile = seal_master_key(mk, mkpk, "12345678-1234-1234-1234-123456789abc",
                             salt, a.iterations)
    aberta = open_master_key(mkfile, mkpk)
    sess = derive_session_key(aberta)
    print(json.dumps({"mkpk_sha256": hashlib.sha256(mkpk).hexdigest()[:16],
                      "master_key_ok": aberta == mk,
                      "session_key_sha256": hashlib.sha256(sess).hexdigest()[:16],
                      "iterations": a.iterations}, indent=2))


if __name__ == "__main__":
    import os as _os
    main()
