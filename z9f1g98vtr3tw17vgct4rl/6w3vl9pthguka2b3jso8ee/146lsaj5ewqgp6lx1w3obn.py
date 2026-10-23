#!/usr/bin/env python3
"""Adapta/verifica convencao de chamada x64 num trecho de disassembly.

Somente biblioteca padrao. Tabela embutida das diferencas x86/x64:
ordem de registradores de argumentos x64 (rcx, rdx, r8, r9), enderecamento
RIP-relativo (lea com [rip+...]) e shadow space de 32 bytes (sub rsp, 0x20).

Valida se a sequencia de argumentos segue a convencao x64 (ate 4 argumentos
em rcx/rdx/r8/r9) e detecta padroes RIP-relativos.
"""

import argparse
import json
import re

# Tabela embutida: diferencas x86 -> x64.
ARG_REGS = ["rcx", "rdx", "r8", "r9"]
SHADOW_SPACE = 0x20

_LINE_RE = re.compile(
    r"^\s*(?:(0x[0-9a-fA-F]+|[0-9a-fA-F]{4,})\s*:?\s+)?"  # endereco opcional
    r"([a-zA-Z]+)"                                       # mnemonico
    r"\s*(.*?)\s*$"                                      # operandos
)
_REG_RE = re.compile(r"\b(rcx|rdx|r8|r9|rsp)\b", re.IGNORECASE)


def parse(text):
    """Converte texto de disassembly em lista de {addr, mnemonic, operands}."""
    insns = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith(";") or line.startswith("#"):
            continue
        m = _LINE_RE.match(line)
        if not m:
            continue
        addr_text, mnemonic, operands = m.group(1), m.group(2), m.group(3)
        mnemonic = mnemonic.lower()
        if mnemonic not in ("mov", "lea", "xor", "push", "sub", "call"):
            continue
        addr = int(addr_text, 16) if addr_text else None
        insns.append({"addr": addr, "mnemonic": mnemonic,
                      "operands": operands.lower()})
    return insns


def _dest_reg(insn):
    """Registrador de destino de mov/lea/xor (primeiro operando)."""
    parts = insn["operands"].split(",", 1)
    if not parts:
        return None
    m = re.match(r"^\s*([a-z][a-z0-9]*)\s*$", parts[0])
    return m.group(1) if m else None


def analyze(text):
    insns = parse(text)
    rip_relative = []
    notes = []

    for insn in insns:
        if "[rip" in insn["operands"] or "[rel " in insn["operands"]:
            if insn["addr"] is not None:
                rip_relative.append("0x%X" % insn["addr"])
                notes.append("enderecamento RIP-relativo em 0x%X"
                             % insn["addr"])

    # Shadow space: sub rsp, 0x20 antes de call.
    shadow = any(i["mnemonic"] == "sub" and _dest_reg(i) == "rsp"
                 and "0x20" in i["operands"] for i in insns)
    if shadow:
        notes.append("shadow space de 32 bytes detectado (sub rsp, 0x20)")

    # Push de argumentos antes de call = estilo x86 (ver janela da chamada).
    args_ok = True

    call_idx = _first_call_idx(insns)
    if call_idx is not None:
        window = insns[max(0, call_idx - 8):call_idx]
        pushes = [i for i in window if i["mnemonic"] == "push"]
        if pushes:
            notes.append("push de argumentos detectado — estilo x86, "
                         "incompativel com a convencao x64")
            args_ok = False
        # Ordem de atribuicao dos registradores de argumento.
        seen = []
        for i in window:
            if i["mnemonic"] in ("mov", "lea", "xor"):
                reg = _dest_reg(i)
                if reg in ARG_REGS and reg not in seen:
                    seen.append(reg)
        if seen:
            expected = ARG_REGS[:len(seen)]
            if seen != expected:
                notes.append("ordem de argumentos fora da convencao x64: "
                             "%s (esperado %s)"
                             % (", ".join(seen), ", ".join(expected)))
                args_ok = False
            else:
                notes.append("%d argumento(s) em %s, conforme a convencao x64"
                             % (len(seen), ", ".join(seen)))
        else:
            notes.append("nenhum argumento em registrador detectado antes "
                         "da chamada")
    else:
        notes.append("nenhuma instrucao call encontrada no trecho")

    return {
        "args_ok": args_ok,
        "rip_relative": sorted(set(rip_relative)),
        "notes": notes,
    }


def _first_call_idx(insns):
    for idx, insn in enumerate(insns):
        if insn["mnemonic"] == "call":
            return idx
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Valida convencao x64 num trecho de disassembly."
    )
    parser.add_argument("input", help="Arquivo texto com o disassembly.")
    args = parser.parse_args(argv)
    with open(args.input, "r", encoding="utf-8") as fh:
        print(json.dumps(analyze(fh.read()), indent=2))


if __name__ == "__main__":
    main()
