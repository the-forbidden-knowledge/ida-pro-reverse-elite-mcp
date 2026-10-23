#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Exporta do IDA Pro o JSON consumido pelos z9f1g98vtr3tw17vgct4rl de leitura (09-20).

RODA DENTRO DO IDA PRO (File > Script file...), NAO nesta maquina.
Formato de saida:
  {functions: [{name, addr, calls: [apis], xrefs_to: [addrs]}],
   strings:   [{text, addr, xrefs: [addrs]}],
   imports:   {dll: [apis]}}

Somente APIs idaapi/idautils/idc, tudo com try/except: o que falhar vira
lista vazia em vez de derrubar a exportacao.
"""

import json
import os

try:
    import idaapi
    import idautils
    import idc
    _TEM_IDA = True
except Exception:
    _TEM_IDA = False


def _hx(ea):
    try:
        return "0x%x" % int(ea)
    except Exception:
        return str(ea)


def _exportar_funcoes():
    funcoes = []
    try:
        for ea in idautils.Functions():
            try:
                nome = idc.get_func_name(ea) or ("sub_%X" % ea)
                fim = idc.get_func_attr(ea, idc.FUNCATTR_END)
                chamadas = []
                xrefs = []
                try:
                    for head in idautils.Heads(ea, fim):
                        try:
                            if idaapi.is_call_insn(head):
                                alvo = idc.get_operand_value(head, 0)
                                anome = idc.get_name(alvo)
                                if anome:
                                    chamadas.append(anome)
                        except Exception:
                            continue
                except Exception:
                    pass
                try:
                    for xr in idautils.XrefsTo(ea):
                        xrefs.append(_hx(xr.frm))
                except Exception:
                    pass
                # remove duplicadas preservando ordem
                vistas = set()
                unicas = []
                for c in chamadas:
                    if c not in vistas:
                        vistas.add(c)
                        unicas.append(c)
                funcoes.append({"name": nome, "addr": _hx(ea),
                                "calls": unicas, "xrefs_to": xrefs})
            except Exception:
                continue
    except Exception:
        pass
    return funcoes


def _exportar_strings():
    strs = []
    try:
        for s in idautils.Strings():
            try:
                texto = str(s)
                ea = s.ea
                xrefs = []
                try:
                    for xr in idautils.XrefsTo(ea):
                        xrefs.append(_hx(xr.frm))
                except Exception:
                    pass
                strs.append({"text": texto, "addr": _hx(ea), "xrefs": xrefs})
            except Exception:
                continue
    except Exception:
        pass
    return strs


def _exportar_imports():
    imports = {}
    try:
        qtd = idaapi.get_import_module_qty()
        for i in range(qtd):
            try:
                dll = idaapi.get_import_module_name(i) or ("mod_%d" % i)
                nomes = []

                def _cb(ea, nome, ordinal):
                    if nome:
                        nomes.append(nome)
                    return True

                try:
                    idaapi.enum_import_names(i, _cb)
                except Exception:
                    pass
                imports[dll] = nomes
            except Exception:
                continue
    except Exception:
        pass
    return imports


def exportar(caminho_saida=None):
    """Gera o dicionario de exportacao e grava o JSON. Retorna o caminho."""
    if not _TEM_IDA:
        raise RuntimeError("rode este script dentro do IDA Pro "
                           "(File > Script file...)")
    dados = {
        "functions": _exportar_funcoes(),
        "strings": _exportar_strings(),
        "imports": _exportar_imports(),
    }
    if not caminho_saida:
        try:
            base = idaapi.get_input_file_path() or "mrg3ynauhl4c6qu1go4jqo"
        except Exception:
            base = "mrg3ynauhl4c6qu1go4jqo"
        caminho_saida = os.path.splitext(base)[0] + "-mrg3ynauhl4c6qu1go4jqo.json"
        try:
            escolha = idaapi.ask_file(True, caminho_saida,
                                      "Salvar export JSON")
            if escolha:
                caminho_saida = escolha
        except Exception:
            pass
    with open(caminho_saida, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)
    try:
        print("export OK: %s (%d funcoes, %d strings, %d dlls)"
              % (caminho_saida, len(dados["functions"]),
                 len(dados["strings"]), len(dados["imports"])))
    except Exception:
        pass
    return caminho_saida


if __name__ == "__main__":
    exportar()
