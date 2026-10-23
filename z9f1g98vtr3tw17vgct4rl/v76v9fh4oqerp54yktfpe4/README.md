# Lab 64 — wfp-simulate

## O que faz

Simula o pipeline de 5 camadas do Windows Filtering Platform: (1) regras
ocultas — Static, depois Configurable; (2) IPsec; (3) bypass autenticado;
(4) regras visíveis; (5) default do perfil. Bloqueio em qualquer camada
bloqueia tudo (exceto bypass autenticado); dentro da camada vence a regra mais
específica (best-match-wins).

## Divergência declarada

O algoritmo exato de especificidade da Microsoft não é documentado;
especificidade aqui = número de campos preenchidos, como modelo de análise.

## Uso

```bash
python3 wfp-simulate.py --rules rules.json --packet '{"direction":"out","proto":"tcp","port":443}'
python3 -m unittest discover
```
