# ylh1syqcjv1o9sdk0hxsj6

Relatório consolidado de desobfuscação: executa os labs 26–29 sobre o
mesmo arquivo e junta os resultados num JSON único.

## O que faz

- Roda `xorsearch` (brute-force XOR 1 byte) e `stackstring-decode` sempre
- Roda `xor-key-recover` quando recebe `--plaintext` (fragmento conhecido)
- Roda `decode-emulate` quando recebe `--dsl` (mini-DSL de decode)
- Junta tudo com SHA-256 do arquivo de entrada

## Entrada

Arquivo binário (+ `--plaintext` e/ou `--dsl` opcionais).

## Saída

JSON com `input`, `sha256`, `xorsearch`, `stackstrings`, `xor_key`, `emulated`.

## Exemplo

```bash
python3 wq48w8utqpp3d0w2bmobyi.py suspeito.bin
python3 wq48w8utqpp3d0w2bmobyi.py suspeito.bin -p "http" --dsl dsl.json -o relatorio.json
```
