# Lab 91 — multiformat-pipeline

Pipeline único de clonagem para PE, ELF, Mach-O fat e DEX: detecta o
formato de cada alvo pelo magic e despacha para o parser do lab
correspondente (labs 53–56).

## O que faz

`detect_format()` identifica elf64, macho-fat, dex ou pe (PE por
detecção apenas — MZ + assinatura `PE\0\0`). `analyze()` roda o parser
certo via `importlib` e devolve o resumo. `run_pipeline()` processa
vários alvos e totaliza por formato, com falhas isoladas por alvo.

## Entrada

Caminhos dos arquivos-alvo.

## Saída

Por alvo: arquivo, formato e resumo (ou erro). Totais por formato.

## Exemplo

```bash
python3 multiformat_pipeline.py alvo.elf app.fat classes.dex prog.exe --json
```

## Testes

```bash
python3 -m unittest discover
```
