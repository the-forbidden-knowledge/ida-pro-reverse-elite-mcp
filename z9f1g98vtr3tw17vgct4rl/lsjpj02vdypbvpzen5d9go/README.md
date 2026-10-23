# Lab 55 — dex-header

Faz o parse do cabeçalho de um arquivo DEX (Dalvik Executable): magic,
checksum adler32, assinatura SHA-1 e as tabelas de `string_ids`,
`type_ids`, `method_ids` e `class_defs`.

## O que faz

Lê o cabeçalho de 112 bytes, valida o magic (`dex\n035\0`) e a
`endian_tag`, e confere a integridade: o adler32 cobre tudo após o campo
de checksum; o SHA-1 cobre tudo após a assinatura.

## Entrada

Caminho de um arquivo `.dex`.

## Saída

JSON com magic, checksum, SHA-1, quantidades/offsets das tabelas e o
resultado das duas verificações de integridade.

## Exemplo

```bash
python3 dex_header.py classes.dex
```

## Testes

```bash
python3 -m unittest discover
```
