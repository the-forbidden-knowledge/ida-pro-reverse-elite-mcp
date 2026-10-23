# Lab 73 — chroot-jail

## O que faz

Monta uma jail mínima estilo `chroot()` a partir da lista de dependências do
alvo: diretórios `111` (só atravessar, sem listar), bibliotecas `555`,
configs `444`. Segredos reais (`shadow` etc.) nunca entram. Gera manifesto,
constrói a árvore e verifica os modos.

## Por que importa

O motor executa binários não confiáveis durante a análise dinâmica. A jail
mínima é o padrão de contenção do sandbox — disciplina agressiva de
permissões desde o desenho.

## Uso

```bash
python3 chroot_jail.py deps.json /tmp/jail --manifesto m.json
```

## Testes

```bash
python3 -m unittest discover
```
