# Lab 01 — hash-identify

Calcula os hashes MD5, SHA-1 e SHA-256 de um arquivo, além do tamanho em
bytes. É o primeiro passo de qualquer triagem: o hash identifica a amostra
de forma única e permite buscar por ela em bases de dados.

## Entrada

Caminho de um arquivo qualquer.

## Saída

JSON com as chaves `md5`, `sha1`, `sha256` e `size`.

## Exemplo

```bash
python3 3ks95ofobzc2vqwo6p719v.py programa.exe
python3 3ks95ofobzc2vqwo6p719v.py programa.exe -o hashes.json
```

Saída:

```json
{
  "md5": "d41d8cd98f00b204e9800998ecf8427e",
  "sha1": "da39a3ee5e6b4b0d3255bfef95601890afd80709",
  "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "size": 0
}
```
