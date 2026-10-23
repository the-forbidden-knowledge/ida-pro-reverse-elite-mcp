# Lab 84 — frida-hooks

Geração de scripts Frida para instrumentação dinâmica.

## O que faz

A partir de uma lista de alvos `(classe, método, tipos)`, gera o script
Frida que intercepta cada método com `Java.use` + `implementation`,
loga a chamada e repassa ao original via `apply`. É a base da extração
de segredos em runtime: o hook gerado pela análise estática revela o
que o código faz de verdade.

## Entrada

Lista de `(classe, metodo, [tipos])`; tipos vazios = sem overload.

## Saída

Código JavaScript pronto para o Frida.

## Como rodar

```bash
python3 frida-hooks.py
python3 -m unittest discover
```
