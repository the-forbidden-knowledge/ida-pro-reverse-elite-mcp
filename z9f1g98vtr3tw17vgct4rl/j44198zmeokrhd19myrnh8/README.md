# Lab 38 — memory-report

Consolida os achados da fase de memória (varredura RWX + detecção de
prólogos + script IDC) num único relatório JSON.

## O que faz

Recebe as saídas dos labs de memória e monta um JSON com três seções
(`rwx`, `hooks`, `idc`) mais um `resumo` com as contagens. Todas as
entradas são opcionais — o relatório sai mesmo com fases ausentes.

## Entrada

- `--rwx JSON` — `{"suspect_regions": [{base, size, protect, ...}, ...]}`
- `--hooks JSON` — `{"patched": [{func, addr, ...}, ...]}`
- `--idc ARQUIVO` — script `.idc` (conta as chamadas `set_name`)

## Saída

```json
{
  "fase": "memoria",
  "rwx": {"regioes_suspeitas": [...], "total": 2},
  "hooks": {"prologos_patcheados": [...], "total": 1},
  "idc": {"arquivo": "r.idc", "rotulos": 5},
  "resumo": {"regioes_rwx": 2, "prologos_patcheados": 1, "rotulos_idc": 5}
}
```

## Exemplo

```bash
python3 2sdojr99he1lxpkaefruub.py --rwx rwx.json --hooks hooks.json --idc r.idc --output rel.json
python3 2sdojr99he1lxpkaefruub.py --rwx rwx.json
```

## Testes

```bash
python3 -m unittest discover
```
