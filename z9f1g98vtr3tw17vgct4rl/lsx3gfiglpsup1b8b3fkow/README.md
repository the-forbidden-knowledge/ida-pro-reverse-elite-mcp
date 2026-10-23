# oep-hunt — caça ao entry point em dump

Valida se um dump/arquivo é um executável PE íntegro e avalia dois sinais
clássicos de dump malformado ou ainda empacotado: o entry point fora de
seção executável e o diretório de imports apontando para fora do arquivo.

## O que faz

1. Verifica o magic `MZ` e a assinatura `PE\0\0`.
2. Lê `AddressOfEntryPoint` e as seções do cabeçalho.
3. Checa se o entry point cai dentro de uma seção com flag de execução
   (`IMAGE_SCN_MEM_EXECUTE`).
4. Checa se o DataDirectory de imports aponta para dentro do arquivo.

## Entrada

Um arquivo (dump de memória ou binário):

```bash
python3 h38d8gegsebkljy66flja7.py dump.bin
```

## Saída

Checklist em JSON:

```json
{
  "valid_pe": true,
  "ep_in_exec_section": true,
  "imports_readable": true,
  "checks": [
    {"check": "magic_mz", "ok": true, "detail": "assinatura 'MZ' presente"},
    {"check": "assinatura_pe", "ok": true, "detail": "'PE\\0\\0' presente"},
    {"check": "entry_point_em_secao_executavel", "ok": true, "detail": "..."},
    {"check": "diretorio_de_imports_legivel", "ok": true, "detail": "..."}
  ]
}
```

Se os cabeçalhos forem inválidos, `valid_pe` é `false` e as demais chaves
também, com o motivo em `checks`.

## Exemplo de uso

```bash
python3 h38d8gegsebkljy66flja7.py /tmp/amostra.dump
python3 h38d8gegsebkljy66flja7.py programa.exe | python3 -m json.tool
```

## Testes

```bash
python3 -m unittest discover
```
