# Lab 62 — token-inventory

## O que faz

Inventaria os privilégios de um token Windows (snapshot sintético em JSON),
sinaliza os perigosos habilitados (`SeDebugPrivilege`, `SeImpersonatePrivilege`,
`SeTcbPrivilege`, `SeBackupPrivilege`, `SeRestorePrivilege`,
`SeTakeOwnershipPrivilege`, `SeLoadDriverPrivilege`, `SeCreateTokenPrivilege`)
e calcula um score de exposição (enabled=10, disabled=2, removed=0).

## Uso

```bash
python3 token-inventory.py --token token.json
python3 -m unittest discover
```
