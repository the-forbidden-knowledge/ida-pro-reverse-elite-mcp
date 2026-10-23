# Lab 08 — triage-report

Executa os labs 01 a 07 sobre o mesmo arquivo e consolida tudo num único
JSON de triagem: hashes, strings (total + amostra), cabeçalhos PE,
entropia por seção, veredito de empacotamento, imports e anomalias.
Cada lab é carregado pelo caminho do arquivo, e uma etapa que falhe vira
`{"erro": ...}` sem derrubar o relatório.

## Entrada

Caminho de um arquivo (idealmente um PE).

## Saída

JSON com as chaves `arquivo`, `hashes`, `strings`, `pe`, `entropia`,
`empacotador`, `imports` e `anomalias`.

## Exemplo

```bash
python3 5mpyx89ub4ty7dy7sy95p9.py programa.exe
python3 5mpyx89ub4ty7dy7sy95p9.py programa.exe -o triagem.json
```
