# Lab 75 — selinux-te

## O que faz

Modelo de Type Enforcement do SELinux: parse de contextos `u:r:t:s0`,
matriz de regras `allow` (tudo que não é explicitamente permitido é
negado) e transições de tipo no `exec` (com herança pai→filho quando não
há transição).

## Por que importa

Ler contextos revela a história de segurança do binário: em que domínio
ele roda, o que pode tocar. Poucas ferramentas de RE modelam MAC — quem
entende TE entende por que um binário "com permissão certa" ainda falha,
e o motor não é morto pelo SELinux ao analisar alvos confinados.

## Uso

```bash
python3 selinux_te.py --ctx system_u:system_r:httpd_t:s0 \
  --allow "allow httpd_t httpd_log_t:file { read write };" \
  --check httpd_t httpd_log_t file read
```

## Testes

```bash
python3 -m unittest discover
```
