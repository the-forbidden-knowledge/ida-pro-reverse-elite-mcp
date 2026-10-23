# Lab 40 — patch-plan

Gera um plano de patch para neutralizar cada defesa anti-análise
encontrada no inventário: o que alterar, como e com quais bytes.

## O que faz

Recebe o JSON do inventário (lab 39) — ou uma lista simples de APIs —
e cruza com uma tabela de contramedidas: `IsDebuggerPresent` → forçar
retorno 0, `rdtsc` → NOPs, `Sleep` → retorno imediato etc. APIs sem
plano automático recebem `tipo: manual`.

Tipos: `forcar-retorno`, `nop`, `inverter-salto`, `zerar-flag`, `manual`.

## Entrada

- `--input JSON` — inventário (`{"defesas": [...]}`), lista `["Sleep"]`
  ou `{"apis": [...]}`

## Saída

```json
{"patches": [{"alvo": "IsDebuggerPresent", "categoria": "deteccao-debugger",
              "tipo": "forcar-retorno", "descricao": "...",
              "bytes": "B8 00 00 00 00 C3", "detalhe": "..."}]}
```

## Exemplo

```bash
python3 k9blishyhhhwfov279ga8l.py --input inventario.json --output plano.json
```

## Testes

```bash
python3 -m unittest discover
```
