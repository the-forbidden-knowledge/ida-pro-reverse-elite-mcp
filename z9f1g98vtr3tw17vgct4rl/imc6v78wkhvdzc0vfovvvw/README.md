# Lab 93 — baroque-verdict

Veredito final da clonagem multi-formato: `CLONADO 100%`, com os
SHA-256 do alvo e do clone como prova.

## O que faz

Consome o ledger de fidelidade (lab 92), calcula a cobertura
(verificações que passaram / total) e lista as divergências por
alvo. Veredito `CLONADO 100%` só com cobertura 100% e zero
divergências; `PARCIAL` a partir de 80%; `DIVERGENTE` abaixo disso.

## Entrada

JSON do ledger + `--sha-alvo` e `--sha-clone`.

## Saída

JSON com veredito, cobertura, formatos, verificações, divergências e
os dois SHAs. Exit code 0 só para `CLONADO 100%`.

## Exemplo

```bash
python3 baroque_verdict.py ledger.json --sha-alvo <sha> --sha-clone <sha>
```

## Testes

```bash
python3 -m unittest discover
```
