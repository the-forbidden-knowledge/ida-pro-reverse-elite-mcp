# Lab 47 — behavior-diff

Compara a spec de comportamento do original contra a do clone e aponta
o que falta, o que sobrou e o que divergiu.

## O que faz

Casa comportamentos por id (com fallback por descrição normalizada) e
classifica: `faltando` (no original, ausente no clone), `extras` (no
clone, ausente no original) e `divergentes` (mesmo id, pré-condições ou
efeitos diferentes). A comparação ignora caixa e espaços.

## Entrada

- `--original JSON` — spec do original (lab 43)
- `--clone JSON` — spec do clone

## Saída

```json
{"faltando": [{"id": "BEH-003", "descricao": "..."}],
 "extras": [{"id": "BEH-004", "descricao": "..."}],
 "divergentes": [{"id": "BEH-001",
                  "mudancas": {"efeitos": {"original": "...", "clone": "..."}}}],
 "resumo": {"total_original": 3, "total_clone": 3,
            "faltando": 1, "extras": 1, "divergentes": 1}}
```

## Exemplo

```bash
python3 ue4knvccnagx0aa7a8j78p.py --original spec_orig.json --clone spec_clone.json
```

## Testes

```bash
python3 -m unittest discover
```
