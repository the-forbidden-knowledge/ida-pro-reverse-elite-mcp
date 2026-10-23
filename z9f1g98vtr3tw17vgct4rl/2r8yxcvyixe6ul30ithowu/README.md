# Lab 59 — dpapi-derive

## O que faz

Modela a cadeia de derivação de chaves do DPAPI do Windows com fixtures 100%
sintéticas: PBKDF2-HMAC-SHA512 (passphrase + salt de 128 bits + iterações,
default 5600) gera a MKPK; a MKPK abre o arquivo de Master Key (GUID/salt/
iteration count em claro + HMAC-SHA-512 de integridade); da Master Key deriva-se
a Session Key.

## Divergências declaradas

- O algoritmo exato do `CryptDeriveKey`/`CryptHashData` não é documentado: a
  Session Key usa SHA-512(MK || contexto) truncado, só como modelo de análise.
- O AES real é substituído por keystream SHA-512 em modo contador (stand-in
  documentado). Não é o DPAPI real e não descriptografa nada real.

## Uso

```bash
python3 dpapi-derive.py --password MinhaSenha --iterations 5600
python3 -m unittest discover
```
