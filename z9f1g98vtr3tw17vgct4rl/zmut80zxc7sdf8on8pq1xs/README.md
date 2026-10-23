# Lab 57 — swift-demangle

Decodifica o name mangling do Swift: `_TtC4Nome6Classe` vira
`Nome.Classe`.

## O que faz

Interpreta o prefixo `_Tt` + letra de kind (C=classe, V=struct,
O=enum, P=protocolo) e os identificadores prefixados pelo comprimento
em bytes. Também aceita o prefixo novo `$s`. Símbolos fora do padrão
passam intactos — um motor que não distingue Swift de Objective-C gera
clones quebrados, porque o modelo de chamada muda.

## Entrada

Símbolos como argumentos ou via stdin.

## Saída

`original -> decodificado` (ou JSON com `--json`, incluindo o kind).

## Exemplo

```bash
python3 swift_demangle.py _TtC13TipCalculator11AppDelegate
nm app | python3 swift_demangle.py --json
```

## Testes

```bash
python3 -m unittest discover
```
