# Lab 80 — smali-deobfuscate

Desofuscação de nomes ProGuard/R8 por heurística.

## O que faz

Renomeia métodos e campos ofuscados (`a`, `b`, `zzb...`) para nomes
legíveis derivados da assinatura: tipo de retorno para métodos
(`()Ljava/lang/String;` → `getString`, `()V` → `run`), tipo do campo
para fields (`I` → `count`). Nomes já legíveis são preservados e
colisões ganham sufixo numérico.

## Entrada

Lista de `{"kind": "method"|"field", "name": ..., "sig": ...}`.

## Saída

Lista de tuplas `(antigo, novo)`, determinística e sem colisões.

## Como rodar

```bash
python3 smali-deobfuscate.py
python3 -m unittest discover
```
