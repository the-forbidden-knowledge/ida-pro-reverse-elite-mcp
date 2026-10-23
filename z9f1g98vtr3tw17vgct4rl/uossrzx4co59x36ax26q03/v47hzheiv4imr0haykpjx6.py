#!/usr/bin/env python3
"""Negociacao de dialeto SMB + deteccao de downgrade (fixtures sinteticas).

O cliente oferece dialetos em ordem; o servidor escolhe o maior em comum.
Quirk documentado: o SMB 3.x detecta downgrade forcado (derruba a sessao +
Event ID 1005), mas so' ate' 2.x -- downgrade ate' 1.0 passa batido (ponto
cego). Sem cripto mandatoria, descer de 3.0 para 1.0 desliga a criptografia.
"""
import argparse
import json

ORDER = ["1.0", "2.0", "2.1", "3.0", "3.1.1"]
_RANK = {d: i for i, d in enumerate(ORDER)}


def negotiate(client_offer: list, server_offer: list) -> str | None:
    """Maior dialeto em comum; None se nenhum."""
    comuns = [d for d in ORDER if d in client_offer and d in server_offer]
    return comuns[-1] if comuns else None


def detect_downgrade(offered_max: str, negotiated: str | None,
                     event1005: bool) -> dict:
    """Detecta downgrade malicioso, incluindo o ponto cego do 1.0."""
    if negotiated is None:
        return {"status": "no-common-dialect", "suspicious": True}
    if _RANK[negotiated] < _RANK[offered_max]:
        if negotiated == "1.0" and not event1005:
            return {"status": "downgrade-blind-spot",
                    "suspicious": True,
                    "detail": ("caiu para 1.0 sem Event 1005: "
                               "downgrade nao detectado pelo servidor")}
        if not event1005:
            return {"status": "downgrade-undetected", "suspicious": True}
        return {"status": "downgrade-detected", "suspicious": False}
    return {"status": "ok", "suspicious": False}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Negociacao de dialeto SMB")
    ap.add_argument("--client", nargs="+", default=["3.1.1", "3.0", "2.1"])
    ap.add_argument("--server", nargs="+", default=["3.0", "2.1", "1.0"])
    ap.add_argument("--event1005", action="store_true")
    a = ap.parse_args(argv)
    neg = negotiate(a.client, a.server)
    print(json.dumps({"negotiated": neg,
                      "analysis": detect_downgrade(max(a.client, key=_RANK.get),
                                                   neg, a.event1005)},
                     indent=2))


if __name__ == "__main__":
    main()
