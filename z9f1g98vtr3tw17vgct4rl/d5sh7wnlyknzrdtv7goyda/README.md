# Lab 04 — entropy-scan

Calcula a entropia de Shannon (bits por byte, de 0 a 8) de cada seção do
PE, mais o histograma de bytes do arquivo inteiro. Código legítimo costuma
ficar entre 4 e 6; valores acima de ~7 numa seção executável indicam
empacotamento ou criptografia.

## Entrada

Caminho de um arquivo PE.

## Saída

JSON com `sections` (nome, tamanho, entropia, alerta) e `histogram`
(256 contagens).

## Exemplo

```bash
python3 03f5dekqd2tqc9931mhc41.py programa.exe
python3 03f5dekqd2tqc9931mhc41.py programa.exe --threshold 7.2 -o entropia.json
```
