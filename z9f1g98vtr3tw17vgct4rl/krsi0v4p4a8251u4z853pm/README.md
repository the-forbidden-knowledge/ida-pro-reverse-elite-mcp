# Lab 48 — pipeline-report

O relatório final do pipeline CLONAR: consolida as 8 fases (triagem,
leitura, unpack, desobfuscação, injeção, memória, bypass, reconstrução)
num único documento.

## O que faz

Lê um manifesto que mapeia cada fase ao seu arquivo JSON de saída,
extrai o resumo de cada uma e monta o relatório com status por fase
(`ok` / `erro` / `nao-executada`). Fases sem arquivo entram como
pendentes.

## Entrada

- `--manifest JSON` — `{"triagem": "t.json", "memoria": "m.json", ...}`
- `--format json|md` — formato de saída (padrão: json)

## Saída

```json
{"relatorio": "CLONAR", "gerado_em": "2026-10-23T08:30:00",
 "fases": {"triagem": {"arquivo": "t.json", "status": "ok", "resumo": {...}},
           "unpack": {"arquivo": null, "status": "nao-executada"}},
 "resumo": {"fases_executadas": 1, "fases_totais": 8,
            "fases_pendentes": ["leitura", "unpack", ...]}}
```

## Exemplo

```bash
python3 hgrtba8s3eyyyd8ujqgex1.py --manifest manifest.json --format md --output relatorio.md
```

## Testes

```bash
python3 -m unittest discover
```
