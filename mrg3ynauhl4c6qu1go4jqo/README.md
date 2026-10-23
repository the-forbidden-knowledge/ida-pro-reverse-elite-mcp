# ida-export — ponte IDA Pro → labs

Script IDAPython que exporta do IDA Pro o JSON consumido pelos labs de
leitura (09–20) e pelo orquestrador `9pd1ao2s9soicz7ndhxu9e/ni8imoj0zs33nddqo4cq01.py`.

## Como usar (dentro do IDA Pro)

1. Abra o binário no IDA e aguarde a auto-análise terminar.
2. Menu **File > Script file...** e selecione `uqr3e1yy66r39mr5tt2a0e.py`.
3. Escolha onde salvar o JSON (padrão: ao lado do binário, com o sufixo
   `-ida-export.json`).

## Formato gerado

```json
{
  "functions": [{"name": "...", "addr": "0x401000",
                 "calls": ["CreateFileA"], "xrefs_to": ["0x402010"]}],
  "strings":   [{"text": "...", "addr": "0x40a000", "xrefs": ["0x401020"]}],
  "imports":   {"kernel32.dll": ["CreateFileA", "ReadFile"]}
}
```

## Notas

- Este script **não roda nesta máquina**: ele usa `idaapi`, `idautils` e
  `idc`, que só existem dentro do IDA Pro. Aqui ele apenas compila
  (`python3 -m py_compile`).
- Cada seção da exportação tem `try/except` próprio: se algo falhar, a
  seção sai vazia em vez de derrubar a exportação.
- Endereços saem como strings hexadecimais (`"0x401000"`).
