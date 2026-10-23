# Lab 68 — dpapi-system

## O que faz

Modela a derivação do seed da Master Key de máquina a partir do segredo
`DPAPI_SYSTEM` dos LSA Secrets — a pista concreta mais citada sobre a
derivação não-documentada da Master Key do computador.

## Divergência declarada

O esquema real não é documentado; usa-se PBKDF2-HMAC-SHA512 como modelo de
análise, não como o algoritmo real.

## Uso

```bash
python3 dpapi-system.py --secret 5f4d3c2b1a09
python3 -m unittest discover
```
