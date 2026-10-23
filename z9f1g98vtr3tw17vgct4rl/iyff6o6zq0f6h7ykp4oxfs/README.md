# Lab 70 — credguard-report

## O que faz

Consolida as saídas dos labs 59 (dpapi-derive), 60 (credhist-unwind), 61
(lsa-secrets), 62 (token-inventory), 63 (wfp-snapshot), 65 (service-privs) e 68
(dpapi-system) num relatório único de segredos Windows — só metadados e
contagens, com valores sensíveis redacted.

## Uso

```bash
python3 credguard-report.py --inputs inputs.json
python3 -m unittest discover
```
