# Lab 65 — service-privs

## O que faz

Inventário de privilégios por serviço (estilo `sc qprivs`): cada serviço pode
ter lista própria, independente da política global. Sinaliza privilégios
perigosos e detecta divergências contra um baseline (anomalia: "por que o
clone tem SeDebugPrivilege e o original não?").

## Uso

```bash
python3 service-privs.py --services services.json
python3 -m unittest discover
```
