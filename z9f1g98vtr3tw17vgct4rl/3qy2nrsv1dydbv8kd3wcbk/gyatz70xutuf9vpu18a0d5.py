#!/usr/bin/env python3
"""Event IDs do WFP como telemetria de rede por processo (fixtures sinteticas).

IDs: 5156 conexao permitida, 5158 bind permitido, 5157 conexao bloqueada,
5159 bind bloqueado, 5152 pacote bloqueado, 5153 pacote bloqueado por filtro
MAIS restritivo (camada L2 -- invisivel na GUI). Habilitados via auditpol nas
subcategorias 'Filtering Platform Connection' e 'Packet Drop'.

O lab constroi o grafo de conexoes por processo (pid, caminho, IPs, portas)
a partir de eventos sinteticos.
"""
import argparse
import json
from collections import defaultdict

EVENT_IDS = {
    5156: "permitted-connection",
    5158: "permitted-bind",
    5157: "blocked-connection",
    5159: "blocked-bind",
    5152: "blocked-packet",
    5153: "blocked-packet-l2-restrictive",
}

CONNECTION_IDS = {5156, 5157}
BIND_IDS = {5158, 5159}


def parse_events(events: list) -> dict:
    """Grafo por processo: {pid: {process, connections[], binds[], blocks[]}}."""
    graph = {}
    for e in events:
        eid = e.get("event_id")
        if eid not in EVENT_IDS:
            continue
        pid = str(e.get("pid"))
        node = graph.setdefault(pid, {"process": e.get("process", "?"),
                                      "connections": [], "binds": [],
                                      "blocks": []})
        rec = {"id": eid, "kind": EVENT_IDS[eid], "src": e.get("src"),
               "dst": e.get("dst"), "sport": e.get("sport"),
               "dport": e.get("dport"), "proto": e.get("proto")}
        if eid in CONNECTION_IDS:
            node["connections"].append(rec)
        elif eid in BIND_IDS:
            node["binds"].append(rec)
        else:
            node["blocks"].append(rec)
    return graph


def l2_invisible(graph: dict) -> list:
    """Eventos 5153: filtragem L2 que nem a GUI mostra."""
    out = []
    for pid, node in graph.items():
        for b in node["blocks"]:
            if b["id"] == 5153:
                out.append({"pid": pid, "process": node["process"], **b})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Telemetria WFP (sintetica)")
    ap.add_argument("--events", default="events.json")
    a = ap.parse_args(argv)
    with open(a.events, encoding="utf-8") as f:
        events = json.load(f)
    g = parse_events(events)
    print(json.dumps({"processes": len(g), "graph": g,
                      "l2_invisible": l2_invisible(g)}, indent=2))


if __name__ == "__main__":
    main()
