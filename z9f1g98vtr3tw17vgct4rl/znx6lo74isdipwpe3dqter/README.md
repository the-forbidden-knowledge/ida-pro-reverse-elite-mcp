# znx6lo74isdipwpe3dqter

Classifica a técnica provável a partir do conjunto de APIs observadas.

## O que faz

- Normaliza as APIs (minúsculas, sem `Ex`/`A`/`W`)
- Cruza com a tabela embutida: injeção, hooking, hollowing, keylogging, persistência
- Pontua cada técnica pela fração de APIs do grupo encontradas
- Devolve o ranking e a técnica mais provável (`top`)

## Entrada

JSON com `apis` (lista de nomes).

## Saída

JSON com `techniques` (nome, matched, score) e `top`.

## Exemplo

```bash
python3 fx2v25vmo0nauju9iegfj3.py apis.json
python3 fx2v25vmo0nauju9iegfj3.py apis.json -o tecnicas.json
```
