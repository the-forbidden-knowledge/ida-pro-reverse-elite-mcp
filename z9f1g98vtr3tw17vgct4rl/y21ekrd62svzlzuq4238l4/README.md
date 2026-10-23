# Lab 76 — audit2allow-loop

## O que faz

Profiling comportamental de um binário: lê denials AVC, gera regras `allow`
cruas e as clusteriza em macros de alto nível (`logging_log_file`,
`corenet_tcp_bind_all_ports`...) em vez de colar regras cruas — que viram
débito técnico.

## Por que importa

É o mesmo shape do pipeline de clonagem: observar comportamento → gerar
especificação → iterar até cobertura total. O `audit2allow` é literalmente
um gerador de spec a partir de observação, e a disciplina de clusterizar
achados brutos em padrões reutilizáveis espelha a destilação de evidências
do motor.

## Uso

```bash
python3 audit2allow_loop.py audit.log -o perfil.json
```

## Testes

```bash
python3 -m unittest discover
```
