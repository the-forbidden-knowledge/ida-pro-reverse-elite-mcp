# Lab 85 — objection-repl

REPL de exploração runtime mobile (estilo Objection).

## O que faz

Simula os comandos de exploração dinâmica sem escrever JavaScript à
mão: `android hooking watch class <classe>` lista os métodos
observáveis da classe, e `memory list modules` mostra os módulos
carregados com seus endereços-base. Comandos desconhecidos retornam
erro honesto.

## Entrada

String do comando + dict do estado do app (`classes`, `modulos`).

## Saída

Dict com o resultado do comando ou `{"erro": ...}`.

## Como rodar

```bash
python3 objection-repl.py "android hooking watch class com.exemplo.Login"
python3 -m unittest discover
```
