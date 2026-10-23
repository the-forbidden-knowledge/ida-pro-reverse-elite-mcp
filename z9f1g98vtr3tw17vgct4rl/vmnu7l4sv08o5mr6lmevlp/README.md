# vmnu7l4sv08o5mr6lmevlp

Varre regiões de memória e lista as suspeitas: regiões graváveis e
executáveis (RWX) contendo código ou cabeçalho MZ — o conceito do malfind.

## O que faz

- Para cada região, verifica se a proteção inclui W e X
- Exige `has_mz` ou `has_code` para marcar como suspeita
- Pontua: base 3, +2 por MZ, +2 por código; ordena por score

## Entrada

JSON com `regions`: `[{base, size, protect, has_mz, has_code}]`.

## Saída

JSON com `suspicious` (base, size, protect, has_mz, has_code, score),
`count` e `total_regions`.

## Exemplo

```bash
python3 dbj8imukuzce65hmiabxtm.py regioes.json
python3 dbj8imukuzce65hmiabxtm.py regioes.json -o suspeitas.json
```
