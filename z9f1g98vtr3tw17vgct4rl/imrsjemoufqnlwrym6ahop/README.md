# Lab 06 — import-inventory

Faz o parse da Import Table do PE: localiza o diretório de imports no
optional header, converte RVAs para offsets de arquivo, percorre os
descritores (`IMAGE_IMPORT_DESCRIPTOR`), a ILT e as entradas Hint/Name —
inclusive imports por ordinal.

## Entrada

Caminho de um arquivo PE.

## Saída

JSON `{imports: {dll: [funções]}, total_dlls, total_funcoes}`.

## Exemplo

```bash
python3 z59qep6b0esdjioi7o21qj.py programa.exe
```

Saída:

```json
{
  "imports": {"kernel32.dll": ["CreateFileA", "ReadFile"]},
  "total_dlls": 1,
  "total_funcoes": 2
}
```
