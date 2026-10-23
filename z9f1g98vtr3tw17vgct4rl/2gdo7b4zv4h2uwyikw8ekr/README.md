# Lab 74 — mknod-devices

## O que faz

Forense de devices: a partir de linhas `ls -l` extrai tipo (char/block),
major e minor e gera o plano de `mknod` para recriar os devices que o alvo
abre (`/dev/null`, `/dev/urandom`...) dentro da jail. Também filtra devices
direto da lista de dependências do lab 71.

## Por que importa

Um clone fiel precisa saber quais devices o alvo abre. Recriar major/minor
corretos evita comportamentos divergentes na análise dinâmica.

## Uso

```bash
python3 mknod_devices.py --ls dev.txt -o plan.json
python3 mknod_devices.py --deps deps.json -o plan.json
```

## Testes

```bash
python3 -m unittest discover
```
