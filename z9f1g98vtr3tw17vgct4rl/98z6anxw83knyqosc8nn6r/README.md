# Lab 90 — mobile-report

Relatório consolidado de app mobile.

## O que faz

Junta as saídas dos labs da fase mobile num relatório único: estado
do pipeline (assinado/alinhado), fidelity score do diff, scoring de
segurança, framework detectado e contagem de vazamentos de log.
Seções ausentes são puladas sem erro.

## Entrada

Dict com chaves opcionais `pipeline`, `diff`, `mobsf`, `hibrido`,
`vazamentos` e `app`.

## Saída

`{"app": ..., "secoes": {...}, "total_secoes": N}`.

## Como rodar

```bash
python3 mobile-report.py
python3 -m unittest discover
```
