# Lab 72 — dt-needed-recursive

## O que faz

Resolve a árvore completa de dependências `DT_NEEDED` em cascata (BFS com
proteção contra ciclos) e compara com o que o `ldd` mostraria. Detecta ainda
dependências ocultas: vistas em runtime mas fora da closure estática
(a armadilha clássica do `libnss`).

## Por que importa

Um motor que empacota só o que o `ldd` lista gera clones quebrados no mundo
real. A reconstrução fiel exige resolução recursiva verdadeira.

## Uso

```bash
python3 dt_needed_recursive.py db.json app --runtime runtime.json -o rel.json
```

O `db.json` mapeia `{lib: {needed: [...]}}`; o `--runtime` é opcional.

## Testes

```bash
python3 -m unittest discover
```
