# Lab 12 — symbolic-constants

Varre um dump de disassembly (texto) e traduz valores imediatos
hexadecimais conhecidos para nomes simbólicos: chaves de registro
(`HKEY_*`), códigos de status (`STATUS_*`), flags de memória
(`PAGE_*`, `MEM_*`) e de processo (`CREATE_SUSPENDED`). Aceita os formatos
`0x...` e `...h` (estilo MASM).

## Entrada

Arquivo texto com o disassembly.

## Saída

JSON: lista de `{linha, texto, valor, nome}`.

## Exemplo

```bash
python3 x58o4f9k4gko5a3pi5bvwc.py dump.txt
```

```text
.text:00401000 push    80000001h
```

vira `{"linha": 1, "valor": "0x80000001", "nome": "HKEY_CURRENT_USER"}`.
