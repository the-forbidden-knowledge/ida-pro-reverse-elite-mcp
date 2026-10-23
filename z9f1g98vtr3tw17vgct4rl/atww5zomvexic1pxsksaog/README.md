# Lab 42 — defense-report

Consolida os achados da fase de bypass (inventário de defesas + plano de
patch + TLS) num único relatório JSON.

## O que faz

Recebe as saídas dos labs de bypass e monta um JSON com três seções
(`defesas`, `patches`, `tls`) mais um `resumo` com as contagens e quantos
patches ainda exigem análise manual. Todas as entradas são opcionais.

## Entrada

- `--inventory JSON` — `{"defesas": [{api, categoria}], "total": N}`
- `--patches JSON` — `{"patches": [{alvo, tipo, ...}]}`
- `--tls JSON` — `{"tls_presente": bool, "total_callbacks": N}`

## Saída

```json
{
  "fase": "bypass",
  "defesas": {"inventario": [...], "total": 2, "por_categoria": {...}},
  "patches": {"plano": [...], "total": 2, "por_tipo": {"forcar-retorno": 1}},
  "tls": {"presente": true, "callbacks": 1},
  "resumo": {"defesas_encontradas": 2, "patches_planejados": 2,
             "patches_manuais": 1, "tls_presente": true}
}
```

## Exemplo

```bash
python3 87pd3uguu2cczxvkd0xxoy.py --inventory inv.json --patches plano.json --tls tls.json
```

## Testes

```bash
python3 -m unittest discover
```
