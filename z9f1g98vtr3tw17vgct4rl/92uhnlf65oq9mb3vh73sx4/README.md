# Lab 92 — fidelity-ledger

Ledger de fidelidade da clonagem: diff método-a-método estilo
Androsim (identical/similar/new/deleted) + verificações por formato.

## O que faz

`diff_methods()` compara as listas de métodos do original e do clone e
classifica cada um; `fidelity_score()` dá o escore 0–100 (identical
vale 1, similar vale 0,5). `ledger_entry()`/`build_ledger()` acumulam
verificações por formato (elf64, dex, macho-fat, pe) e `ledger_score()`
dá o percentual total que passou.

## Entrada

Listas de métodos `{nome, assinatura, tamanho}` ou JSON de entradas.

## Saída

Diff categorizado, escore de fidelidade e ledger em JSON.

## Exemplo

```bash
python3 fidelity_ledger.py entradas.json
```

## Testes

```bash
python3 -m unittest discover
```
