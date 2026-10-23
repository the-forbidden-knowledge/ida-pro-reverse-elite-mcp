# Lab 51 — clone-assemble

Junta o esqueleto (lab 49) com os templates (lab 50) num projeto de clone
montado: diretório de saída com `clone.py`, README de montagem e manifesto.

## O que faz

Lê o esqueleto `.py`, identifica cada função pelo id do comportamento
(`beh_001_...` → `BEH-001`) e injeta no corpo os trechos das APIs mapeadas
para aquele comportamento. Funções sem template mantêm o
`NotImplementedError` (status `stub`). Templates sem função correspondente
vão para `templates_nao_aplicados` no manifesto.

## Entrada

- `--skeleton PY` — esqueleto do lab 49
- `--templates JSON` — templates do lab 50
- `--outdir DIR` — diretório de saída (criado se não existir)
- `--nome NOME` — nome do arquivo do clone (padrão: `clone.py`)

## Saída

- `clone.py` — projeto montado
- `README.md` — o que foi montado, o que falta, templates órfãos
- `montagem.json` — manifesto `{funcoes, templates_nao_aplicados, resumo}`

## Exemplo

```bash
python3 22c0lopwh84k1l6gfvp25e.py --skeleton esqueleto.py --templates templates.json --outdir clone/
```

## Testes

```bash
python3 -m unittest discover
```
