#!/usr/bin/env python3
"""Emite templates de codigo Python para cada API mapeada nas evidencias.

Entrada: mapa JSON do lab 44 {"mapa": {BEH-id: {funcoes, evidencias}}}.
         As descricoes das evidencias sao varridas em busca de APIs
         conhecidas; para cada uma, emite o trecho de codigo equivalente
         a partir da tabela interna API -> template.
Saida: JSON {"templates": [{api, categoria, comportamento, funcao,
         evidencia, codigo}]} e, opcional, um arquivo .py com os trechos.
"""

import argparse
import json
import re
import sys

# Tabela interna: nome normalizado -> {api, categoria, template}.
# Os templates sao pontos de partida com TODOs; ajuste os argumentos
# conforme as evidencias de cada comportamento.
API_TEMPLATES = {
    "createfile": ("CreateFileA", "arquivo",
        "handle = open(caminho, modo)  # TODO: caminho/modo vindos da evidencia\n"
        "# equivale a CreateFileA"),
    "readfile": ("ReadFile", "arquivo",
        "dados = handle.read(tamanho)  # TODO: tamanho da evidencia\n"
        "# equivale a ReadFile"),
    "writefile": ("WriteFile", "arquivo",
        "handle.write(dados)  # equivale a WriteFile"),
    "closehandle": ("CloseHandle", "arquivo",
        "handle.close()  # equivale a CloseHandle"),
    "regopenkey": ("RegOpenKeyEx", "registro",
        "import winreg\n"
        "chave = winreg.OpenKey(winreg.HKEY_CURRENT_USER, subchave)  # TODO: hive/subchave\n"
        "# equivale a RegOpenKeyEx"),
    "regsetvalue": ("RegSetValueEx", "registro",
        "import winreg\n"
        "winreg.SetValueEx(chave, nome, 0, winreg.REG_SZ, valor)  # TODO: nome/valor\n"
        "# equivale a RegSetValueEx"),
    "regcreatekey": ("RegCreateKeyEx", "registro",
        "import winreg\n"
        "chave = winreg.CreateKey(winreg.HKEY_CURRENT_USER, subchave)  # TODO\n"
        "# equivale a RegCreateKeyEx"),
    "createprocess": ("CreateProcess", "processo",
        "import subprocess\n"
        "proc = subprocess.Popen([executavel, *args])  # TODO: linha de comando\n"
        "# equivale a CreateProcess"),
    "socket": ("socket", "rede",
        "import socket\n"
        "s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TODO: familia/tipo\n"
        "# equivale a socket()"),
    "connect": ("connect", "rede",
        "s.connect((host, porta))  # TODO: host/porta da evidencia\n"
        "# equivale a connect()"),
    "send": ("send", "rede",
        "s.sendall(dados)  # equivale a send()"),
    "recv": ("recv", "rede",
        "dados = s.recv(tamanho)  # TODO: tamanho\n"
        "# equivale a recv()"),
    "virtualalloc": ("VirtualAlloc", "memoria",
        "import ctypes\n"
        "buf = ctypes.create_string_buffer(tamanho)  # TODO: tamanho/protecao\n"
        "# equivale a VirtualAlloc"),
    "writeprocessmemory": ("WriteProcessMemory", "memoria",
        "import ctypes\n"
        "# TODO: obter handle do processo e endereco via evidencias\n"
        "ctypes.windll.kernel32.WriteProcessMemory(handle, endereco, dados, len(dados), None)\n"
        "# equivale a WriteProcessMemory"),
    "createremotethread": ("CreateRemoteThread", "processo",
        "import ctypes\n"
        "# TODO: handle, endereco inicial e parametro via evidencias\n"
        "ctypes.windll.kernel32.CreateRemoteThread(handle, None, 0, endereco, None, 0, None)\n"
        "# equivale a CreateRemoteThread"),
    "openprocess": ("OpenProcess", "processo",
        "import ctypes\n"
        "handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, pid)  # TODO: pid\n"
        "# equivale a OpenProcess"),
    "getasynckeystate": ("GetAsyncKeyState", "input",
        "import ctypes\n"
        "pressionada = ctypes.windll.user32.GetAsyncKeyState(codigo_tecla) & 0x8000  # TODO\n"
        "# equivale a GetAsyncKeyState"),
    "setwindowshookex": ("SetWindowsHookEx", "input",
        "import ctypes\n"
        "# TODO: tipo de hook, callback e modulo via evidencias\n"
        "hook = ctypes.windll.user32.SetWindowsHookExW(tipo, callback, modulo, 0)\n"
        "# equivale a SetWindowsHookEx"),
    "createmutex": ("CreateMutex", "sincronizacao",
        "import ctypes\n"
        "mutex = ctypes.windll.kernel32.CreateMutexW(None, False, nome)  # TODO: nome\n"
        "# equivale a CreateMutex"),
    "urldownloadtofile": ("URLDownloadToFile", "rede",
        "import urllib.request\n"
        "urllib.request.urlretrieve(url, destino)  # TODO: url/destino\n"
        "# equivale a URLDownloadToFile"),
    "shellexecute": ("ShellExecute", "processo",
        "import subprocess\n"
        "subprocess.Popen([alvo])  # TODO: alvo/parametros\n"
        "# equivale a ShellExecute"),
    "cryptdecrypt": ("CryptDecrypt", "cripto",
        "# TODO: reproduzir o algoritmo a partir da evidencia (chave, modo)\n"
        "dados_claros = decifrar(dados_cifrados, chave)  # implementar decifrar()\n"
        "# equivale a CryptDecrypt"),
    "httpsendrequest": ("HttpSendRequest", "rede",
        "import urllib.request\n"
        "resposta = urllib.request.urlopen(url, data=corpo)  # TODO: url/corpo\n"
        "# equivale a HttpSendRequest"),
}


def normaliza_api(nome):
    """Normaliza nome de API para a chave da tabela.

    Remove sufixos A/W e Ex (ex.: RegSetValueExW -> regsetvalue), mas sem
    comer o "ex" de palavras como "mutex": testa candidatos e devolve o
    primeiro que existe na tabela.
    """
    n = nome.lower()
    sem_aw = re.sub(r"[aw]$", "", n)
    candidatos = [n, sem_aw, re.sub(r"ex$", "", n),
                  re.sub(r"ex$", "", sem_aw)]
    for c in candidatos:
        if c in API_TEMPLATES:
            return c
    return sem_aw


def apis_no_texto(texto):
    """Lista as APIs da tabela encontradas no texto (ordem da tabela)."""
    achadas = []
    for chave in API_TEMPLATES:
        if re.search(r"\b%s(ex)?[aw]?\b" % re.escape(chave), texto or "",
                     re.IGNORECASE):
            achadas.append(chave)
    return achadas


def emite_templates(mapa, apis_extras=None):
    """Varre evidencias e monta a lista de templates."""
    templates = []
    vistos = set()
    for bid, vinc in (mapa or {}).items():
        for e in vinc.get("evidencias", []):
            for chave in apis_no_texto(e.get("descricao", "")):
                marca = (bid, chave)
                if marca in vistos:
                    continue
                vistos.add(marca)
                api, categoria, codigo = API_TEMPLATES[chave]
                templates.append({
                    "api": api, "categoria": categoria,
                    "origem": "evidencia",
                    "comportamento": bid,
                    "funcao": e.get("funcao", ""),
                    "evidencia": e.get("id", ""),
                    "codigo": codigo,
                })
    for nome in apis_extras or []:
        chave = normaliza_api(nome.strip())
        if chave in API_TEMPLATES and (None, chave) not in vistos:
            vistos.add((None, chave))
            api, categoria, codigo = API_TEMPLATES[chave]
            templates.append({
                "api": api, "categoria": categoria,
                "origem": "manual",
                "comportamento": None, "funcao": "",
                "evidencia": "",
                "codigo": codigo,
            })
    return templates


def gera_snippet(templates):
    """Concatena os trechos num arquivo .py comentado por API."""
    partes = ['"""Trechos de codigo gerados a partir das APIs mapeadas.\n',
              'Ajuste argumentos conforme as evidencias de cada comportamento.\n',
              '"""\n']
    for t in templates:
        partes.append("# API: %s | comportamento: %s | evidencia: %s"
                      % (t["api"], t["comportamento"], t["evidencia"]))
        partes.append(t["codigo"])
        partes.append("")
    return "\n".join(partes)


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Emite templates de codigo para APIs mapeadas.")
    ap.add_argument("--map", required=True, help="mapa JSON do lab 44")
    ap.add_argument("--apis", default=None,
                    help="arquivo com APIs extras (uma por linha)")
    ap.add_argument("--output", default=None,
                    help="JSON de saida (padrao: stdout)")
    ap.add_argument("--snippet", default=None,
                    help="arquivo .py com os trechos concatenados")
    args = ap.parse_args(argv)

    with open(args.map, encoding="utf-8") as f:
        mapa = json.load(f).get("mapa", {})
    extras = []
    if args.apis:
        with open(args.apis, encoding="utf-8") as f:
            extras = [l.strip() for l in f if l.strip()]

    templates = emite_templates(mapa, extras)
    texto = json.dumps({"templates": templates}, indent=2,
                       ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(texto)
    else:
        sys.stdout.write(texto)
    if args.snippet:
        with open(args.snippet, "w", encoding="utf-8") as f:
            f.write(gera_snippet(templates))


if __name__ == "__main__":
    main()
