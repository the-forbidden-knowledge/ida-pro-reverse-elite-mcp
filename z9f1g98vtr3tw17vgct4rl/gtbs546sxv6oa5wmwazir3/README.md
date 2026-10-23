# Lab 50 — api-map-emit

Para cada API encontrada nas evidências, gera o trecho de código Python
equivalente a partir de uma tabela interna API → template.

## O que faz

Varre as descrições das evidências do mapa do lab 44 em busca de APIs
conhecidas (CreateFileA, socket, RegSetValueEx etc.) e emite, por API, o
trecho Python correspondente — com categoria, comportamento e evidência de
origem. Aceita ainda uma lista manual de APIs extras (`--apis`).

## Entrada

- `--map JSON` — mapa do lab 44
- `--apis TXT` — APIs extras, uma por linha (opcional)
- `--output JSON` — saída (padrão: stdout)
- `--snippet PY` — trechos concatenados num .py (opcional)

## Saída

```json
{"templates": [
  {"api": "socket", "categoria": "rede", "origem": "evidencia",
   "comportamento": "BEH-001", "funcao": "sub_401000",
   "evidencia": "EV-001", "codigo": "import socket\n..."}
]}
```

## Exemplo

```bash
python3 u4u8665mu3tq6orbfr1f6h.py --map mapa.json --output templates.json --snippet trechos.py
```

## Testes

```bash
python3 -m unittest discover
```
