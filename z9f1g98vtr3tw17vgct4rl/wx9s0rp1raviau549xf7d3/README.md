# Lab 54 — macho-fat

Faz o parse de um binário Mach-O universal ("fat", magic `0xcafebabe`) e
extrai o slice de uma arquitetura (thinning por `cputype`).

## O que faz

Lê o cabeçalho fat em big-endian, lista as arquiteturas embutidas
(`x86_64`, `arm64`, ...) com offset e tamanho de cada slice, e recorta o
slice pedido — o primeiro passo antes de qualquer análise, para reduzir
a complexidade a 1 binário por arquitetura.

## Entrada

Caminho de um binário Mach-O fat.

## Saída

JSON com as arquiteturas, ou o slice extraído (`--thin CPUTYPE --saida`).

## Exemplo

```bash
python3 macho_fat.py app.fat
python3 macho_fat.py app.fat --thin 0x0100000c --saida app.arm64
```

## Testes

```bash
python3 -m unittest discover
```
