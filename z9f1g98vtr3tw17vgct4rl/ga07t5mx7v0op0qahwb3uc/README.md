# Lab 45 — obligation-ledger

O livro-razão da reconstrução: cada comportamento vira uma obrigação que
o clone precisa cumprir, com status acompanhado até 100%.

## O que faz

A partir do mapa de rastreabilidade (lab 44), cria uma obrigação por
evidência (ou uma por comportamento sem evidência, marcada para
investigar). `--concluidas` marca obrigações como `feito`; o resto nasce
`pendente`.

## Entrada

- `--input JSON` — `{"mapa": {BEH-id: {funcoes, evidencias}}}`
- `--concluidas IDS` — ex.: `BEH-001,BEH-003` (opcional)

## Saída

```json
{"obrigacoes": [{"comportamento": "BEH-001", "evidencia": "EV-001",
                 "descricao_evidencia": "chamada WSASocket",
                 "funcao": "sub_401000", "status": "feito", "notas": ""}]}
```

## Exemplo

```bash
python3 m2ese22k0myo678menipp9.py --input mapa.json --concluidas BEH-001 --output ledger.json
```

## Testes

```bash
python3 -m unittest discover
```
