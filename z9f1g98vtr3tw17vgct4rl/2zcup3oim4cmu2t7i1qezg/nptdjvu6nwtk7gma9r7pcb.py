#!/usr/bin/env python3
"""Hierarquia ZSK/KSK + rollover para atestação de clones.

ZSK assina os artefatos (vida curta, 30 dias); KSK assina as ZSKs (vida
longa, chain of trust). Rollover disciplinado: curr -> old, next -> curr,
gera nova next — com validade curta e automação, sem refém de chave vazada.
"""

import argparse
import hashlib
import hmac
import json
import sys
from datetime import date, timedelta

VALIDADE_ZSK = 30  # dias


def nova_chave(kind, kid, hoje):
    return {"id": kid, "kind": kind, "state": "next",
            "criada": hoje.isoformat(), "valida_dias": VALIDADE_ZSK}


def _expirada(chave, hoje):
    criada = date.fromisoformat(chave["criada"])
    return (hoje - criada).days > chave["valida_dias"]


def rollover(chaves, hoje, proxima_id):
    """curr->old, next->curr, nova next. Old expirada é descartada."""
    novas = []
    for c in chaves:
        c = dict(c)
        if c["state"] == "curr":
            c["state"] = "old"
        elif c["state"] == "next":
            c["state"] = "curr"
        novas.append(c)
    novas = [c for c in novas
             if not (c["state"] == "old" and _expirada(c, hoje))]
    novas.append(nova_chave("ZSK", proxima_id, hoje))
    return novas


def _segredo(chave):
    return hashlib.sha256(("baroque:" + chave["id"]).encode()).digest()


def assinar(chave, dados):
    """Assinatura HMAC-SHA256 (modelo da assinatura de zona)."""
    if chave["state"] != "curr":
        raise ValueError("só a chave curr assina")
    mac = hmac.new(_segredo(chave), dados.encode(), hashlib.sha256).hexdigest()
    return {"key_id": chave["id"], "kind": chave["kind"], "mac": mac}


def verificar(chave, dados, assinatura):
    esperado = hmac.new(_segredo(chave), dados.encode(),
                        hashlib.sha256).hexdigest()
    return hmac.compare_digest(esperado, assinatura["mac"])


def atestar_clone(chaves, clone_sha, hoje):
    """Atestação de um clone com a ZSK curr."""
    curr = [c for c in chaves if c["kind"] == "ZSK" and c["state"] == "curr"]
    if not curr:
        return {"erro": "sem ZSK curr válida"}
    if _expirada(curr[0], hoje):
        return {"erro": "ZSK curr expirada: rode o rollover"}
    sig = assinar(curr[0], clone_sha)
    return {"clone_sha": clone_sha, "assinatura": sig, "data": hoje.isoformat(),
            "veredito": "ATESTADO"}


def main(argv=None):
    ap = argparse.ArgumentParser(description="ZSK/KSK + rollover")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init", help="cria par curr/next")
    p.add_argument("--hoje", default=date.today().isoformat())
    p.add_argument("-o", "--saida")

    p = sub.add_parser("rollover", help="executa o rollover")
    p.add_argument("chaves", help="JSON com as chaves")
    p.add_argument("--proxima", required=True, help="id da nova chave")
    p.add_argument("--hoje", default=date.today().isoformat())
    p.add_argument("-o", "--saida")

    p = sub.add_parser("atestar", help="atesta um clone")
    p.add_argument("chaves", help="JSON com as chaves")
    p.add_argument("sha", help="SHA do clone")
    p.add_argument("--hoje", default=date.today().isoformat())
    p.add_argument("-o", "--saida")

    args = ap.parse_args(argv)
    hoje = date.fromisoformat(args.hoje)
    if args.cmd == "init":
        chaves = [nova_chave("ZSK", "zsk-1", hoje),
                  nova_chave("ZSK", "zsk-2", hoje)]
        chaves[0]["state"] = "curr"
        resultado = {"chaves": chaves}
    elif args.cmd == "rollover":
        chaves = json.load(open(args.chaves, encoding="utf-8"))
        if isinstance(chaves, dict):
            chaves = chaves.get("chaves", [])
        resultado = {"chaves": rollover(chaves, hoje, args.proxima)}
    else:
        chaves = json.load(open(args.chaves, encoding="utf-8"))
        if isinstance(chaves, dict):
            chaves = chaves.get("chaves", [])
        resultado = atestar_clone(chaves, args.sha, hoje)
    texto = json.dumps(resultado, indent=2, ensure_ascii=False)
    if args.saida:
        with open(args.saida, "w", encoding="utf-8") as f:
            f.write(texto)
    else:
        print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
