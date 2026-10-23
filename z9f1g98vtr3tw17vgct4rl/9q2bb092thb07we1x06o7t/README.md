# Lab 94 — anti-ida-benchmark

Benchmark do pipeline de agentes do BAROQUE DIGITAL contra o fluxo
manual no IDA Pro, por tarefa — com honestidade declarada.

## O que faz

Recebe tarefas `{nome, ida_segundos, baroque_segundos}`, calcula o
speedup por tarefa e total, e imprime a tabela. O cenário padrão traz
5 tarefas típicas de engenharia reversa.

## Aviso honesto

Os números são **simulados/estimados** — exercitam a metodologia, não
são medições reais do IDA. Medição real exige: instrumentar o tempo
das duas abordagens no mesmo conjunto de binários, com o mesmo
analista, repetindo N vezes e reportando média/desvio. Este lab define
o formato; os números reais entram quando medidos.

## Entrada

Opcional: JSON com a lista de tarefas (`--tarefas`).

## Saída

Tabela com speedups por tarefa e total.

## Exemplo

```bash
python3 anti_ida_benchmark.py
python3 anti_ida_benchmark.py --tarefas minhas.json
```

## Testes

```bash
python3 -m unittest discover
```
