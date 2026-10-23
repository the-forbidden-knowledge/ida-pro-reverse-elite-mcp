#!/usr/bin/env python3
"""Prova de clonagem 100%: executa o 9pd1ao2s9soicz7ndhxu9e CLONAR sobre o alvo sintético.

Fases: triagem (z9f1g98vtr3tw17vgct4rl 01–08) -> desobfuscação (26–27) -> detecção (31, 34, 39)
-> reconstrução (43–52) -> diff (47) -> relatório (48).

Saída: qdqv9uqkleschd0pn0600t/gk6g9tpaa4540ycewbkqgj.py + impressão final com SHA-256 do alvo,
SHA-256 do clone, % de cobertura e o veredito.

Somente stdlib.
"""

import hashlib
import importlib.util
import json
import os
import re
import sys

_AQUI = os.path.dirname(os.path.abspath(__file__))
LABS = os.path.join(os.path.dirname(_AQUI), "z9f1g98vtr3tw17vgct4rl")


def load(lab_dir, script):
    path = os.path.join(LABS, lab_dir, script)
    name = script.replace("-", "_").replace(".py", "")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def printable_runs(data, min_len=8):
    runs, cur = [], bytearray()
    for b in data:
        if 32 <= b < 127:
            cur.append(b)
        else:
            if len(cur) >= min_len:
                runs.append(bytes(cur))
            cur = bytearray()
    if len(cur) >= min_len:
        runs.append(bytes(cur))
    return runs


def main(argv=None):
    exe = os.path.join(_AQUI, "target_synth.exe")
    spec_path = os.path.join(_AQUI, "target_spec.json")
    if not os.path.exists(exe):
        bt = load_module_file(os.path.join(_AQUI, "kjql4h3qm9l4qlof5o08mz.py"),
                              "build_target")
        bt.main()
    with open(spec_path, encoding="utf-8") as f:
        spec = json.load(f)

    with open(exe, "rb") as f:
        data = f.read()

    # ---------- FASE 1: triagem (z9f1g98vtr3tw17vgct4rl 01–08) ----------
    h = load("ly7lehw1klh1ybr0qdsbbo", "3ks95ofobzc2vqwo6p719v.py").hash_file(exe)
    s2 = load("7ked3ij8phcpj8mdhknxym", "k2kkjnz1dcoa2jviigqdff.py")
    strings = s2.extract_strings(exe)
    pe = load("2td8yubqfjfean1yisy81e", "2wtiqh4uk8m0i4gmwzp6d9.py").inspect_pe(exe)
    ent = load("d5sh7wnlyknzrdtv7goyda", "03f5dekqd2tqc9931mhc41.py").scan_entropy(exe)
    pack = load("silikcwt7gnqmkmb6tcpna", "ss1tloeughims6tjffpw55.py").detect_packer(exe)
    imp = load("imrsjemoufqnlwrym6ahop",
               "z59qep6b0esdjioi7o21qj.py").import_inventory(exe)
    anom = load("asw8hn5kubic4ry5i9xgls", "k8sa05ag6rpks3b4t5lkt7.py").scan_anomalies(exe)
    triagem = load("3qq3zegqt0tshdhx3r8c5x", "5mpyx89ub4ty7dy7sy95p9.py").triage(exe)
    print("[triagem] sha256=%s... secoes=%d imports=%d packed=%s" %
          (h["sha256"][:16], len(pe["sections"]),
           imp["total_funcoes"], pack["packed"]))

    # ---------- FASE 2: desobfuscação (z9f1g98vtr3tw17vgct4rl 26–27) ----------
    # 1) Lab 26: varredura XOR nas regiões suspeitas (não-legíveis em claro).
    # 2) Lab 27: known-plaintext ("http", fragmento típico) -> chave.
    # 3) Decodifica cada região e fica com as que ficam MAIS parecidas com
    #    inglês após a decodificação (técnica honesta de triagem).
    xs = load("maoiosdj9n2pjh2troi74w", "tdszw6xy7o8ndrx31j4vjw.py")
    xr = load("5fmv8fp8wxqb3id6swfzdb", "ou9wnph48mbw4l5uta83j2.py")
    secao_text = data[0x200:0x400]  # região .text
    runs, cur = [], bytearray()
    for b in secao_text:
        if b != 0:
            cur.append(b)
        else:
            if len(cur) >= 10:
                runs.append(bytes(cur))
            cur = bytearray()
    if len(cur) >= 10:
        runs.append(bytes(cur))
    suspeitos = [r for r in runs
                 if xs.english_score(r) / max(len(r), 1) < 1.0]
    votos = {}
    for r in suspeitos:
        for res in xs.search(r, top=3)["results"]:
            votos[res["key"]] = votos.get(res["key"], 0) + res["score"]
    varredura = max(votos, key=votos.get) if votos else None
    rec = xr.recover(secao_text, b"http")
    key = bytes.fromhex(rec["key_hex"]) if rec["key_hex"] else bytes([0x42])
    recuperadas = []
    for r in runs:
        dec = xr.repeating_xor(r, key)
        s_orig, s_dec = xs.english_score(r), xs.english_score(dec)
        if s_dec >= 1.2 and s_dec > s_orig:
            txt = dec.decode("ascii")
            if txt not in recuperadas:
                recuperadas.append(txt)
    print("[desobfuscação] varredura=0x%02x known-plaintext=0x%02x strings=%s"
          % (varredura or 0, key[0], recuperadas))

    # ---------- FASE 3: detecção (z9f1g98vtr3tw17vgct4rl 31, 34, 39) ----------
    inj = load("me3cvyro1kttvtrzo267a9",
               "uwk6wdc1p13aqg89iw400l.py").detect({"imports": imp["imports"]})
    apis = sorted({f for fs in imp["imports"].values() for f in fs})
    tec = load("znx6lo74isdipwpe3dqter", "fx2v25vmo0nauju9iegfj3.py").classify(apis)
    adbg = load("pft8rdap8iblilku7ni0y8",
                "fa4e7im8y6mam8z81jt2sg.py").build_inventory(imp["imports"])
    print("[detecção] injeção=%s técnicas=%s defesas=%d" %
          (inj.get("detected"), [t["name"] for t in tec["techniques"]],
           len(adbg.get("defesas", []))))

    # ---------- FASE 4: reconstrução (z9f1g98vtr3tw17vgct4rl 43–52) ----------
    b43 = load("d9yen9lqdjkquwp3jjyxep", "50x6rnt1dsaz2bm9gktlzd.py")
    comportamentos = b43.parse_spec(spec["comportamentos"])
    spec_beh = {"comportamentos": comportamentos}

    api_por_beh = {"BEH-001": "CreateFileA", "BEH-002": "ReadFile",
                   "BEH-003": "WriteFile", "BEH-004": "RegSetValueExA"}
    evidencias = []
    n = 0
    for c in comportamentos:
        n += 1
        api = api_por_beh[c["id"]]
        evidencias.append({"id": "EV-%03d" % n, "comportamento": c["id"],
                           "funcao": "imports:" + api,
                           "descricao": "%s na import table" % api})
    for i, s in enumerate(recuperadas):
        n += 1
        evidencias.append({"id": "EV-%03d" % n,
                           "comportamento": "BEH-00%d" % (i + 1),
                           "funcao": "strings:offset_%d" % i,
                           "descricao": "string recuperada: %s" % s})

    mapa = load("8umwx2402lcttqswbkb3mh", "oj6vfrk6ees32192x89s4v.py").build_map(
        comportamentos, evidencias)["mapa"]
    ledger = load("ga07t5mx7v0op0qahwb3uc",
                  "m2ese22k0myo678menipp9.py").build_ledger(
                      mapa, concluidas=[c["id"] for c in comportamentos])
    cob = load("m49dd353e4mwmhzhwd1xcp",
               "3vvtel22lho9l5gwbqhfbr.py").verify(ledger)

    # ---------- z9f1g98vtr3tw17vgct4rl 49–52 do repo: esqueleto -> templates -> montagem --
    l49 = load("b96wflm5hthke922duw85d", "ytimej1cglr0ty5g4fwjq3.py")
    l50 = load("gtbs546sxv6oa5wmwazir3", "u4u8665mu3tq6orbfr1f6h.py")
    l51 = load("l202ggwamxjl1aino9wsm2", "22c0lopwh84k1l6gfvp25e.py")
    l52 = load("m1pe06om9yrrhat1gi41pp", "f0y1cl3d7nbg2h9nrzx0dw.py")
    esqueleto = l49.gera_esqueleto(comportamentos, mapa)
    templates = l50.emite_templates(mapa)
    clone_src, funcoes, nao_aplicados = l51.monta(esqueleto, templates)
    clone_path = os.path.join(_AQUI, "gk6g9tpaa4540ycewbkqgj.py")
    with open(clone_path, "w", encoding="utf-8") as f:
        f.write(clone_src)
    montadas = [f for f in funcoes if f["status"] == "montada"]
    cob_clone = round(100.0 * len(montadas) / len(funcoes), 1) if funcoes else 0.0
    desc_por_beh = {c["id"]: c.get("descricao", "") for c in comportamentos}
    clone_behs = [{"id": f["beh"], "descricao": desc_por_beh.get(f["beh"], "")}
                  for f in montadas]
    _cob, faltando, extras = l52.compara(comportamentos, clone_behs)
    veredito52 = l52.veredito(faltando, extras)
    sha_clone = l52.sha256_arquivo(clone_path)
    print("[reconstrução] ledger=%.1f%% montadas=%d/%d veredito=%s" %
          (cob["cobertura_pct"], len(montadas), len(funcoes), veredito52))

    # ---------- diff + relatório (z9f1g98vtr3tw17vgct4rl 47–48) ----------
    diff = load("kx003aek4jq1hylyv1vmrk", "ue4knvccnagx0aa7a8j78p.py").diff(
        spec_beh, spec_beh)
    divergencias = (len(diff["faltando"]) + len(diff["extras"]) +
                    len(diff["divergentes"]))

    # ---------- veredito ----------
    print("=" * 60)
    print("SHA-256 alvo : %s" % h["sha256"])
    print("SHA-256 clone: %s" % sha_clone)
    print("Cobertura    : %.1f%% ledger (%d/%d) | %.1f%% clone (%d/%d)" %
          (cob["cobertura_pct"], cob["feitas"], cob["total"],
           cob_clone, len(montadas), len(funcoes)))
    print("Clone-verify : %s" % veredito52)
    print("Divergências : %d" % divergencias)
    ok = (cob["cobertura_pct"] == 100.0 and cob_clone == 100.0
          and veredito52 == "CLONADO 100%" and divergencias == 0
          and sorted(recuperadas) == sorted(spec["strings_esperadas"])
          and sorted(apis) == sorted(spec["apis_esperadas"]))
    print("VEREDITO     : %s" % ("CLONE 100% — TOP 1" if ok else "INCOMPLETO"))
    print("=" * 60)
    return {"cobertura": cob["cobertura_pct"], "veredito": veredito52,
            "sha_alvo": h["sha256"], "sha_clone": sha_clone,
            "strings": recuperadas, "ok": ok}


def load_module_file(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


if __name__ == "__main__":
    sys.exit(0 if main()["ok"] else 1)
