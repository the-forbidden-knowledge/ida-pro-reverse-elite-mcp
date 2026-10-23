# Lab 83 — dumpdecrypted

Despejo de Mach-O descriptografado (estilo dumpdecrypted).

## O que faz

Apps de loja chegam criptografados no disco (cryptid=1) e o loader os
descriptografa em runtime. Este lab simula o despejo: copia as regiões
`__TEXT` já limpas e zera o `cryptid`. Sem essa etapa, `strings` num
binário criptografado retorna lixo — é a porta de entrada obrigatória
do pipeline iOS.

## Entrada

Blob binário sintético com cabeçalho `(magic, cryptoff, cryptsize, cryptid)`.

## Saída

`{"despejado": bool, "dados": bytes, "regiao": [off, size]}`; se o
`cryptid` já for 0, retorna o binário intacto.

## Como rodar

```bash
python3 dumpdecrypted.py
python3 -m unittest discover
```
