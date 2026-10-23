# Lab 69 — firewall-ids

## O que faz

Transforma os Event IDs do Windows Filtering Platform em telemetria de rede
por processo: 5156 (conexão permitida), 5158 (bind permitido), 5157 (conexão
bloqueada), 5159 (bind bloqueado), 5152 (pacote bloqueado) e 5153 (pacote
bloqueado por filtro L2 mais restritivo — invisível na GUI). Constrói o grafo
de conexões por PID a partir de eventos sintéticos.

## Uso

```bash
python3 firewall-ids.py --events events.json
python3 -m unittest discover
```
