# qp4ap4yltvkxhk5r3qrb0c

Detecta process hollowing: `CreateProcess` com a flag `CREATE_SUSPENDED`
(0x4) combinado com escrita no processo filho.

## O que faz

- Procura `CreateProcess*` nos imports
- Procura a flag `0x4` (por valor, nome ou contexto da chamada)
- Procura `WriteProcessMemory`, `NtUnmapViewOfSection`, `SetThreadContext`, `ResumeThread`
- Veredito positivo: create + suspenso + (escrita ou unmap)

## Entrada

JSON com `apis` (lista) e `flags` (`[{value, name, context}]`).

## Saída

JSON com `detected`, `technique` e `indicators`.

## Exemplo

```bash
python3 vw0n1su0rwakdd6buguz7l.py trace.json
python3 vw0n1su0rwakdd6buguz7l.py trace.json -o hollowing.json
```
