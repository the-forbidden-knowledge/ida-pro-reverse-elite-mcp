# 6w3vl9pthguka2b3jso8ee — Verificação da convenção de chamada x64

## O que faz

Recebe um trecho de disassembly em texto e verifica se a preparação de
argumentos segue a convenção de chamada x64 (até 4 argumentos nos
registradores rcx, rdx, r8, r9), detecta padrões RIP-relativos (`lea` com
`[rip+...]`) e anota observações (shadow space de 32 bytes, push de
argumentos estilo x86, ordem de registradores fora da convenção).

## Entrada

Arquivo texto com o disassembly; endereços opcionais no início da linha:

```
0x401000: mov rcx, 0x1
0x401007: mov rdx, rbx
0x40100a: call 0x402000
```

## Saída

JSON:

```json
{
  "args_ok": true,
  "rip_relative": ["0x401030"],
  "notes": ["2 argumento(s) em rcx, rdx, conforme a convencao x64"]
}
```

- `args_ok`: verdadeiro se os argumentos estão na ordem rcx→rdx→r8→r9 e
  nenhum push de argumento aparece antes da chamada.
- `rip_relative`: endereços das instruções com endereçamento RIP-relativo.
- `notes`: observações em pt-BR sobre o que foi detectado.

## Exemplo de uso

```bash
python3 146lsaj5ewqgp6lx1w3obn.py trecho.asm
python3 -m unittest discover   # executa a suíte de testes
```
