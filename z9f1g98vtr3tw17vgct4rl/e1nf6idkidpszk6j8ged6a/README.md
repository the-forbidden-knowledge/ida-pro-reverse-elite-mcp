# Lab 53 — elf-parse

Faz o parse de um binário ELF64: ELF header, program headers (segmentos) e
section headers (seções), com nomes de seção resolvidos via `.shstrtab`.

## O que faz

Lê os bytes do arquivo com `struct` (só stdlib) e devolve a estrutura
completa: tipo (EXEC), máquina (x86-64), ponto de entrada, lista de
segmentos com permissões R/W/X e lista de seções com endereço e tamanho.

## Entrada

Caminho de um binário ELF64 little-endian.

## Saída

Resumo em texto ou JSON (`--json`): formato, tipo, máquina, entrada,
segmentos carregáveis e seções.

## Exemplo

```bash
python3 elf_parse.py alvo.elf
python3 elf_parse.py alvo.elf --json
```

## Testes

```bash
python3 -m unittest discover
```
