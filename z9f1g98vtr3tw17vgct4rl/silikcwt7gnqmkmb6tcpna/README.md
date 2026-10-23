# Lab 05 — packer-detect

Detecta se um executável PE está empacotado (comprimido/criptografado por
um packer) combinando três heurísticas:

1. **Entropia alta** (≥ 7.2) em alguma seção — código comprimido ou
   criptografado tem entropia próxima de 8 bits/byte;
2. **Poucos descritores de importação** (< 2) — o packer esconde os imports
   reais e reconstrói na hora de executar;
3. **Nomes de seção suspeitos** — UPX, ASPack, Themida, VMP, Enigma etc.

## Entrada

Caminho de um arquivo PE.

## Saída

JSON `{packed, reasons, import_descriptors}`. O veredito é positivo com
2 ou mais motivos.

## Exemplo

```bash
python3 ss1tloeughims6tjffpw55.py programa.exe
python3 ss1tloeughims6tjffpw55.py programa.exe --threshold 7.5
```
