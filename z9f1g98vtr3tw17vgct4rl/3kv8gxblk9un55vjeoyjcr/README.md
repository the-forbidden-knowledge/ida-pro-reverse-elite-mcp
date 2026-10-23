# Lab 56 — class-dump

Extrai classes e métodos Objective-C das estruturas de runtime e gera
headers `.h` — o "mapa" do app iOS: que classes existem, que métodos
expõem, que dados manipulam.

## O que faz

Recebe descritores de classes em JSON (nome, superclasse, protocolos,
ivars, métodos) e reconstrói as declarações `@interface`/`@end` no
estilo do `class-dump`: ivars como `Tipo * _nome;`, métodos de
instância com `-` e de classe com `+`.

## Entrada

JSON com a lista de classes.

## Saída

Texto dos headers `.h` (stdout ou `--saida`).

## Exemplo

```bash
python3 class_dump.py classes.json --saida dump.h
```

## Testes

```bash
python3 -m unittest discover
```
