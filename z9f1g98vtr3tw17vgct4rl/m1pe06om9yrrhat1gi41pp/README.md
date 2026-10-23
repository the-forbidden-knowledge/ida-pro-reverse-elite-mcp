# Lab 52 — clone-verify

Verifica a paridade do clone contra a spec original: compara a spec de
comportamentos do original com a spec do clone e gera o relatório de
paridade com hashes SHA-256 dos artefatos.

## O que faz

Compara descrições normalizadas (caixa e espaços ignorados) entre as duas
specs do lab 43 e classifica cada comportamento como coberto, faltando ou
extra. Calcula `%` de cobertura, gera SHA-256 dos artefatos (arquivos ou
diretórios, recursivo) e emite o veredito: `CLONADO 100%` somente quando
não há faltando nem extras.

## Entrada

- `--original JSON` — spec do original (lab 43)
- `--clone JSON` — spec do clone (lab 43)
- `--artefatos ...` — arquivos/diretórios para hash (opcional)
- `--output JSON` — saída (padrão: stdout)

## Saída

```json
{"cobertos": [{"id": "BEH-001", "descricao": "abre socket"}],
 "faltando": [], "extras": [],
 "cobertura_pct": 100.0, "total_original": 2,
 "artefatos": [{"arquivo": "clone.py", "sha256": "..."}],
 "veredito": "CLONADO 100%"}
```

## Exemplo

```bash
python3 f0y1cl3d7nbg2h9nrzx0dw.py --original spec_orig.json --clone spec_clone.json --artefatos clone/ --output relatorio.json
```

## Testes

```bash
python3 -m unittest discover
```
