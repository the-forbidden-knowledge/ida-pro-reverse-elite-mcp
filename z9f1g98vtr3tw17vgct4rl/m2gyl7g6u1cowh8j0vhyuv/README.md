# Lab 60 — credhist-unwind

## O que faz

Modela a CREDHIST do Windows: hashes SHA-512 de todas as senhas anteriores
encadeados, cada um cifrado com chave derivada do hash da senha seguinte. Com
a senha atual, o motor "desenrola" a cadeia até o hash mais antigo — o que
abriria uma Master Key arquivada. Cada entrada tem HMAC para detectar
adulteração.

## Divergência declarada

A cifra real usa AES via DPAPI; aqui usa-se keystream SHA-512 em modo contador
(stand-in documentado). O formato exato do arquivo CREDHIST não é reproduzido
byte a byte — só a lógica da cadeia.

## Uso

```bash
python3 credhist-unwind.py --passwords antiga1 antiga2 atual
python3 -m unittest discover
```
