# Lab 37 — idc-generate

Gera um script IDC que rotula endereços com nomes de API (o equivalente
automatizado de renomear chamadas manualmente no disassembler).

## O que faz

Lê um mapa `{endereço: nome_api}` em JSON e produz um script IDC
(`#include <idc.idc>` + `static main()` com chamadas `set_name()`),
ordenado por endereço. Endereços podem vir como `"0x401000"`,
`"4198400"` (decimal em texto) ou inteiro.

## Entrada

JSON com o mapa direto ou aninhado em `"labels"`:

```json
{"labels": {"0x401000": "CreateRemoteThread", "4198400": "VirtualAllocEx"}}
```

## Saída

Texto IDC (stdout ou arquivo via `--output`):

```idc
#include <idc.idc>

static main() {
    set_name(0x401000, "CreateRemoteThread");
    set_name(0x400040, "VirtualAllocEx");
}
```

## Exemplo

```bash
python3 kxq86vk9dq02q7psd4u9oj.py --input labels.json --output rotulos.idc
python3 kxq86vk9dq02q7psd4u9oj.py --input labels.json
```

## Testes

```bash
python3 -m unittest discover
```
