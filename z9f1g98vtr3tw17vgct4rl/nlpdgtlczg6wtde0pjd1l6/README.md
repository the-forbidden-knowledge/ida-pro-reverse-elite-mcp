# nlpdgtlczg6wtde0pjd1l6 — Geração de plano de anotações em IDC

## O que faz

Recebe um plano de renomeação e comentários e gera um script IDC aplicável no
IDA, com linhas `MakeName(0xADDR, "nome");` e `MakeComm(0xADDR, "comentario");`.

## Entrada

Arquivo JSON:

```json
{
  "functions": [
    {"addr": 4198400, "name": "funcao_principal"},
    {"addr": 4198912, "name": "decodifica_payload"}
  ],
  "comments": [
    {"addr": 4198416, "text": "chave xor derivada do relogio"}
  ]
}
```

Endereços podem ser inteiros decimais ou strings no formato `0x...`.

## Saída

Script IDC em texto (impresso na saída):

```c
static main()
{
    MakeName(0x401000, "funcao_principal");
    MakeName(0x401200, "decodifica_payload");
    MakeComm(0x401010, "chave xor derivada do relogio");
}
```

## Exemplo de uso

```bash
python3 i72bqacdxje1wevomoisc9.py plano.json > anotar.idc
python3 -m unittest discover   # executa a suíte de testes
```
