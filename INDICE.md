# Índice de técnicas — ida-pro-reverse-elite-mcp

94 labs em 14 fases do pipeline CLONAR: **analisar o binário → entender a
funcionalidade → reconstruir com evidências**. Direcionado ao IDA Pro como
engine de análise nativa.

## Fase 1 — Triagem estática (labs 01–08)

| Lab | Pasta | Técnica |
|---|---|
| 01 | `ly7lehw1klh1ybr0qdsbbo` | `hash-identify` — impressão digital do arquivo (MD5/SHA-1/SHA-256) |
| 02 | `7ked3ij8phcpj8mdhknxym` | `strings-extract` — strings ASCII e UTF-16LE com offsets |
| 03 | `2td8yubqfjfean1yisy81e` | `pe-inspect` — cabeçalho PE e seções via parse binário |
| 04 | `d5sh7wnlyknzrdtv7goyda` | `entropy-scan` — entropia de Shannon por seção |
| 05 | `silikcwt7gnqmkmb6tcpna` | `packer-detect` — heurísticas de empacotamento |
| 06 | `imrsjemoufqnlwrym6ahop` | `import-inventory` — tabela de imports como mapa de capacidades |
| 07 | `asw8hn5kubic4ry5i9xgls` | `anomaly-scan` — constantes de cripto/compressão embutidas |
| 08 | `3qq3zegqt0tshdhx3r8c5x` | `triage-report` — relatório consolidado de triagem |

## Fase 2 — Leitura no IDA (labs 09–20)

| Lab | Pasta | Técnica |
|---|---|
| 09 | `9d0trqr4ktimjrds7goieb` | `xref-trace` — da API ao código: cadeia de chamadores |
| 10 | `xma5iz9yl37z2m496hj3d7` | `strings-navigate` — string → função que a usa |
| 11 | `icqliognasbghpdwlaq0u7` | `library-filter` — separar código do autor de código de biblioteca |
| 12 | `t87xkpvnhcvf29870buqso` | `symbolic-constants` — números mágicos → constantes nomeadas |
| 13 | `ek9h3ofp5ycv8o362sr889` | `function-anatomy` — prólogo/epílogo, args, locais, convenção |
| 14 | `32b05wtz4ddq3mdlrh2e5v` | `control-flow` — if/else, loop, switch no disassembly |
| 15 | `j01gg0kgnpmnuc33134uhy` | `loop-deconstruct` — as 4 partes de um loop |
| 16 | `3q09u6xwsb2isw11q6gw0m` | `jumptable-resolve` — tabela de salto → cases |
| 17 | `q2qasb3270wv09m270atgb` | `api-patterns` — grupos de APIs → intenção do código |
| 18 | `u52ahn6smk2ewnh0uax885` | `dataflow-trace` — rastreamento reverso até a origem do dado |
| 19 | `nlpdgtlczg6wtde0pjd1l6` | `annotate-plan` — plano de renomeação/comentários → script IDC |
| 20 | `6w3vl9pthguka2b3jso8ee` | `x64-adapt` — nuances 64-bit (convenção, RIP-relativo) |

## Fase 3 — Unpacking (labs 21–25)

| Lab | Pasta | Técnica |
|---|---|
| 21 | `lsx3gfiglpsup1b8b3fkow` | `oep-hunt` — checklist de validade do dump no OEP |
| 22 | `44xatb29o7po8kzbub0sm5` | `dump-validate` — dump de memória é um PE válido? |
| 23 | `xmryk9bdyo3jrqjcqa174v` | `iat-rebuild` — reconstrução da tabela de imports + IDC |
| 24 | `k8ezfosqm9w3wukcsasoyc` | `aslr-strip` — desliga ASLR para endereços estáveis |
| 25 | `k1zlgokezxoi94chw88qpu` | `unpack-compare` — empacotado × dump: veredito de unpacking |

## Fase  4 — Desobfuscação (labs 26–30)

| Lab | Pasta | Técnica |
|---|---|
| 26 | `maoiosdj9n2pjh2troi74w` | `xorsearch` — brute-force XOR de 1 byte com ranking |
| 27 | `5fmv8fp8wxqb3id6swfzdb` | `xor-key-recover` — known-plaintext: deriva a chave |
| 28 | `r0zx4dq741d2qo17exc2dm` | `stackstring-decode` — strings montadas na stack |
| 29 | `ho34my4hrz5m5a5kipq3k1` | `decode-emulate` — emula loops de decode (XOR/ADD/SUB/ROL/ROR) |
| 30 | `ylh1syqcjv1o9sdk0hxsj6` | `deobf-report` — relatório consolidado de desobfuscação |

## Fase 5 — Injeção e hooking (labs 31–34)

| Lab | Pasta | Técnica |
|---|---|
| 31 | `me3cvyro1kttvtrzo267a9` | `injection-chain` — cadeia de injeção de código |
| 32 | `lpoeo3swubbrqw122jmi2c` | `hook-trampoline` — padrão de inline hook |
| 33 | `qp4ap4yltvkxhk5r3qrb0c` | `hollowing-detect` — process hollowing |
| 34 | `znx6lo74isdipwpe3dqter` | `technique-map` — APIs → classificação da técnica |

## Fase 6 — Ponte com memória (labs 35–38)

| Lab | Pasta | Técnica |
|---|---|
| 35 | `vmnu7l4sv08o5mr6lmevlp` | `rwx-scan` — regiões executáveis suspeitas (código injetado) |
| 36 | `qospd4bifqjqxx3j6zos0g` | `prologue-scan` — prólogos patchados (hooks) |
| 37 | `19ns8q36n70mjwbq6j8dkd` | `idc-generate` — mapa endereço→API vira script IDC |
| 38 | `j44198zmeokrhd19myrnh8` | `memory-report` — relatório consolidado de memória |

## Fase 7 — Bypass de defesas (labs 39–42)

| Lab | Pasta | Técnica |
|---|---|
| 39 | `pft8rdap8iblilku7ni0y8` | `antidebug-inventory` — inventário de defesas anti-análise |
| 40 | `r7vkuk0bo7khhekzv7to9p` | `patch-plan` — plano de neutralização de cada defesa |
| 41 | `ugqtqasgy279l2p5axv4is` | `tls-parse` — callbacks TLS do PE |
| 42 | `atww5zomvexic1pxsksaog` | `defense-report` — relatório consolidado de defesas |

## Fase 8 — Reconstrução (labs 43–48)

| Lab | Pasta | Técnica |
|---|---|
| 43 | `d9yen9lqdjkquwp3jjyxep` | `behavior-spec` — comportamentos → especificação estruturada |
| 44 | `8umwx2402lcttqswbkb3mh` | `evidence-link` — comportamento → evidência → função |
| 45 | `ga07t5mx7v0op0qahwb3uc` | `obligation-ledger` — ledger de obrigações de reconstrução |
| 46 | `m49dd353e4mwmhzhwd1xcp` | `coverage-verify` — % de cobertura do clone + gaps |
| 47 | `kx003aek4jq1hylyv1vmrk` | `behavior-diff` — original × clone: divergências |
| 48 | `krsi0v4p4a8251u4z853pm` | `pipeline-report` — relatório final do pipeline CLONAR |

## Fase 9 — Geração do clone (labs 49–52)

| Lab | Pasta | Técnica |
|---|---|
| 49 | `b96wflm5hthke922duw85d` | `spec-to-skeleton` — spec → esqueleto de código do clone |
| 50 | `gtbs546sxv6oa5wmwazir3` | `api-map-emit` — evidências → templates de chamadas de API |
| 51 | `l202ggwamxjl1aino9wsm2` | `clone-assemble` — monta o projeto do clone |
| 52 | `m1pe06om9yrrhat1gi41pp` | `clone-verify` — paridade original × clone + veredito |

## Ponte com o IDA e pipeline

- **`mrg3ynauhl4c6qu1go4jqo/uqr3e1yy66r39mr5tt2a0e.py`** — script IDAPython (roda dentro do IDA:
  File > Script file) que exporta funções, xrefs, strings e imports no JSON
  que os labs consomem.
- **`9pd1ao2s9soicz7ndhxu9e/ni8imoj0zs33nddqo4cq01.py`** — orquestrador: triagem → leitura do
  export do IDA → desobfuscação → detecção → reconstrução → relatório final,
  num comando só.
- **`qdqv9uqkleschd0pn0600t/`** — prova ponta a ponta: alvo PE sintético construído do zero,
  pipeline real executado, clone gerado e verificado (**cobertura 100%**,
  veredito `CLONADO 100%`, com SHA-256 do alvo e do clone).

## Divergências declaradas

- **lab 11** implementa um filtro heurístico de código de biblioteca; não
  reproduz assinaturas proprietárias de identificação de bibliotecas.
- **lab 29** emula loops simples de decode (XOR/ADD/SUB/ROL/ROR) descritos em
  mini-DSL; não é um emulador completo de binário.
- Ferramentas externas (debugger, Scylla, Volatility, FLOSS) **não** estão
  embutidas: os labs validam dumps, geram planos e scripts para essas
  ferramentas, mas não as executam.
- O script `mrg3ynauhl4c6qu1go4jqo/uqr3e1yy66r39mr5tt2a0e.py` só executa dentro do IDA Pro
  (IDAPython); aqui ele é validado por compilação, não por execução.
- O `qdqv9uqkleschd0pn0600t/` usa um alvo PE 100% sintético construído pelo próprio demo;
  nenhum binário real acompanha o repositório.
- Todos os testes usam fixtures sintéticas geradas no próprio teste.
- Nenhum lab executa código de terceiros: análise 100% estática sobre
  artefatos fornecidos pelo operador.

## Fase 10 — Formatos de binário (labs 53–58)

| Lab | Pasta | Técnica |
|---|---|
| 53 | `e1nf6idkidpszk6j8ged6a` | `elf-parse` — cabeçalho ELF64 + program/section headers via struct |
| 54 | `wx9s0rp1raviau549xf7d3` | `macho-fat` — parse Mach-O universal (0xcafebabe) + thinning por cputype |
| 55 | `lsjpj02vdypbvpzen5d9go` | `dex-header` — magic, adler32, SHA-1, string/type_ids do DEX |
| 56 | `3kv8gxblk9un55vjeoyjcr` | `class-dump` — classes/métodos Obj-C → headers .h |
| 57 | `zmut80zxc7sdf8on8pq1xs` | `swift-demangle` — _TtC4Nome6Classe → Nome.Classe |
| 58 | `1ekzyarczii14rrygfbo4d` | `capability-inventory` — frameworks/APIs linkadas → capacidades |


## Fase 11 — Windows por dentro (labs 59–70)

| Lab | Pasta | Técnica |
|---|---|
| 59 | `2r8yxcvyixe6ul30ithowu` | `dpapi-derive` — cadeia PBKDF2-SHA-512/5600 → Master Key → Session Key |
| 60 | `m2gyl7g6u1cowh8j0vhyuv` | `credhist-unwind` — cadeia SHA-512 de senhas antigas até hash arquivado |
| 61 | `89225yzgt4gszurgghkr2s` | `lsa-secrets` — parse de hive simulado; segredos _SC_<nome> com redação |
| 62 | `cja2tv24022ixy8gro983l` | `token-inventory` — privilégios por token + score de exposição |
| 63 | `g9qah2t25v4o2og6tft3v0` | `wfp-snapshot` — snapshot dos 4 policy stores incl. ocultos |
| 64 | `v76v9fh4oqerp54yktfpe4` | `wfp-simulate` — simulador das 5 camadas, best-match-wins |
| 65 | `7snac5392qftt7ur0mgcfo` | `service-privs` — privilégios por serviço + diff contra baseline |
| 66 | `uossrzx4co59x36ax26q03` | `smb-dialect` — negociação de dialeto + detecção de downgrade |
| 67 | `kysf5qt0fmtflzkpu9uh4z` | `ngen-detect` — .ni.dll (NGEN nativo) vs IL |
| 68 | `hllubl8w5jr63y0z3of3nr` | `dpapi-system` — Master Key de máquina via segredo DPAPI_SYSTEM |
| 69 | `3qy2nrsv1dydbv8kd3wcbk` | `firewall-ids` — Event IDs WFP 5156/5158/5157/5159/5152/5153 → grafo |
| 70 | `iyff6o6zq0f6h7ykp4oxfs` | `credguard-report` — consolidado dos labs 59–63, 65, 68 com redação |


## Fase 12 — Linux por dentro (labs 71–78)

| Lab | Pasta | Técnica |
|---|---|
| 71 | `8r6wuschpsym4nltq0d2rv` | `strace-oracle` — parse de strace; último ENOENT fatal → dependências |
| 72 | `m5oztl382pfyc674lkxtpn` | `dt-needed-recursive` — DT_NEEDED em cascata + ocultas de runtime |
| 73 | `qpid535clfjhw0skt9q1h7` | `chroot-jail` — jail mínima 111/555/444, shadow banido |
| 74 | `2gdo7b4zv4h2uwyikw8ekr` | `mknod-devices` — parse major/minor, plano mknod |
| 75 | `zi6q49fqavvblwigii3ft3` | `selinux-te` — contextos u:r:t:s0, matriz allow, transições |
| 76 | `y21ekrd62svzlzuq4238l4` | `audit2allow-loop` — AVC → allow crua → clusters em macros |
| 77 | `i4o9flsvqwrkbyfxizkga7` | `automount-trick` — wildcard + bind mounts + macro & |
| 78 | `2zcup3oim4cmu2t7i1qezg` | `dnssec-hierarchy` — ZSK/KSK, rollover curr→old/next→curr, atestação |


## Fase 13 — Mobile (labs 79–90)

| Lab | Pasta | Técnica |
|---|---|
| 79 | `kiuar0cmi7rc41ec1foz6a` | `apk-pipeline` — decode→patch→build→sign→zipalign (ordem certa) |
| 80 | `eetqxqiprc53gmardwkvq2` | `smali-deobfuscate` — ProGuard/R8 → nomes legíveis por assinatura |
| 81 | `f77vby2689d573mg79gi1b` | `simplify-deadcode` — poda de código morto em grafo de chamadas |
| 82 | `ju40j8t6usy3cdhz3vh2z0` | `androsim-diff` — diff método-a-método + fidelity score do clone |
| 83 | `ezeylwmvldwqp92hqyccji` | `dumpdecrypted` — despejo de Mach-O (cryptid→0, região __TEXT) |
| 84 | `lbju9j64iigan84ol1gxrm` | `frida-hooks` — gera script Java.use + implementation com overload |
| 85 | `sc42np56i7vmgvj4vh1h1z` | `objection-repl` — android hooking watch / memory list modules simulados |
| 86 | `et9v2fpd4wh1mjuoivh4u3` | `hybrid-detect` — PhoneGap (cordova.js) / Xamarin (assemblies/*.dll) |
| 87 | `yuwx86mngxtami4r35s8ib` | `mobsf-score` — scoring por permissões, exportados e APIs arriscadas |
| 88 | `qon2vsvds6sbx3sp7zg14o` | `method-swizzle` — troca de implementações na tabela Obj-C |
| 89 | `hgfb348r861ipum52523m6` | `log-leak` — Log.d/e/i/w/v() com const-strings pós-ofuscação |
| 90 | `98z6anxw83knyqosc8nn6r` | `mobile-report` — relatório consolidado da fase mobile |


## Fase 14 — Veredito BAROQUE (labs 91–94)

| Lab | Pasta | Técnica |
|---|---|
| 91 | `9lr2qv30k9bx88h96uohlj` | `multiformat-pipeline` — PE+ELF+Mach-O+DEX num pipeline único |
| 92 | `92uhnlf65oq9mb3vh73sx4` | `fidelity-ledger` — Androsim-diff + ledger de fidelidade por formato |
| 93 | `imc6v78wkhvdzc0vfovvvw` | `baroque-verdict` — veredito CLONADO 100% multi-formato + SHAs |
| 94 | `9q2bb092thb07we1x06o7t` | `anti-ida-benchmark` — benchmark agentes-vs-IDA (simulado, honesto) |
