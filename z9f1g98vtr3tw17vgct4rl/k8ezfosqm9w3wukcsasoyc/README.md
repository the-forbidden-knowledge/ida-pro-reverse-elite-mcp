# aslr-strip — remoção da relocação de base (ASLR)

Zera a flag `IMAGE_DLLCHARACTERISTICS_DYNAMIC_BASE` (0x0040) no campo
`DllCharacteristics` do optional header de um PE, fixando a imagem na
`ImageBase` declarada. A edição é in-place via `struct`, e um backup
`<arquivo>.bak` é criado antes de qualquer escrita.

## O que faz

1. Localiza o campo `DllCharacteristics` (PE32 e PE32+).
2. Cria o backup `<arquivo>.bak` (cópia byte a byte).
3. Se a flag `0x0040` estiver ligada, zera só ela — as demais flags são
   preservadas.

## Entrada

Um arquivo PE:

```bash
python3 2uoj8fwax14wq7qft5frg5.py programa.exe
```

## Saída

JSON:

```json
{
  "patched": true,
  "backup": "programa.exe.bak"
}
```

`patched` é `true` apenas quando a flag estava ligada e foi zerada. Se o
arquivo não for um PE válido, imprime `{"patched": false, "backup": "",
"error": "..."}` e sai com código 1.

## Exemplo de uso

```bash
python3 2uoj8fwax14wq7qft5frg5.py /tmp/alvo.exe
# backup em /tmp/alvo.exe.bak; DllCharacteristics sem o bit 0x0040
```

## Testes

```bash
python3 -m unittest discover
```
