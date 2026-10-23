# IDA Pro Reverse Elite MCP — DIGITAL BAROQUE v.6.6.6

![IDA Pro Reverse Elite MCP — DIGITAL BAROQUE v.6.6.6](xgyjkdytayiqr968ge98yn.png)

Dois motores de engenharia reversa vivem neste repositório, sem mistura.
O **MCP do IDA Pro** (labs 1–52) liga agentes de IA ao IDA para RE
assistida. O **DIGITAL BAROQUE** (labs 53–94) é o motor próprio
multi-formato, feito para superar o IDA em velocidade e autonomia.
Cada motor roda sozinho, com seus labs e suas provas.

## Motor 1 — RE assistida no IDA Pro (labs 1–52)

Você aponta uma funcionalidade que viu num aplicativo. O agente abre o
binário no IDA sem o código-fonte, traça procedimentos, lê pseudocódigo,
strings e referências cruzadas, e devolve os achados com evidências.
Depois, reconstrói a lógica no seu projeto.

Fases 1–9 do pipeline CLONAR — **analisar → entender → reconstruir**:

- **Fase 1 — Triagem estática (01–08):** hash, strings, inspeção do PE,
  entropia por seção, detecção de packer, inventário de imports, varredura
  de anomalias e relatório consolidado.
- **Fase 2 — Leitura no IDA (09–20):** xrefs, navegação por strings, filtro
  de bibliotecas, constantes simbólicas, anatomia de função, fluxo de
  controle, loops, jump tables, padrões de API, dataflow reverso, plano de
  anotação e nuances 64-bit.
- **Fase 3 — Unpacking (21–25):** caça ao OEP, validação de dump,
  reconstrução da IAT, ASLR desligado e comparativo empacotado × dump.
- **Fase 4 — Desobfuscação (26–30):** XOR brute-force, known-plaintext,
  stack strings, emulação de loops de decode e relatório.
- **Fase 5 — Injeção e hooking (31–34):** cadeia de injeção, trampoline de
  hook, process hollowing e mapa de técnicas por APIs.
- **Fase 6 — Ponte com memória (35–38):** regiões RWX suspeitas, prólogos
  patchados, geração de IDC e relatório.
- **Fase 7 — Bypass de defesas (39–42):** inventário anti-análise, plano de
  patches, TLS callbacks e relatório.
- **Fase 8 — Reconstrução (43–48):** especificação de comportamentos, elo
  evidência→função, ledger de obrigações, verificação de cobertura,
  diff original × clone e relatório final do pipeline.
- **Fase 9 — Geração do clone (49–52):** spec → esqueleto de código,
  templates de API, montagem do clone e verificação de paridade com
  veredito.

## Motor 2 — DIGITAL BAROQUE (labs 53–94)

RE multi-formato que não depende do IDA. Parsers nativos de ELF, Mach-O,
DEX e APK; internals de Windows, Linux e mobile; veredito de fidelidade
do clone. Agentes autônomos rodam o pipeline de ponta a ponta — o humano
aprova o veredito.

Fases 10–14:

- **Fase 10 — Formatos de binário (53–58):** parsers nativos ELF64,
  Mach-O universal com thinning, DEX, class-dump Obj-C, Swift demangle
  e inventário de capacidades.
- **Fase 11 — Windows por dentro (59–70):** cadeia de derivação DPAPI,
  CREDHIST, segredos LSA, inventário de tokens, snapshot e simulação
  WFP, privilégios de serviços, dialeto SMB, NGEN e relatório de
  credenciais.
- **Fase 12 — Linux por dentro (71–78):** oráculo strace+ENOENT,
  DT_NEEDED recursivo, jail chroot mínima, devices mknod, SELinux TE,
  loop audit2allow, truque do automounter e hierarquia DNSSEC.
- **Fase 13 — Mobile (79–90):** pipeline APK (decode→patch→sign→
  zipalign), desofuscação smali, diff de fidelidade Androsim,
  dumpdecrypted, hooks Frida, REPL Objection, detecção de híbridos,
  scoring estilo MobSF, swizzling e vazamentos de log.
- **Fase 14 — Veredito BAROQUE (91–94):** pipeline multi-formato,
  ledger de fidelidade, veredito `CLONADO 100%` multi-formato e
  benchmark agentes-vs-IDA.

Índice completo das 14 fases em `INDICE.md`.

## Provas

**604 testes verdes**, todos com fixtures sintéticas — nenhum binário real
no repositório. Para rodar os testes de um lab (do diretório do lab):

```bash
python3 -m unittest discover -p "*.py"
```

## Ponte com o IDA (Motor 1)

- **`mrg3ynauhl4c6qu1go4jqo/uqr3e1yy66r39mr5tt2a0e.py`** — script IDAPython: rode dentro do IDA
  (File > Script file) para exportar funções, xrefs, strings e imports no
  formato JSON que os labs consomem.
- **`9pd1ao2s9soicz7ndhxu9e/ni8imoj0zs33nddqo4cq01.py`** — orquestrador do pipeline completo:

```bash
python3 9pd1ao2s9soicz7ndhxu9e/ni8imoj0zs33nddqo4cq01.py alvo.exe --ida-export export.json -o saida/
```

## Prova ponta a ponta (Motor 1)

O `qdqv9uqkleschd0pn0600t/` constrói um alvo PE sintético do zero, executa o pipeline real,
gera o clone e verifica a paridade — cobertura **100%**, veredito
`CLONADO 100%`, com SHA-256 do alvo e do clone como prova:

```bash
python3 qdqv9uqkleschd0pn0600t/z71me9i2b581v1yejqq9v1.py
```

## Fluxo da skill (Motor 1)

1. **Roteia o alvo** — `open_binary` para binários nativos e pacotes
   (ZIP/APK/IPA/DMG, executáveis PyInstaller).
2. **Inspeciona** — procedimentos (`list_procedures`, `procedure_pseudo_code`),
   instruções (`inspect_native_instruction`), strings, xrefs, grafo de
   chamadas (`get_call_graph`).
3. **Traça a feature** — `trace_application_feature` liga o comportamento
   observado ao código responsável.
4. **Reconstrói** — `verify_reconstruction` e o ledger de obrigações medem a
   cobertura do clone contra o original.

Nada é executado: análise 100% estática, com evidências e limitações
declaradas em cada achado.

## Instalação

Com Node.js 22+ instalado:

```bash
npx rea-agents setup
```

Escolha os agentes, revise as mudanças propostas e aprove. O setup registra o
servidor MCP e as instruções de workflow. Reinicie o agente depois.

## Uso

```text
Abra o binário do app X no IDA, entenda como o login funciona,
me mostre as evidências e reconstrua a lógica no meu projeto.
```

## Requisitos

- Node.js 22.23.4+, 24.22.1+ ou 26.12.1+
- IDA Pro 8.3 como engine de análise nativa (Motor 1)

## Licença

MIT — Copyright (c) 2026 A Elite Estrangeira. Veja `LICENSE`.
