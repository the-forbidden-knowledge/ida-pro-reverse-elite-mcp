# pipeline — orquestrador CLONAR

Executa o pipeline completo de clonagem ponta a ponta sobre um alvo,
chamando os labs via `importlib`. Cada etapa que falha vira
`{"erro": ...}` sem derrubar o resto.

## Uso

```bash
# só triagem + desobfuscação + injeção + bypass + reconstrução
python3 9pd1ao2s9soicz7ndhxu9e/ni8imoj0zs33nddqo4cq01.py /caminho/do/alvo.exe -o saida/

# pipeline completo, com leitura do export do IDA
python3 9pd1ao2s9soicz7ndhxu9e/ni8imoj0zs33nddqo4cq01.py /caminho/do/alvo.exe \
    --ida-export alvo-ida-export.json -o saida/
```

O JSON do `--ida-export` é gerado por `../mrg3ynauhl4c6qu1go4jqo/uqr3e1yy66r39mr5tt2a0e.py`
rodando **dentro do IDA Pro** (File > Script file...).

## Etapas

1. **triagem** — labs 01–08 sobre o arquivo
2. **leitura** — labs 09–20 sobre o export do IDA (labs que precisam de
   texto de disassembly são marcados com erro explicativo, pois o export
   JSON não o inclui)
3. **desobfuscacao** — labs 26–29 · **injecao** — labs 31–34 ·
   **bypass** — labs 39–41
4. **reconstrucao** — labs 43–46: comportamentos derivados dos achados →
   spec → mapa de evidências → ledger → cobertura
5. **relatorio** — lab 48: `relatorio.json` + `relatorio.md`

## Saída

```
saida/
  triagem.json  leitura.json  desobfuscacao.json  injecao.json
  bypass.json   reconstrucao.json
  relatorio.json  relatorio.md
```

## Testes

```bash
cd pipeline && python3 -m unittest discover
```

Fixtures 100% sintéticas (PE32 mínimo montado byte a byte + export JSON
sintético); nenhum binário real.
