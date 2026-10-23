# qospd4bifqjqxx3j6zos0g

Detecta prólogo de função patcheado: um JMP logo no início da função
indica hook inline — o conceito do apihooks.

## O que faz

- Lê os primeiros bytes de cada função (hex)
- Reconhece: `E9` (jmp rel32), `EB` (jmp rel8), `68` (push imm32,
  padrão push/ret), `FF 25` (jmp [mem] indireto)
- Separa `hooked` de `clean_count`

## Entrada

JSON com `functions`: `[{name, addr, bytes}]`.

## Saída

JSON com `hooked` (name, addr, patch), `hooked_count`, `clean_count`.

## Exemplo

```bash
python3 it4mcsmqidin2ywfrxqyjy.py funcoes.json
python3 it4mcsmqidin2ywfrxqyjy.py funcoes.json -o hooks.json
```
