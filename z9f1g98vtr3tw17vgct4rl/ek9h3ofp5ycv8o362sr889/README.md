# Lab 13 — function-anatomy

Análise estática de uma função a partir de texto de disassembly: identifica
prólogo/epílogo, conta argumentos e variáveis locais e infere a convenção
de chamada.

## O que faz

Lê um arquivo de texto com disassembly (uma instrução por linha, com ou sem
prefixo de endereço/bytes) e devolve:

- `prologue`: `true` se houver `push ebp`/`push rbp` seguido de
  `mov ebp, esp` / `mov rbp, rsp`;
- `epilogue`: `true` se houver `leave`, `ret`/`retn`/`retf` ou a sequência
  `mov esp, ebp` + `pop ebp` + `ret`;
- `args`: nº de argumentos distintos (`arg_0`, `arg_4`, ...);
- `locals`: nº de variáveis locais distintas (`var_4`, `var_8`, ...);
- `convention`: `stdcall` se a função limpa a pilha (`ret N`);
  `cdecl` se o chamador limpa (`add esp, N`) ou o retorno é simples;
  `unknown` caso contrário.

## Entrada

Arquivo `.asm`/`.txt` com o disassembly. Aceita linhas com endereço
(`00401000 55 push ebp`), só mnemônicos (`push ebp`) e comentários `;`.

## Saída

JSON na stdout, ex.:

```json
{
  "prologue": true,
  "epilogue": true,
  "args": 2,
  "locals": 2,
  "convention": "stdcall"
}
```

## Exemplo de uso

```bash
python3 c50srswv6gq3514hwui0rb.py exemplo.asm
python3 -m unittest discover   # 8 testes
```

## Testes

`ex04fk3nmo3dszz5ae5j2m.py` — fixtures 100% sintéticas, geradas no próprio
teste (nenhum binário real).
