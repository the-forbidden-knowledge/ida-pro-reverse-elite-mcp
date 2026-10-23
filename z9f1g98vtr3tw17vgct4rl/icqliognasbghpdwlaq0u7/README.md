# Lab 11 — library-filter

Separa o código escrito pelo autor do código de biblioteca (prefixos de
compilador, thunks, STL etc.) a partir de padrões regex. Em binários
reais, a maior parte das funções é biblioteca — filtrá-las deixa visível
só o que interessa.

## Entrada

JSON `{functions: [...]}` com opcional `library_patterns: [...]`, e/ou
`--pattern` repetido na CLI.

## Saída

JSON `{biblioteca: [...], autor: [...]}`.

## Exemplo

```bash
python3 kjifdy5ei4ewouwqln20jx.py export.json --pattern "^j_" --pattern "^sub_"
```
