# Lab 43 — behavior-spec

Transforma a lista livre de comportamentos observados numa especificação
estruturada em JSON — a base do que o clone precisa reproduzir.

## O que faz

Lê um arquivo texto (um comportamento por linha) e atribui a cada um um
id (`BEH-001`, `BEH-002`…) com `descricao`, `pre_condicoes` e `efeitos`.
O formato estendido usa `;;` como separador.

## Entrada

```text
# observacoes da analise dinamica
abre socket ;; rede disponivel ;; conexao tcp estabelecida
cria arquivo temporario
```

## Saída

```json
{"comportamentos": [
  {"id": "BEH-001", "descricao": "abre socket",
   "pre_condicoes": "rede disponivel", "efeitos": "conexao tcp estabelecida"}
]}
```

## Exemplo

```bash
python3 50x6rnt1dsaz2bm9gktlzd.py --input observacoes.txt --output spec.json
```

## Testes

```bash
python3 -m unittest discover
```
