#!/usr/bin/env python3
"""loop-deconstruct: decompoe um bloco de loop em init/condition/update/body.

A partir de um texto de disassembly contendo um loop, identifica:
  - init:      linhas de inicializacao (MOV antes do rotulo do loop);
  - condition: comparacao + salto condicional que fecha o loop (CMP/TEST + Jcc);
  - update:    atualizacao do contador (INC/DEC/ADD/SUB no registrador comparado);
  - body:      demais instrucoes dentro do loop.

Uso: python3 kxva252vefs4lkfh7c072l.py <arquivo.asm>
Saida: JSON {"init", "condition", "update", "body"} na stdout.
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
JUMPS = JCC | {"jmp", "loop", "loope", "loopne", "loopnz", "loopz"}

MNEMONICS = {
    "mov", "movzx", "movsx", "lea", "push", "pop", "xchg",
    "add", "sub", "inc", "dec", "imul", "mul", "div", "idiv", "neg", "not",
    "and", "or", "xor", "shl", "shr", "sar", "rol", "ror",
    "cmp", "test", "call", "ret", "retn", "retf", "leave", "enter",
    "nop", "int",
} | JUMPS


def parse(text):
    """Retorna lista de itens: ("label", nome) ou ("insn", mnemonico, operandos, raw)."""
    items = []
    for raw in text.splitlines():
        line = raw.split(";", 1)[0].strip()
        if not line:
            continue
        m = re.fullmatch(r"([A-Za-z_?.@$][\w?.@$]*):", line)
        if m:
            items.append(("label", m.group(1)))
            continue
        tokens = line.split()
        idx = None
        for i, tok in enumerate(tokens):
            if tok.lower() in MNEMONICS:
                idx = i
                break
        if idx is None:
            continue
        mnemonic = tokens[idx].lower()
        operands = " ".join(tokens[idx + 1:])
        items.append(("insn", mnemonic, operands, raw.strip()))
    return items


def _first_operand_reg(operands):
    m = re.match(r"\s*([a-zA-Z][a-zA-Z0-9]*)\b", operands)
    return m.group(1).lower() if m else None


def deconstruct(text):
    items = parse(text)

    # rotulo do loop: alvo do salto para tras
    loop_label = None
    closing = None  # indice do salto que fecha o loop
    label_pos = {}
    for i, it in enumerate(items):
        if it[0] == "label":
            label_pos[it[1]] = i
    for i, it in enumerate(items):
        if it[0] == "insn" and it[1] in JUMPS:
            tgt = it[2].strip().split(",")[0].strip()
            if tgt in label_pos and label_pos[tgt] < i:
                loop_label = tgt
                closing = i
                break
    if loop_label is None:
        # sem salto para tras: usa o primeiro rotulo como referencia
        for i, it in enumerate(items):
            if it[0] == "label":
                loop_label = it[1]
                break

    init, body = [], []
    condition_parts = []
    counter = None

    # condicao: CMP/TEST imediatamente antes do salto de fechamento
    cond_idx = set()
    if closing is not None:
        prev = closing - 1
        while prev >= 0 and items[prev][0] == "label":
            prev -= 1
        if prev >= 0 and items[prev][0] == "insn" and items[prev][1] in ("cmp", "test"):
            cond_idx.add(prev)
            condition_parts.append(items[prev][3])
            counter = _first_operand_reg(items[prev][2])
        cond_idx.add(closing)
        condition_parts.append(items[closing][3])

    # update: INC/DEC/ADD/SUB operando o contador
    update_idx = set()
    update_parts = []
    if counter:
        for i, it in enumerate(items):
            if it[0] != "insn" or i in cond_idx:
                continue
            mn, op = it[1], it[2]
            reg = _first_operand_reg(op)
            if reg == counter and (
                mn in ("inc", "dec")
                or (mn in ("add", "sub") and re.match(r"\s*" + counter + r"\s*,", op, re.IGNORECASE))
            ):
                update_idx.add(i)
                update_parts.append(it[3])

    # reparte init (antes do rotulo) e body (dentro do loop)
    seen_label = False
    for i, it in enumerate(items):
        if it[0] == "label":
            if it[1] == loop_label:
                seen_label = True
            continue
        if i in cond_idx or i in update_idx:
            continue
        if not seen_label:
            if it[1] == "mov":
                init.append(it[3])
        else:
            body.append(it[3])

    return {
        "init": "\n".join(init),
        "condition": "\n".join(condition_parts),
        "update": "\n".join(update_parts),
        "body": body,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="arquivo de texto com o bloco do loop")
    args = parser.parse_args(argv)
    with open(args.input, "r", encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    print(json.dumps(deconstruct(text), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
