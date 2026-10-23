# Lab 58 — capability-inventory

Mapeia frameworks e APIs linkadas para capacidades: o que o app
* pode * fazer (rede, cripto, localização, câmera...).

## O que faz

Recebe o inventário de imports (como o `otool -L` no iOS ou a tabela
de imports no PE/ELF) e traduz cada item para capacidades, com um
escore de exposição (0–100) que sobe com capacidades sensíveis. É o
mapa barato e rápido que direciona a análise profunda do motor.

## Entrada

JSON com a lista de frameworks/APIs.

## Saída

JSON com o inventário por item e o resumo (contagem por capacidade +
escore).

## Exemplo

```bash
echo '["CFNetwork","CoreLocation","Security"]' > fw.json
python3 capability_inventory.py fw.json
```

## Testes

```bash
python3 -m unittest discover
```
