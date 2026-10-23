# Lab 46 — coverage-verify

Calcula o percentual de cobertura do clone a partir do ledger de
obrigações: quantas foram cumpridas, quantas faltam e onde estão os gaps.

## O que faz

Conta obrigações `feito` vs `pendente`, calcula `cobertura_pct`, lista os
ids de comportamento com pendências (`gaps`) e detalha por comportamento.

## Entrada

- `--input JSON` — ledger do lab 45 `{"obrigacoes": [{comportamento, status}]}`

## Saída

```json
{"total": 4, "feitas": 2, "pendentes": 2, "cobertura_pct": 50.0,
 "gaps": ["BEH-002", "BEH-003"],
 "por_comportamento": {"BEH-001": {"total": 2, "feitas": 2}}}
```

## Exemplo

```bash
python3 3vvtel22lho9l5gwbqhfbr.py --input ledger.json
```

## Testes

```bash
python3 -m unittest discover
```
