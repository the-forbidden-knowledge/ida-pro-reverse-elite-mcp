# Lab 03 — pe-inspect

Faz o parse dos cabeçalhos de um executável PE usando só `struct`:
assinatura MZ, offset `e_lfanew`, assinatura PE, cabeçalho COFF (arquitetura,
número de seções, timestamp de compilação) e a tabela de seções (nome,
tamanho virtual, endereço virtual, tamanho bruto e características).

## Entrada

Caminho de um arquivo PE.

## Saída

JSON com `machine`, `machine_name`, `number_of_sections`, `timestamp` e a
lista `sections`.

## Exemplo

```bash
python3 2wtiqh4uk8m0i4gmwzp6d9.py programa.exe
```
