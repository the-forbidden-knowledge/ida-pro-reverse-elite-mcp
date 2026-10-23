# q2qasb3270wv09m270atgb — Detecção de padrões de intenção por APIs

## O que faz

Detecta intenções típicas de análise (persistência, injeção, comunicação de
rede, escrita de arquivo, anti-análise, criptografia) a partir de uma lista de
nomes de APIs importadas por uma função ou programa. A tabela de padrões é
embutida no `x7zvgqybn3g6ytmtg801l1.py` e não cita nenhuma fonte externa.

## Entrada

Arquivo JSON:

```json
{
  "apis": ["OpenProcess", "VirtualAllocEx", "WriteProcessMemory",
           "CreateRemoteThread", "CloseHandle"]
}
```

## Saída

JSON com os grupos cujas APIs aparecem na entrada (comparação insensível a
caixa; o grupo inteiro precisa estar presente):

```json
{
  "patterns": [
    {
      "apis": ["OpenProcess", "VirtualAllocEx", "WriteProcessMemory",
               "CreateRemoteThread"],
      "intent": "injecao-processo"
    }
  ]
}
```

## Exemplo de uso

```bash
python3 x7zvgqybn3g6ytmtg801l1.py entrada.json
python3 -m unittest discover   # executa a suíte de testes
```
