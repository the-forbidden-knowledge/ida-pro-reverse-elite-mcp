#!/usr/bin/env python3
"""Desenrolar da CREDHIST -- cadeia de senhas antigas (fixtures sinteticas).

Modelo: hashes SHA-512 de todas as senhas anteriores ficam encadeados; cada
entrada i cifra o hash da senha anterior com chave derivada do hash da senha
atual. Com a senha atual, descriptografa-se a anterior, e assim por diante,
ate' o hash que abre uma Master Key arquivada.

Cifra: keystream SHA-512 em modo contador (stand-in documentado para o AES).
Cada entrada carrega HMAC-SHA-512 para detectar adulteracao.
"""
import argparse
import hashlib
import hmac
import json

ITERATIONS = 5600


def _kdf(h: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha512", h, b"credhist", ITERATIONS, dklen=32)


def _keystream(key: bytes, n: int) -> bytes:
    out, c = b"", 0
    while len(out) < n:
        out += hashlib.sha512(key + c.to_bytes(8, "big")).digest()
        c += 1
    return out[:n]


def _xor(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def build_chain(passwords: list) -> list:
    """Constroi a cadeia: passwords[0] = mais antiga, [-1] = atual."""
    hashes = [hashlib.sha512(p.encode()).digest() for p in passwords]
    entries = []
    for i in range(1, len(passwords)):
        key = _kdf(hashes[i])
        blob = _xor(hashes[i - 1], _keystream(key, 64))
        mac = hmac.new(key, blob, hashlib.sha512).hexdigest()
        entries.append({"index": i, "blob": blob.hex(), "hmac": mac})
    return entries


def unwind(current_password: str, entries: list) -> list:
    """Desenrola a cadeia a partir da senha atual. Retorna os hashes antigos."""
    h = hashlib.sha512(current_password.encode()).digest()
    recovered = []
    for e in sorted(entries, key=lambda x: x["index"], reverse=True):
        key = _kdf(h)
        blob = bytes.fromhex(e["blob"])
        mac = hmac.new(key, blob, hashlib.sha512).hexdigest()
        if not hmac.compare_digest(mac, e["hmac"]):
            raise ValueError(f"entrada {e['index']} adulterada ou senha errada")
        h = _xor(blob, _keystream(key, 64))
        recovered.append(h.hex())
    return recovered


def main(argv=None):
    ap = argparse.ArgumentParser(description="Desenrolar da CREDHIST (sintetico)")
    ap.add_argument("--passwords", nargs="+",
                    default=["antiga1", "antiga2", "atual3"])
    a = ap.parse_args(argv)
    entries = build_chain(a.passwords)
    rec = unwind(a.passwords[-1], entries)
    print(json.dumps({"entradas": len(entries),
                      "hashes_recuperados": len(rec),
                      "primeiro_hash": rec[-1][:16] + "..."}, indent=2))


if __name__ == "__main__":
    main()
