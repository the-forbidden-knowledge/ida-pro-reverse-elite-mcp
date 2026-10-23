# Lab 77 — automount-trick

## O que faz

Resolve mapas automount: wildcard `*` que casa qualquer chave, múltiplos
mounts por entrada (executados em ordem), bind mounts locais (prefixo `:`)
e a macro `&` (substituída pelo nome casado). Gera o layout do sandbox
para um alvo — base imutável compartilhada + overlay por análise.

## Por que importa

Arquitetura de sandbox multi-alvo do motor: N análises idênticas sem
duplicar gigabytes de bibliotecas. Domínio de mounts além do `chroot()`
básico — detalhe que quase ninguém documenta.

## Uso

```bash
python3 automount_trick.py auto.map ana -o sandbox.json
```

## Testes

```bash
python3 -m unittest discover
```
