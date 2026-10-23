# Lab 63 — wfp-snapshot

## O que faz

Tira snapshot de TODOS os policy stores do firewall Windows, incluindo os dois
ocultos (`StaticServiceStore` — regras "Windows Service Hardening" — e
`ConfigurableServiceStore`), invisíveis no snap-in. Documenta o bug real do
ActiveStore: deveria somar todos os stores, mas só inclui Persistent+RSOP.

## Uso

```bash
python3 wfp-snapshot.py --state fwstate.json
python3 -m unittest discover
```
