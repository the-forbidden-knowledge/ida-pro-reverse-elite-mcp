# Lab 67 — ngen-detect

## O que faz

Classifica módulos .NET carregados: `.ni.dll` = Native Image (NGEN, código
nativo) vs `.dll` = IL (bytecode). Detecta qual variante do engine PowerShell
(`System.Management.Automation`) está carregada — nativa ou IL — o que decide
onde breakpoints e hooks funcionam na análise.

## Uso

```bash
python3 ngen-detect.py --modules a.ni.dll b.dll
python3 -m unittest discover
```
