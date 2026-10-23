#!/usr/bin/env python3
"""control-flow: reconhece padroes de fluxo de controle em texto de disassembly.

Detecta:
  - if/else: CMP ou TEST seguido de salto condicional (Jcc);
  - loop:    salto condicional ou JMP para um endereco anterior;
  - switch:  JMP indireto via tabela (ex.: jmp dword ptr [eax*4+0x402000]).

Uso: python3 mptrosthdlemn4edpmu7us.py <arquivo.asm>
Saida: JSON {"patterns": [{"type", "addr", "detail"}]} na stdout.
"""

import argparse
import json
import re
import sys

JCC = {
    "ja", "jb", "jc", "je", "jg", "jl", "jge", "jle", "jbe", "jae",
    "jz", "jnz", "jne", "js", "jns", "jo", "jno", "jp", "jnp",
    "jcxz", "jecxz", "jrcxz",
}
LOOP_INSNS = {"loop", "loope", "loopne", "loopnz", "loopz"}

MNEMONICS = {
    "mov", "movzx", "movsx", "lea", "push", "pop", "xchg",
    "add", "sub", "inc", "dec", "imul", "mul", "div", "idiv", "neg", "not",
    "and", "or", "xor", "shl", "shr", "sar", "rol", "ror",
    "cmp", "test", "call", "ret", "retn", "retf", "leave", "enter",
    "nop", "int",
} | JCC | LOOP_INSNS | {"jmp"}


def _norm_addr(tok):
    tok = tok.rstrip(":")
    return tok if tok.lower().startswith("0x") else "0x" + tok


def parse_lines(text):
    """Retorna lista de dicts: addr (ou None), mnemonic, operands, raw."""
    out = []
    for raw in text.splitlines():
        line = raw.split(";", 1)[0].strip()
        if not line:
            continue
        if re.fullmatch(r"[A-Za-z_?.@$][\w?.@$]*:", line):
            out.append({"addr": None, "mnemonic": "label",
                        "operands": line[:-1], "raw": raw.strip()})
            continue
        tokens = line.split()
        idx = None
        for i, tok in enumerate(tokens):
            if tok.lower() in MNEMONICS:
                idx = i
                break
        if idx is None:
            continue
        addr = None
        if idx > 0 and re.fullmatch(r"(0x)?[0-9A-Fa-f]{3,}:?", tokens[0]):
            addr = _norm_addr(tokens[0])
        mnemonic = tokens[idx].lower()
        operands = " ".join(tokens[idx + 1:])
        out.append({"addr": addr, "mnemonic": mnemonic,
                    "operands": operands, "raw": raw.strip()})
    return out


def _target_addr(operand):
    m = re.search(r"\b(0x[0-9A-Fa-f]+)\b", operand)
    if m:
        return int(m.group(1), 16)
    return None


def _addr_int(addr):
    return int(addr, 16) if addr else None


def _is_switch_jump(mnemonic, operands):
    if mnemonic != "jmp":
        return False
    op = operands.lower().replace(" ", "")
    return "[" in op and ("*4" in op or "*8" in op or "ptr" in op)


def detect(lines):
    patterns = []
    instrs = [l for l in lines if l["mnemonic"] != "label"]
    for i, ins in enumerate(instrs):
        m, op, addr = ins["mnemonic"], ins["operands"], ins["addr"]
        addr_s = addr if addr else f"line{i}"

        # switch: jmp indireto via tabela indexada
        if _is_switch_jump(m, op):
            patterns.append({
                "type": "switch", "addr": addr_s,
                "detail": f"indirect jump via indexed table: {op}",
            })
            continue

        # loop: salto para endereco anterior
        if m in (JCC | LOOP_INSNS | {"jmp"}):
            tgt = _target_addr(op)
            cur = _addr_int(addr)
            if tgt is not None and cur is not None and tgt < cur:
                patterns.append({
                    "type": "loop", "addr": addr_s,
                    "detail": f"{m} {_norm_addr(op)} targets earlier address",
                })
                continue

        # if: cmp/test seguido de jcc
        if m in ("cmp", "test") and i + 1 < len(instrs):
            nxt = instrs[i + 1]
            if nxt["mnemonic"] in JCC:
                patterns.append({
                    "type": "if", "addr": nxt["addr"] or f"line{i+1}",
                    "detail": f"{m} {op} -> {nxt['mnemonic']} {nxt['operands']}",
                })
    return patterns


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="arquivo de texto com o disassembly")
    args = parser.parse_args(argv)
    with open(args.input, "r", encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    print(json.dumps({"patterns": detect(parse_lines(text))}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
