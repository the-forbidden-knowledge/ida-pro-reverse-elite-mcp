# Lab 14 — control-flow

Reconhecimento de padrões de fluxo de controle em texto de disassembly.

## O que faz

Lê um arquivo de texto com disassembly (uma instrução por linha, endereços
`0x...` opcionais) e devolve a lista de padrões encontrados:

- `if`: `CMP`/`TEST` seguido de salto condicional (`Jcc`);
- `loop`: salto condicional ou `JMP` para um endereço anterior ao atual;
- `switch`: `JMP` indireto via tabela indexada
  (ex.: `jmp dword ptr [eax*4+0x404000]`).

Cada padrão sai como `{"type", "addr", "detail"}`.

## Entrada

Arquivo `.asm`/`.txt`. Aceita comentários `;` e rótulos (`nome:`).

## Saída

JSON na stdout, ex.:

```json
{
  "patterns": [
    {"type": "if", "addr": "0x401007", "detail": "cmp eax, 5 -> jle 0x401020"},
    {"type": "loop", "addr": "0x40200c", "detail": "jl 0x402004 targets earlier address"},
    {"type": "switch", "addr": "0x40300c", "detail": "indirect jump via indexed table: dword ptr [eax*4+0x404000]"}
  ]
}
```

## Exemplo de uso

```bash
python3 mptrosthdlemn4edpmu7us.py exemplo.asm
python3 -m unittest discover   # 8 testes
```

## Testes

`fj7xzoepgfnlv1wtlzglpn.py` — fixtures 100% sintéticas, geradas no próprio teste.
