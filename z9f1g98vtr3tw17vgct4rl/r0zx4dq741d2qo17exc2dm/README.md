# r0zx4dq741d2qo17exc2dm

Decodifica stack strings: sequências de caracteres empilhados como dwords
(little-endian) viram texto ASCII legível — o equivalente à tecla R sobre
uma sequência de MOVs.

## O que faz

- Lê o arquivo em blocos de 4 bytes
- Extrai os caracteres imprimíveis de cada bloco (ignora nulls)
- Concatena blocos vizinhos em strings, com offset de cada uma

## Entrada

Arquivo binário com dwords empilhados.

## Saída

JSON com `strings` (offset, offset_hex, string) e `count`.

## Exemplo

```bash
python3 jsgipjcsv0qjxk2hcjnewc.py regiao.bin
python3 jsgipjcsv0qjxk2hcjnewc.py regiao.bin --min-len 6 -o strings.json
```
