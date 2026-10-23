# 5fmv8fp8wxqb3id6swfzdb

Recupera a chave de um XOR repetido usando known-plaintext: dado um
fragmento conhecido do texto original (ex.: `http`), deriva a chave.

## O que faz

- Para cada comprimento de chave (1..N) e cada offset do arquivo:
  - deriva a chave alinhando o fragmento conhecido
  - descarta candidatos inconsistentes
  - pontua a decodificação completa por legibilidade
- Devolve a melhor chave (hex + ASCII quando imprimível), o offset e o score
- Com `--decode`, grava o arquivo decodificado

## Entrada

Arquivo binário + fragmento conhecido via `--plaintext`.

## Saída

JSON com `key_hex`, `key_ascii`, `key_length`, `offset`, `score`
(e `decoded_to` quando decodifica).

## Exemplo

```bash
python3 ou9wnph48mbw4l5uta83j2.py suspeito.bin --plaintext http
python3 ou9wnph48mbw4l5uta83j2.py suspeito.bin -p http --decode limpo.bin -o chave.json
```
