#!/usr/bin/env python3
"""Relatorio consolidado de segredos Windows (fixtures sinteticas).

Consolida as saidas dos labs 59 (dpapi-derive), 60 (credhist-unwind),
61 (lsa-secrets), 62 (token-inventory), 63 (wfp-snapshot), 65 (service-privs)
e 68 (dpapi-system) num relatorio unico, com redacao de valores sensiveis.
"""
import argparse
import json


def redact(value, keep: int = 4) -> str:
    s = str(value)
    if len(s) <= keep:
        return "***REDACTED***"
    return s[:keep] + "***REDACTED***"


def _redact_obj(o):
    if isinstance(o, dict):
        return {k: _redact_obj(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_redact_obj(v) for v in o]
    if isinstance(o, str) and len(o) > 12:
        return redact(o)
    return o


def build(inputs: dict) -> dict:
    """Monta o relatorio consolidado a partir das saidas dos labs."""
    secoes = {}
    if "dpapi" in inputs:
        d = inputs["dpapi"]
        secoes["dpapi"] = {"mkpk_sha256": d.get("mkpk_sha256"),
                           "master_key_ok": d.get("master_key_ok"),
                           "iterations": d.get("iterations")}
    if "credhist" in inputs:
        secoes["credhist"] = {"hashes_recuperados":
                              inputs["credhist"].get("hashes_recuperados")}
    if "lsa" in inputs:
        secoes["lsa"] = {"total_secrets":
                         inputs["lsa"].get("total_secrets"),
                         "service_secrets": [
                             s["name"] for s in
                             inputs["lsa"].get("service_secrets", [])]}
    if "token" in inputs:
        t = inputs["token"]
        secoes["token"] = {"exposure_score": t.get("exposure_score"),
                           "dangerous": [f["privilege"] for f in
                                         t.get("dangerous_enabled", [])]}
    if "wfp" in inputs:
        secoes["wfp"] = {"total_rules": inputs["wfp"].get("total_rules"),
                         "hidden_stores": inputs["wfp"].get(
                             "hidden_stores_present")}
    if "services" in inputs:
        alto = [n for n, s in inputs["services"].items()
                if s.get("risk") == "HIGH"]
        secoes["services"] = {"high_risk": alto}
    if "dpapi_system" in inputs:
        secoes["dpapi_system"] = {"seed_sha256":
                                  inputs["dpapi_system"].get("seed_sha256")}
    return {"credguard_report": secoes,
            "note": "valores sensiveis redacted; ver saidas individuais"}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Relatorio consolidado (sintetico)")
    ap.add_argument("--inputs", default="inputs.json")
    a = ap.parse_args(argv)
    with open(a.inputs, encoding="utf-8") as f:
        print(json.dumps(build(json.load(f)), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
