# Lab 41 — tls-parse

Faz o parse do TLS Directory de um executável PE (32 ou 64 bits) e lista
os callbacks registrados — pontos de execução que rodam antes do entry
point.

## O que faz

Lê os cabeçalhos do PE com `struct`: DOS → assinatura PE → COFF →
Optional Header → Data Directory[9] (TLS). Converte o `AddressOfCallBacks`
(VA) para offset de arquivo via tabela de seções e lê o array de
ponteiros terminado em NULL.

## Entrada

- `--input ARQUIVO` — executável PE

## Saída

```json
{
  "tls_presente": true,
  "bits": 32,
  "image_base": "0x400000",
  "diretorio": {"rva": "0x3000", "address_of_callbacks": "0x403100", ...},
  "callbacks": [{"va": "0x404000", "rva": "0x4000"}],
  "total_callbacks": 1
}
```

## Exemplo

```bash
python3 nd23wixgi0e1j565ctf8po.py --input amostra.exe --output tls.json
```

## Testes

```bash
python3 -m unittest discover
```
