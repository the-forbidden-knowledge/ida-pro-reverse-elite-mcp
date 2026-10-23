# Lab 81 — simplify-deadcode

Eliminação de código morto em grafo de chamadas smali.

## O que faz

A partir dos pontos de entrada (ex.: `onCreate`), percorre o grafo de
chamadas e marca todos os métodos alcançáveis. Métodos fora do alcance
são código morto — ofuscação típica — e saem na lista de podados, no
estilo do Simplify.

## Entrada

Grafo `{metodo: [chamadas]}` e lista de pontos de entrada.

## Saída

`{"vivos": [...], "mortos": [...], "removidos": N, "total": M}`.

## Como rodar

```bash
python3 simplify-deadcode.py
python3 -m unittest discover
```
