# Lab 07 — anomaly-scan

Varre os bytes do arquivo procurando constantes conhecidas de
criptografia e compressão: S-boxes do AES, constantes do SHA-256, estado
inicial do MD5, delta do TEA e magic numbers de formatos (ZIP, RAR, 7z,
gzip, MZ). Encontrar essas constantes aponta onde estão as rotinas de
cripto ou os dados comprimidos embutidos.

## Entrada

Caminho de um arquivo qualquer.

## Saída

JSON: lista de `{offset, nome, tipo}` ordenada por offset.

## Exemplo

```bash
python3 k8sa05ag6rpks3b4t5lkt7.py programa.exe
```
