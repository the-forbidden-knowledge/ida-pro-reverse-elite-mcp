# Lab 16 — jumptable-resolve

Resolução de jump table (tabela de saltos de `switch`) a partir de hex dump.

## O que faz

Lê os bytes brutos da tabela de um arquivo de hex dump, interpreta cada
entrada como um deslocamento (RVA, little-endian) e soma ao endereço base,
produzindo o alvo (`target`) de cada `case`.

## Entrada

- Arquivo com o hex dump: bytes separados por espaço, string hex contínua
  ou linhas estilo `xxd` (`offset: bytes |ascii|`);
- `--base`: endereço base em hex (ex.: `0x401000` ou `401000`) — obrigatório;
- `--count`: número de entradas da tabela — obrigatório;
- `--ptrsize`: `4` ou `8` (padrão `4`).

## Saída

JSON na stdout, ex.:

```json
{
  "cases": [
    {"index": 0, "target": "0x401100"},
    {"index": 1, "target": "0x401150"}
  ]
}
```

## Exemplo de uso

```bash
python3 et7kucclfz81q4w51d8rcs.py --base 0x401000 --count 4 --ptrsize 4 tabela.hex
python3 -m unittest discover   # 8 testes
```

Se os bytes forem insuficientes para `--count` entradas, o programa sai com
erro (exit ≠ 0).

## Testes

`mesvozp0v5p8oztdby9uns.py` — hex dumps 100% sintéticos, gerados no próprio
teste (nenhum binário real).
