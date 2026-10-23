# Lab 89 — log-leak

Caça a vazamentos de `Log.x()` pós-ofuscação.

## O que faz

Percorre o smali e encontra chamadas `Log.d/e/i/w/v()` cujos
argumentos vêm de `const-string`. Essas chamadas frequentemente vazam
os nomes originais que o ofuscador tentou esconder — tags e mensagens
revelam a semântica real do código.

## Entrada

Lista de linhas smali.

## Saída

`[{"linha": N, "nivel": "d"|"e"|"i"|"v"|"w", "tag": ..., "msg": ...}]`;
registradores sem `const-string` viram `"?"`.

## Como rodar

```bash
python3 log-leak.py
python3 -m unittest discover
```
