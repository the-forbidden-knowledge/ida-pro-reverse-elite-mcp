# dump-validate — validação estrutural de dump PE

Verifica se um dump/arquivo respeita a estrutura esperada de um executável
PE: assinaturas, alinhamento das seções e coerência do entry point. Útil
para separar dumps íntegros de dumps corrompidos ou ainda empacotados.

## O que faz

1. Checa o magic `MZ` e a assinatura `PE\0\0`.
2. Para cada seção, checa:
   - `VirtualAddress` múltiplo de `SectionAlignment`;
   - `SizeOfRawData` múltiplo de `FileAlignment`;
   - `PointerToRawData` múltiplo de `FileAlignment`;
   - dados crus dentro dos limites do arquivo.
3. Checa se o `AddressOfEntryPoint` cai dentro de alguma seção.

## Entrada

Um arquivo (dump de memória ou binário):

```bash
python3 033jydbq9nrdlq8wn8eu9q.py dump.bin
```

## Saída

JSON com o veredito e a lista de problemas:

```json
{
  "ok": false,
  "issues": [
    "secao '.text': VirtualAddress 0x1001 nao e multiplo de SectionAlignment 0x1000",
    "entry point 0x9000 fora de todas as secoes"
  ]
}
```

`ok` é `true` somente quando `issues` está vazia.

## Exemplo de uso

```bash
python3 033jydbq9nrdlq8wn8eu9q.py /tmp/amostra.dump
python3 033jydbq9nrdlq8wn8eu9q.py programa.exe | python3 -c "import json,sys; print(json.load(sys.stdin)['ok'])"
```

## Testes

```bash
python3 -m unittest discover
```
