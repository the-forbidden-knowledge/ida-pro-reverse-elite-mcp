#!/usr/bin/env python3
"""Simulador do pipeline de 5 camadas do WFP (fixtures sinteticas).

Ordem das camadas:
  1. regras ocultas (Static, depois Configurable -- Configurable vence)
  2. IPsec (Connection Security)
  3. bypass autenticado ("Override block rules")
  4. regras visiveis
  5. default do perfil

Regras: bloqueio em qualquer camada bloqueia tudo (exceto bypass autenticado).
Dentro da mesma camada vence a MAIS ESPECIFICA (best-match-wins; o algoritmo
exato da Microsoft nao e' documentado -- aqui especificidade = nº de campos
preenchidos, declarado como modelo).

Semantica: camadas processadas em ordem; na primeira camada com regra
casando o pacote, a MAIS ESPECIFICA decide e o veredito e' final. Sem regra
em nenhuma camada, vale o default do perfil.
"""
import argparse
import json

LAYERS = ["static", "configurable", "ipsec", "auth_bypass", "visible", "default"]


def matches(rule: dict, pkt: dict) -> bool:
    for campo in ("direction", "proto", "port", "app", "service"):
        if campo in rule and rule[campo] != pkt.get(campo):
            return False
    return True


def specificity(rule: dict) -> int:
    return sum(1 for c in ("direction", "proto", "port", "app", "service")
               if c in rule)


def decide(pkt: dict, rules: list, default_action: str = "block") -> dict:
    """Simula o pipeline. Retorna veredito + camada decisora."""
    por_camada = {l: [] for l in LAYERS}
    for r in rules:
        por_camada.setdefault(r.get("layer", "visible"), []).append(r)
    for layer in LAYERS:
        candidatas = [r for r in por_camada.get(layer, []) if matches(r, pkt)]
        if not candidatas:
            continue
        melhor = max(candidatas, key=specificity)
        note = None
        if layer == "auth_bypass" and melhor["action"] == "allow":
            note = "bypass autenticado sobrepoe bloqueio"
        r = {"verdict": melhor["action"], "layer": layer, "rule": melhor["name"]}
        if note:
            r["note"] = note
        return r
    return {"verdict": default_action, "layer": "default", "rule": None}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Simulador WFP (sintetico)")
    ap.add_argument("--rules", default="rules.json")
    ap.add_argument("--packet", default='{"direction":"out","proto":"tcp","port":443}')
    a = ap.parse_args(argv)
    with open(a.rules, encoding="utf-8") as f:
        rules = json.load(f)
    print(json.dumps(decide(json.loads(a.packet), rules), indent=2))


if __name__ == "__main__":
    main()
