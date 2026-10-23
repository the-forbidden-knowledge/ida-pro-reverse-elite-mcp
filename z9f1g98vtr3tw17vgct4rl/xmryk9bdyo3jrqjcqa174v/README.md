# iat-rebuild — reconstrução sintética da tabela de imports

Recebe dicas de endereços ("neste endereço há esta API") e reconstrói uma
tabela de imports sintética agrupada por DLL. Com a flag `--idc`, gera um
script IDC com `MakeName` para cada endereço, pronto para aplicar no
disassembler e renomear as thunks da IAT.

## O que faz

1. Lê um JSON com `{"hints": {"0x401000": "kernel32.CreateFileA", ...}}`.
2. Agrupa as entradas por DLL (case-insensitive), ordenadas por endereço.
3. Imprime o agrupamento em JSON — ou, com `--idc`, um script IDC.

## Entrada

Arquivo JSON. As chaves aceitam hexadecimal (`"0x401000"`), decimal
(`"4198400"`) ou inteiro; os valores usam o formato `dll.funcao`:

```json
{
  "hints": {
    "0x401000": "kernel32.CreateFileA",
    "0x401004": "kernel32.ReadFile",
    "0x402000": "user32.MessageBoxA"
  }
}
```

## Saída

Sem flag — JSON:

```json
{
  "imports": {
    "kernel32": [
      {"addr": "0x401000", "name": "CreateFileA"},
      {"addr": "0x401004", "name": "ReadFile"}
    ],
    "user32": [
      {"addr": "0x402000", "name": "MessageBoxA"}
    ]
  }
}
```

Com `--idc` — script IDC:

```c
static main() {
    auto ea;
    // kernel32
    ea = 0x00401000; MakeName(ea, "kernel32_CreateFileA");
    ea = 0x00401004; MakeName(ea, "kernel32_ReadFile");
    // user32
    ea = 0x00402000; MakeName(ea, "user32_MessageBoxA");
    Message("imports nomeados\n");
}
```

## Exemplo de uso

```bash
python3 uie1lpxr4wfkdchmwuffa3.py hints.json
python3 uie1lpxr4wfkdchmwuffa3.py hints.json --idc > renomear.idc
```

## Testes

```bash
python3 -m unittest discover
```
