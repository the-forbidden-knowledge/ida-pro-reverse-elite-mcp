# Prova de clonagem 100% — demo ponta a ponta

Esta pasta contém a **prova executável** de que o pipeline CLONAR do
repositório funciona de verdade: um alvo sintético é construído, analisado,
desofuscado e reconstruído — e o clone gerado cobre 100% dos comportamentos.

## Arquivos

- `kjql4h3qm9l4qlof5o08mz.py` — constrói `target_synth.exe`: um PE 32-bit mínimo e
  válido (2 seções, uma de alta entropia simulando packing), com tabela de
  imports (`kernel32.dll`: CreateFileA, ReadFile, WriteFile; `advapi32.dll`:
  RegSetValueExA) e 3 strings ofuscadas com XOR de 1 byte. Gera também
  `target_spec.json` com o comportamento esperado.
- `z71me9i2b581v1yejqq9v1.py` — executa o pipeline real importando os labs via importlib:
  triagem (01–08) → desobfuscação (26–27) → detecção (31, 34, 39) →
  reconstrução (43–52) → diff (47) → relatório (48). Gera
  `gk6g9tpaa4540ycewbkqgj.py` e imprime SHA-256 do alvo, SHA-256 do clone,
  % de cobertura e o veredito.
- `f8knpa86259mdz03uvi26f.py` — unittest ponta a ponta: afirma cobertura == 100% e
  strings recuperadas == esperadas.

## Como rodar

```bash
python3 kjql4h3qm9l4qlof5o08mz.py   # constrói o alvo sintético
python3 z71me9i2b581v1yejqq9v1.py       # executa o pipeline (veredito no final)
python3 -m unittest discover  # teste ponta a ponta
```

## O que a prova demonstra

1. **Triagem honesta**: o alvo é detectado como empacotado (seção de alta
   entropia), os 4 imports são inventariados, nenhuma injeção é
   falsamente acusada.
2. **Desobfuscação real**: a chave XOR é descoberta por known-plaintext e
   as 3 strings são recuperadas sem conhecer o alvo de antemão.
3. **Reconstrução completa**: cada comportamento vira especificação,
   evidência, obrigação no ledger e função no clone — 100% de cobertura,
   zero divergências, veredito `CLONADO 100%`.

Nenhum binário real é usado: o alvo é 100% sintético, gerado por
`kjql4h3qm9l4qlof5o08mz.py`.
