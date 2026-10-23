# k1zlgokezxoi94chw88qpu

Compara dois relatórios de triagem — binário empacotado (antes) e dump
(depois) — e avalia se o unpacking funcionou.

## O que faz

Cruza quatro métricas entre o antes e o depois:

- **entropia média**: empacotado tem entropia alta; dump normalizado cai
- **imports**: dump revela muito mais imports que o empacotado
- **seções**: dump costuma expor mais seções
- **tamanho**: dump tende a ser maior

Cada sinal soma pontos; com 3+ pontos o veredito é `unpacked: true`,
com a lista de motivos.

## Entrada

Dois arquivos JSON com os campos `avg_entropy`, `imports`, `sections`, `size`.

## Saída

JSON com `unpacked`, `score`, `metrics` e `reasons`.

## Exemplo

```bash
python3 ojg3mycarz10qyln7fvo0m.py packed.json dump.json
python3 ojg3mycarz10qyln7fvo0m.py packed.json dump.json -o resultado.json
```
