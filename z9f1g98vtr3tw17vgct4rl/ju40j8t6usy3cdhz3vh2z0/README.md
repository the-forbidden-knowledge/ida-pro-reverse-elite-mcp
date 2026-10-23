# Lab 82 — androsim-diff

Diff método-a-método entre dois apps (estilo Androsim).

## O que faz

Compara o original com o clone método por método e classifica cada um
em `identical` (corpo igual), `similar` (mudou), `new` (só no clone) ou
`deleted` (só no original). Emite o **fidelity score**: o veredito
numérico da clonagem — nenhum clonador oferece isso.

## Entrada

Dois dicts `{metodo: hash_do_corpo}` (original e clone).

## Saída

Classificação por categoria + `fidelity_score` de 0 a 100.

## Como rodar

```bash
python3 androsim-diff.py
python3 -m unittest discover
```
