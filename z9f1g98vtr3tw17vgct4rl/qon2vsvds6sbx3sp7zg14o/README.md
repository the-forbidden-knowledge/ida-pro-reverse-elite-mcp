# Lab 88 — method-swizzle

Instrumentação por method swizzling (Objective-C).

## O que faz

Troca as implementações de dois métodos na tabela da classe — a
técnica de hooking do runtime Objective-C. É assim que o motor
instrumenta um app iOS sem alterar o binário: o método original passa
a apontar para o hook e vice-versa. Swizzling duplo restaura tudo.

## Entrada

Tabela `{metodo: implementacao}` + os dois métodos a trocar.

## Saída

`{"tabela": {...}, "trocados": [a, b]}`; método desconhecido gera `KeyError`.

## Como rodar

```bash
python3 method-swizzle.py
python3 -m unittest discover
```
