# lpoeo3swubbrqw122jmi2c

Detecta o padrão de hook via trampolim: `ReadProcessMemory` →
`VirtualProtect` → `WriteProcessMemory` (lê o original, afrouxa a proteção,
aplica o patch).

## O que faz

- Normaliza os imports (minúsculas, sem sufixo `Ex`/`A`/`W`)
- Verifica presença das três APIs do padrão
- Quando recebe o grafo de chamadas, confere a ordem
- Devolve `detected`, `matched`, `missing` e `in_order`

## Entrada

JSON com `imports` (`{dll: [funções]}`) e `calls` (`[[origem, destino]]`, opcional).

## Saída

JSON com `detected`, `technique`, `matched`, `missing`, `in_order`.

## Exemplo

```bash
python3 ijkmsk91ju98zx9czr5t6e.py trace.json
python3 ijkmsk91ju98zx9czr5t6e.py trace.json -o hook.json
```
