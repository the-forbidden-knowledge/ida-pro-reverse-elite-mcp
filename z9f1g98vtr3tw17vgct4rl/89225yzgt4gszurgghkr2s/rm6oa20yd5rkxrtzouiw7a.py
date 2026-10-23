#!/usr/bin/env python3
"""Parse de segredos LSA em hive simulado (fixtures sinteticas).

Segredos de contas de servico ficam sob Policy\\Secrets no hive Security;
servicos tem subchave `_SC_<nome>`. Este lab parseia um hive sintetico
(JSON), lista os segredos de servico e emite relatorio com redacao.
"""
import argparse
import json

SERVICE_PREFIX = "_SC_"


def load_hive(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def list_secrets(hive: dict) -> list:
    """Retorna [(nome, valor)] de todos os segredos."""
    secrets = hive.get("HKLM\Security\Policy\Secrets", {})
    return [(k, v.get("CurrentValue", "")) for k, v in secrets.items()]


def service_secrets(hive: dict) -> list:
    """Só os segredos de contas de serviço (`_SC_<nome>`)."""
    return [(n, v) for n, v in list_secrets(hive) if n.startswith(SERVICE_PREFIX)]


def redact(value: str, keep: int = 0) -> str:
    if keep <= 0 or len(value) <= keep:
        return "***REDACTED***"
    return value[:keep] + "***REDACTED***"


def report(hive: dict, show_values: bool = False) -> dict:
    svcs = service_secrets(hive)
    return {
        "total_secrets": len(list_secrets(hive)),
        "service_secrets": [
            {"name": n, "value": v if show_values else redact(v)}
            for n, v in svcs
        ],
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Parse de segredos LSA (sintetico)")
    ap.add_argument("--hive", default="hive.json")
    ap.add_argument("--show", action="store_true",
                    help="mostra valores (padrao: redacted)")
    a = ap.parse_args(argv)
    print(json.dumps(report(load_hive(a.hive), a.show), indent=2,
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
