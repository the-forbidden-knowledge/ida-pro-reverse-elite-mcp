# Lab 66 — smb-dialect

## O que faz

Negocia o dialeto SMB (maior em comum entre cliente e servidor) e detecta
downgrade: o SMB 3.x gera Event ID 1005 ao detectar downgrade forçado, mas só
até 2.x — cair para 1.0 sem o evento é o ponto cego (assinatura de downgrade
malicioso ou stack antiga).

## Uso

```bash
python3 smb-dialect.py --client 3.1.1 3.0 --server 3.0 1.0
python3 -m unittest discover
```
