#!/usr/bin/env python3
"""Relatorio consolidado de desobfuscacao: roda os z9f1g98vtr3tw17vgct4rl 26-29 e junta tudo.

Somente stdlib. Invoca os CLIs irmaos via subprocess e mescla os JSONs
num relatorio unico.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile

BASE = os.path.dirname(os.path.abspath(__file__))

LABS = {
    "xorsearch": ("maoiosdj9n2pjh2troi74w", "tdszw6xy7o8ndrx31j4vjw.py"),
    "stackstrings": ("r0zx4dq741d2qo17exc2dm", "jsgipjcsv0qjxk2hcjnewc.py"),
    "xor_key": ("5fmv8fp8wxqb3id6swfzdb", "ou9wnph48mbw4l5uta83j2.py"),
    "emulate": ("ho34my4hrz5m5a5kipq3k1", "hzjr418t8gos1vsg2os9uq.py"),
}


def run_lab(name, args):
    folder, script = LABS[name]
    path = os.path.join(BASE, "..", folder, script)
    proc = subprocess.run(
        [sys.executable, path] + args,
        capture_output=True, text=True, timeout=300,
    )
    if proc.returncode != 0:
        return {"error": proc.stderr.strip()[-500:]}
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"raw": proc.stdout.strip()[-500:]}


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def build_report(input_path, plaintext=None, dsl=None, workdir=None):
    report = {
        "input": os.path.basename(input_path),
        "sha256": sha256_of(input_path),
    }
    report["xorsearch"] = run_lab("xorsearch", [input_path, "--top", "5"])
    report["stackstrings"] = run_lab("stackstrings", [input_path])
    if plaintext:
        report["xor_key"] = run_lab(
            "xor_key", [input_path, "--plaintext", plaintext, "--max-key", "8"])
    else:
        report["xor_key"] = None
    if dsl:
        tmp = workdir or tempfile.gettempdir()
        decoded = os.path.join(tmp, "deobf_decoded.bin")
        res = run_lab("emulate", [input_path, dsl, "--output", decoded])
        report["emulated"] = {
            "decoded_to": decoded,
            "sha256": sha256_of(decoded) if os.path.exists(decoded) else None,
            "detail": res,
        }
    else:
        report["emulated"] = None
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Consolida os z9f1g98vtr3tw17vgct4rl 26-29 num relatorio de desobfuscacao."
    )
    ap.add_argument("input", help="arquivo binario de entrada")
    ap.add_argument("--plaintext", "-p", help="fragmento conhecido p/ known-plaintext")
    ap.add_argument("--dsl", help="JSON da mini-DSL de decode")
    ap.add_argument("--output", "-o", help="arquivo de saida JSON")
    args = ap.parse_args(argv)

    report = build_report(args.input, plaintext=args.plaintext, dsl=args.dsl)
    out = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out + "\n")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
