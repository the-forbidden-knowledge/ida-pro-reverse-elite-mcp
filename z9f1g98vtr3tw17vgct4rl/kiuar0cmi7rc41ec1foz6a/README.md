# Lab 79 — apk-pipeline

Pipeline de reempacotamento de APK: `decode` → `patch` → `build` → `sign` → `zipalign`.

## O que faz

Modela o workflow de clonagem de um app Android: extrai o pacote num
projeto editável (equivale ao `apktool d`), aplica patches em arquivos
smali, remonta o pacote (`apktool b`), assina e alinha os recursos.

Regra de ouro: **zipalign SEMPRE depois da assinatura** — alinhar antes
invalida a assinatura. O pipeline recusa a ordem errada com erro.

## Entrada

Dict do pacote: `{"arquivos": {...}, "manifest": {...}}`, mais a lista de
patches `(caminho, antigo, novo)` e o alias da chave.

## Saída

Dict do pacote final com `assinado=True`, `alinhado=True` e o arquivo
`META-INF/CERT.RSA`.

## Como rodar

```bash
python3 apk-pipeline.py
python3 -m unittest discover
```
