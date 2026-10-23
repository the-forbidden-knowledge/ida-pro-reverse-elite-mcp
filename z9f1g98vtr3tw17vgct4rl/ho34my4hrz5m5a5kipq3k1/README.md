# ho34my4hrz5m5a5kipq3k1

Emula loops simples de decodificação (XOR/ADD/SUB/ROL/ROR) descritos numa
mini-DSL em JSON — sem precisar rodar o binário.

## O que faz

- Lê a DSL: lista de operações com `op`, `key`, `start` e `length`
- Aplica cada operação em sequência sobre os bytes (módulo 256)
- Grava o resultado decodificado

## Entrada

Arquivo binário + JSON da DSL, ex.:

```json
{"ops": [{"op": "sub", "key": 3}, {"op": "xor", "key": 170}]}
```

## Saída

Arquivo binário decodificado.

## Exemplo

```bash
python3 hzjr418t8gos1vsg2os9uq.py suspeito.bin dsl.json --output limpo.bin
```
