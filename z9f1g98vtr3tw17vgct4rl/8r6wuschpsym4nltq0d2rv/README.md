# Lab 71 — strace-oracle

## O que faz

Oráculo de dependências de runtime para binário black-box: lê um log do
`strace`, coleta os `ENOENT` na janela final antes do `exit` (o último costuma
ser o fatal) e emite a lista única de dependências ausentes — arquivos,
bibliotecas, dispositivos e binários.

## Por que importa

Responde "o que este binário precisa para rodar" sem código-fonte. É a
contraparte dinâmica da análise estática: alimenta a montagem do pacote de
runtime do clone e a construção da jail de análise.

## Uso

```bash
python3 strace_oracle.py alvo.strace -o deps.json
python3 strace_oracle.py alvo.strace --janela 60
```

## Testes

```bash
python3 -m unittest discover
```
