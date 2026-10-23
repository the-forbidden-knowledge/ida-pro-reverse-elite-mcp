# Lab 61 — lsa-secrets

## O que faz

Parseia um hive Security simulado (JSON) e extrai os segredos LSA. Segredos de
contas de serviço vivem em subchaves `_SC_<nome>` sob
`HKLM\Security\Policy\Secrets`. O relatório sai com valores redacted por
padrão (`--show` exibe, só em lab).

## Uso

```bash
python3 lsa-secrets.py --hive hive.json
python3 -m unittest discover
```
