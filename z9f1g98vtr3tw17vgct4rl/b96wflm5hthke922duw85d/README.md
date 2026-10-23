# Lab 49 — spec-to-skeleton

Gera o esqueleto Python do clone a partir da spec de comportamentos: uma
função stub por comportamento, com a docstring carregando descrição,
pré-condições, efeitos e evidências.

## O que faz

Lê a spec JSON do lab 43 (`{"comportamentos": [{id, descricao,
pre_condicoes, efeitos}]}`) e, opcionalmente, o mapa do lab 44 para
enriquecer cada stub com as evidências e funções de referência. O corpo de
cada função traz TODOs e levanta `NotImplementedError`.

## Entrada

- `--spec JSON` — spec do lab 43
- `--map JSON` — mapa do lab 44 (opcional)
- `--output PY` — arquivo de saída (padrão: stdout)

## Saída

Arquivo `.py` válido, por exemplo:

```python
def beh_001_abre_socket():
    """abre socket.

    Pre-condicoes: rede disponivel
    Efeitos: conexao estabelecida

    Evidencias:
      - EV-001 [sub_401000]: chama socket()
    Funcoes de referencia: sub_401000
    """
    # TODO: implementar a partir das evidencias acima
    # TODO: funcoes de referencia: sub_401000
    raise NotImplementedError("BEH-001: pendente")
```

## Exemplo

```bash
python3 ytimej1cglr0ty5g4fwjq3.py --spec spec.json --map mapa.json --output esqueleto.py
```

## Testes

```bash
python3 -m unittest discover
```
