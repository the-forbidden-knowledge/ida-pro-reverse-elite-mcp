# Lab 44 — evidence-link

Liga cada comportamento observado às evidências que o sustentam e às
funções onde elas aparecem — o mapa de rastreabilidade da reconstrução.

## O que faz

Cruza a spec de comportamentos (lab 43) com a lista de evidências
`{id, funcao, descricao, comportamento}` e produz, por comportamento,
as funções e evidências vinculadas. Comportamentos sem evidência vão
para `sem_evidencia` (lacunas a investigar).

## Entrada

- `--behaviors JSON` — `{"comportamentos": [{id, descricao, ...}]}`
- `--evidences JSON` — `{"evidencias": [{id, funcao, descricao, comportamento}]}`

## Saída

```json
{"mapa": {"BEH-001": {"descricao": "abre socket",
                      "funcoes": ["sub_401000"],
                      "evidencias": [{"id": "EV-001", ...}]}},
 "sem_evidencia": ["BEH-002"]}
```

## Exemplo

```bash
python3 oj6vfrk6ees32192x89s4v.py --behaviors spec.json --evidences ev.json --output mapa.json
```

## Testes

```bash
python3 -m unittest discover
```
