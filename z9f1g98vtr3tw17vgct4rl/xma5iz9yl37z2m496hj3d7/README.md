# Lab 10 — strings-navigate

Dada uma string e uma exportação em JSON (`functions` com `addr`/`size` e
`strings` com `xrefs`), segue cada referência cruzada da string até a
função cujo intervalo de endereços a contém. Strings interessantes
(comandos, URLs, chaves) viram assim pontos de entrada para a análise.

## Entrada

JSON de exportação + `--string TEXTO`.

## Saída

JSON `{string, usos: [{funcao, via}]}`.

## Exemplo

```bash
python3 i3kcp6jz9krnhnzl52k04y.py export.json --string "cmd.exe"
```
