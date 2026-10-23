# me3cvyro1kttvtrzo267a9

Detecta a cadeia clássica de injeção de processo: `OpenProcess` →
`VirtualAllocEx` → `WriteProcessMemory` → `CreateRemoteThread`.

## O que faz

- Normaliza os imports (minúsculas, sem sufixo `Ex`/`A`/`W`)
- Verifica se todas as APIs da cadeia estão presentes
- Quando recebe o grafo de chamadas, confere se aparecem **em ordem**
- Devolve `detected`, `matched`, `missing` e `in_order`

## Entrada

JSON com `imports` (`{dll: [funções]}`) e `calls` (`[[origem, destino]]`, opcional).

## Saída

JSON com `detected`, `technique`, `matched`, `missing`, `in_order`.

## Exemplo

```bash
python3 uwk6wdc1p13aqg89iw400l.py trace.json
python3 uwk6wdc1p13aqg89iw400l.py trace.json -o injecao.json
```
