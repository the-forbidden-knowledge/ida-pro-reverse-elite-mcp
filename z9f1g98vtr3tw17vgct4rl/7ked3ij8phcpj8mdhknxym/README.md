# Lab 02 — strings-extract

Extrai strings legíveis de um arquivo binário, com o offset de cada uma.
Cobre ASCII (caracteres imprimíveis) e UTF-16LE (pares caractere + byte
nulo, comum em binários Windows). Strings revelam URLs, nomes de API,
mensagens de erro e outros indícios antes mesmo de abrir o desmontador.

## Entrada

Caminho de um arquivo binário.

## Saída

JSON: lista de `{offset, encoding, text}` ordenada por offset.

## Exemplo

```bash
python3 k2kkjnz1dcoa2jviigqdff.py programa.exe
python3 k2kkjnz1dcoa2jviigqdff.py programa.exe --min-len 6 --encoding ascii -o strings.json
```

Saída:

```json
[
  {"offset": 1024, "encoding": "ascii", "text": "CreateFileW"},
  {"offset": 2048, "encoding": "utf-16le", "text": "SOFTWARE\\Exemplo"}
]
```
