# Lab 39 — antidebug-inventory

Varre os imports (e, opcionalmente, o texto de disassembly) em busca de
APIs e mnemônicos de defesa anti-análise, produzindo um inventário por
categoria.

## O que faz

Compara cada import contra uma tabela embutida de defesas conhecidas
(`IsDebuggerPresent`, `GetTickCount`, `GetCursorPos`, `RegOpenKeyExA`…)
e procura mnemônicos no disassembly (`rdtsc`, `cpuid`, `int 3`…).
Cada achado sai com `{api, categoria, origem}`.

Categorias: `deteccao-debugger`, `temporizacao`, `anti-sandbox`, `anti-vm`.

## Entrada

- `--input JSON` — `{"kernel32.dll": ["IsDebuggerPresent", ...]}` (ou `{"imports": {...}}`)
- `--disasm TXT` — texto de disassembly (opcional)

## Saída

```json
{
  "defesas": [{"api": "IsDebuggerPresent", "categoria": "deteccao-debugger",
               "origem": "imports", "dll": "kernel32.dll"}],
  "por_categoria": {"deteccao-debugger": ["IsDebuggerPresent"]},
  "total": 1
}
```

## Exemplo

```bash
python3 fa4e7im8y6mam8z81jt2sg.py --input imports.json --disasm func.txt --output inventario.json
```

## Testes

```bash
python3 -m unittest discover
```
