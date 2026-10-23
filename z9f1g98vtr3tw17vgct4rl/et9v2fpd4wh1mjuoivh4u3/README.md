# Lab 86 — hybrid-detect

Detecção de frameworks híbridos em apps.

## O que faz

Inspeciona a lista de arquivos do pacote e identifica o framework:
PhoneGap/Cordova pela presença de `assets/www/cordova.js`, Xamarin
pelas `assemblies/*.dll` (ou `NOTICE`). Sem evidências, o app é
nativo. É a base do dispatcher multi-framework do motor: cada
framework exige um analisador diferente.

## Entrada

Lista de caminhos de arquivos do pacote.

## Saída

`{"framework": "nativo"|"phonegap"|"xamarin"|"phonegap+xamarin", "evidencias": [...]}`.

## Como rodar

```bash
python3 hybrid-detect.py
python3 -m unittest discover
```
