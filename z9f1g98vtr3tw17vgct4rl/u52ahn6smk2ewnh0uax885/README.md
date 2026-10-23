# u52ahn6smk2ewnh0uax885 — Rastreio de fluxo de dados para trás

## O que faz

Recebe um rastreio simulado de escrita numa global e, dada uma escrita-alvo
(`--target`), caminha para trás coletando as instruções de comparação e
atribuição anteriores que a influenciam, imprimindo a cadeia até a origem
(backward slice sobre uma global).

## Entrada

Arquivo JSON com `writes` e `reads` (registros inventados de rastreio):

```json
{
  "writes": [
    {"addr": 1024, "op": "assign", "target": "senha", "value": "input"},
    {"addr": 1040, "op": "write", "target": "global", "value": "senha"}
  ],
  "reads": []
}
```

Cada registro: `addr` (endereço), `op` (write/read/compare/assign),
`target` (variável escrita) e `value` (origem do valor).

## Saída

JSON com a cadeia de influência, da origem até a escrita-alvo:

```json
{
  "chain": [
    {"addr": 1024, "op": "assign", "detail": "senha <- input"},
    {"addr": 1040, "op": "write", "detail": "global <- senha"}
  ]
}
```

## Exemplo de uso

```bash
python3 55kzhelx13j4h96x9xtxb0.py rastreio.json --target 0x1040
python3 -m unittest discover   # executa a suíte de testes
```
