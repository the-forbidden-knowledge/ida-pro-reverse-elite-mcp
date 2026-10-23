# maoiosdj9n2pjh2troi74w

Brute-force de XOR de 1 byte: testa as 256 chaves possíveis e ranqueia cada
decodificação pela legibilidade (distribuição de caracteres do inglês).

## O que faz

- Lê o arquivo binário e aplica XOR com cada chave de `0x00` a `0xFF`
- Pontua: espaço e letras somam, bytes não-imprimíveis penalizam
- Devolve o ranking das melhores chaves com preview do texto decodificado

## Entrada

Arquivo binário qualquer.

## Saída

JSON com `results` (chave, chave em hex, score, preview) e `best_key`.

## Exemplo

```bash
python3 tdszw6xy7o8ndrx31j4vjw.py suspeito.bin
python3 tdszw6xy7o8ndrx31j4vjw.py suspeito.bin --top 10 --preview 200 -o chaves.json
```
