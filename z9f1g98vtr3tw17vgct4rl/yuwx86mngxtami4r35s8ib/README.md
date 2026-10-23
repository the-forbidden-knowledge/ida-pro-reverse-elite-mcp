# Lab 87 — mobsf-score

Scoring de segurança de app (estilo MobSF).

## O que faz

Pontua o app de 0 a 100 a partir de três sinais: permissões perigosas
(-8 cada), atividades exportadas sem permissão de proteção (-10) e
APIs arriscadas (-5). Cada desconto gera um achado tipado. É o
blueprint arquitetural do motor: ingestão → inventário → scoring.

## Entrada

`{"permissoes": [...], "atividades": [{"nome", "exportada", "permissao"}], "apis": [...]}`.

## Saída

`{"score": 0-100, "nivel": "alto"|"medio"|"baixo", "achados": [...]}`.

## Como rodar

```bash
python3 mobsf-score.py
python3 -m unittest discover
```
