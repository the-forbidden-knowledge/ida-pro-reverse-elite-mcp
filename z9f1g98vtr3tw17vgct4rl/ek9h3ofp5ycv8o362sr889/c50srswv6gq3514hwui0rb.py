#!/usr/bin/env python3
"""function-anatomy: anatomia estatica de funcao a partir de texto de disassembly.

Le um arquivo de texto com disassembly (uma instrucao por linha, com ou sem
prefixo de endereco) e identifica:
  - prologo:  push ebp/rbp seguido de mov ebp,esp / mov rbp,rsp
  - epilogo:  leave/ret ou mov esp,ebp + pop ebp + ret
  - args:     quantidade de argumentos distintos (padrao arg_N)
  - locals:   quantidade de variaveis locais distintas (padrao var_N)
  - convention: stdcall se a funcao limpa a pilha (ret N);
                cdecl se o chamador limpa (add esp,N) ou ret simples;
                unknown caso contrario.

Uso: python3 c50srswv6gq3514hwui0rb.py <arquivo.asm>
Saida: JSON na stdout.
"""

import argparse
import json
import re
import sys

MNEMONICS = {
    "push", "pop", "mov", "movzx", "movsx", "lea", "xchg",
    "add", "sub", "inc", "dec", "imul", "mul", "div", "idiv", "neg", "not",
    "and", "or", "xor", "shl", "shr", "sar", "rol", "ror",
    "cmp", "test",
    "jmp", "je", "jne", "jz", "jnz", "ja", "jb", "jbe", "jae",
    "jg", "jl", "jge", "jle", "js", "jns", "jo", "jno", "jp", "jnp", "jc",
    "jcxz", "jecxz", "loop", "loope", "loopne",
    "call", "ret", "retn", "retf", "leave", "enter", "int", "nop",
    "pushad", "popad", "pushfd", "popfd",
}

PROLOGUE_PUSH = {"ebp", "rbp"}
PROLOGUE_MOV = {("ebp", "esp"), ("rbp", "rsp")}
EPILOGUE_MOV = {("esp", "ebp"), ("rsp", "rbp")}
EPILOGUE_POP = {"ebp", "rbp"}


def parse_instructions(text):
    """Extrai (mnemonico, operandos) de cada linha de disassembly.

    Ignora comentarios, rotulos e prefixos de endereco/bytes.
    """
    instrs = []
    for raw in text.splitlines():
        line = raw.split(";", 1)[0].strip()
        if not line:
            continue
        if re.fullmatch(r"[A-Za-z_?.@$][\w?.@$]*:", line):
            continue  # rotulo
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
        instrs.append((mnemonic, operands))
    return instrs


def _ops(operands):
    return [o.strip().lower() for o in operands.split(",")]


def has_prologue(instrs):
    for i in range(len(instrs) - 1):
        m1, o1 = instrs[i]
        m2, o2 = instrs[i + 1]
        if m1 == "push" and _ops(o1) and _ops(o1)[0] in PROLOGUE_PUSH:
            parts = _ops(o2)
            if m2 == "mov" and len(parts) == 2 and tuple(parts) in PROLOGUE_MOV:
                return True
    return False


def has_epilogue(instrs):
    for i, (m, o) in enumerate(instrs):
        if m == "leave":
            return True
        if m in ("ret", "retn", "retf"):
            return True
        if m == "mov" and tuple(_ops(o)) in EPILOGUE_MOV:
            # mov esp,ebp ; pop ebp ; ret
            saved = _ops(o)[1]
            rest = instrs[i + 1:i + 3]
            if (len(rest) == 2 and rest[0][0] == "pop"
                    and _ops(rest[0][1]) == [saved]
                    and rest[1][0] in ("ret", "retn", "retf")):
                return True
    return False


def count_names(text, prefix):
    return len(set(re.findall(r"\b" + prefix + r"_([0-9A-Fa-f]+)\b", text)))


def infer_convention(text):
    if re.search(r"\bret\w*\s+(0x[0-9A-Fa-f]+|[0-9A-Fa-f]+h|\d+)\b", text, re.IGNORECASE):
        return "stdcall"
    if re.search(r"\badd\s+(esp|rsp)\s*,", text, re.IGNORECASE):
        return "cdecl"
    if re.search(r"\bret\w*\b", text, re.IGNORECASE):
        return "cdecl"
    return "unknown"


def analyze(text):
    instrs = parse_instructions(text)
    return {
        "prologue": has_prologue(instrs),
        "epilogue": has_epilogue(instrs),
        "args": count_names(text, "arg"),
        "locals": count_names(text, "var"),
        "convention": infer_convention(text),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="arquivo de texto com o disassembly")
    args = parser.parse_args(argv)
    with open(args.input, "r", encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    print(json.dumps(analyze(text), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
