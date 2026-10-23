# Lab 15 — loop-deconstruct

Decomposição de um bloco de loop em suas partes estruturais.

## O que faz

Lê um arquivo de texto com um loop em disassembly e devolve:

- `init`: linhas de inicialização — `MOV` antes do rótulo do loop;
- `condition`: comparação + salto que fecha o loop (`CMP`/`TEST` + `Jcc`);
- `update`: atualização do contador (`INC`/`DEC`/`ADD`/`SUB` no registrador
  comparado na condição);
- `body`: demais instruções dentro do loop.

O rótulo do loop é o alvo do salto para trás; o contador é o registrador
comparado na condição.

## Entrada

Arquivo `.asm`/`.txt` com o bloco do loop. Aceita comentários `;`.

## Saída

JSON na stdout, ex.:

```json
{
  "init": "mov     ecx, 0",
  "condition": "cmp     ecx, 10\njl      loc_loop",
  "update": "inc     ecx",
  "body": [
    "mov     eax, [esi+ecx*4]",
    "add     eax, 1",
    "mov     [esi+ecx*4], eax"
  ]
}
```

## Exemplo de uso

```bash
python3 kxva252vefs4lkfh7c072l.py loop.asm
python3 -m unittest discover   # 5 testes
```

## Testes

`3ubj1gtuptqo511jmbvq8f.py` — fixtures 100% sintéticas, geradas no próprio teste.
