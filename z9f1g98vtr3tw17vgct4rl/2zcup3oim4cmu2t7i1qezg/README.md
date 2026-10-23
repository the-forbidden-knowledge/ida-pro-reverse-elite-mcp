# Lab 78 — dnssec-hierarchy

## O que faz

Gestão de chaves de assinatura para atestação de clones: ZSK assina os
artefatos (vida curta, 30 dias), KSK assina as ZSKs (chain of trust).
Rollover disciplinado — curr→old, next→curr, nova next — com descarte da
old expirada. Sem chave curr válida, o clone não é atestado.

## Por que importa

Nenhum concorrente de clonagem pensa em assinatura de artefatos — e sem
isso não há enterprise. A disciplina curr/next/old + validade curta +
automação é key management operacional, não teórico.

## Uso

```bash
python3 dnssec_hierarchy.py init -o chaves.json
python3 dnssec_hierarchy.py rollover chaves.json --proxima zsk-3 -o chaves2.json
python3 dnssec_hierarchy.py atestar chaves2.json <sha-do-clone>
```

## Testes

```bash
python3 -m unittest discover
```
