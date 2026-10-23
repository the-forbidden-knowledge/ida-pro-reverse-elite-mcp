# Lab 09 — xref-trace

Dada uma API-alvo e uma exportação de funções em JSON
(`{functions: [{name, calls: [...]}]}`), reconstrói o grafo de chamadas e
enumera todas as cadeias de chamadores das funções raiz até o alvo. É o
equivalente automatizado de seguir xrefs para trás no desmontador até
achar quem chama a API.

## Entrada

JSON de exportação + `--api NOME`.

## Saída

JSON `{alvo, cadeias: [[raiz, ..., alvo], ...]}`.

## Exemplo

```bash
python3 ll91zo7q1yljfftnf60qws.py export.json --api CreateFileW
```
