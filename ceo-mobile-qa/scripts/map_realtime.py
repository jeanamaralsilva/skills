#!/usr/bin/env python3
"""Pairs the real-time contract between a Phoenix server and a React Native client.

Usage: python map_realtime.py <mobile-repo> <server-repo> [--json]

Server side (lib/**/*.ex): `channel "topic:*", Module` in the socket, `handle_in("event", ...)`
handlers, and every event the server emits with push/broadcast/broadcast!/broadcast_from.
Mobile side (src/**, app/**): `channel.on("event")` listeners and `channel.push("event")`.
Reports the pairs and, more useful, the gaps: events the server emits that nobody listens to,
listeners waiting for events no server code emits, pushes with no handle_in, and handlers no
screen pushes (so another actor, e.g. the other role, must trigger them in a test).
Phoenix.Presence events (presence_state, presence_diff) and phx_* events are not gaps.
"""
import argparse
import json
import os
import re
import sys

SKIP_DIRS = {"node_modules", ".git", "deps", "_build", "__tests__", "ios", "android", ".expo", "test"}
BUILTIN_EVENTS = {"presence_state", "presence_diff", "phx_join", "phx_leave", "phx_reply", "phx_error", "phx_close", "heartbeat"}
CHANNEL_DECL = re.compile(r'channel\s+"([^"]+)"\s*,\s*([\w.]+)')
HANDLE_IN = re.compile(r'handle_in\(\s*"([^"]+)"')
SERVER_EMIT = re.compile(r'\b(?:push|broadcast!?|broadcast_from!?)\(\s*[^,]+,\s*"([^"]+)"')
SERVER_EMIT_ENDPOINT = re.compile(r'Endpoint\.broadcast!?\(\s*[^,]+,\s*"([^"]+)"')
MOBILE_ON = re.compile(r'\.on\(\s*[\'"]([^\'"]+)[\'"]')
MOBILE_PUSH = re.compile(r'\.push\(\s*[\'"]([^\'"]+)[\'"]')
MOBILE_TOPIC = re.compile(r'\.channel\(\s*[`\'"]([^`\'"]+)[`\'"]')


def walk(root: str, exts: tuple[str, ...]):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name.endswith(exts):
                path = os.path.join(dirpath, name)
                try:
                    with open(path, encoding="utf-8", errors="ignore") as handle:
                        yield os.path.relpath(path, root).replace(os.sep, "/"), handle.read()
                except OSError:
                    continue


def collect(regex: re.Pattern, files) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for rel, source in files:
        for match in regex.finditer(source):
            line = source.count("\n", 0, match.start()) + 1
            found.setdefault(match.group(1), []).append(f"{rel}:{line}")
    return found


def scan(mobile: str, server: str) -> dict:
    server_files = list(walk(server, (".ex", ".exs")))
    mobile_files = list(walk(mobile, (".ts", ".tsx", ".js", ".jsx")))
    topics = collect(CHANNEL_DECL, server_files)
    handlers = collect(HANDLE_IN, server_files)
    emits = collect(SERVER_EMIT, server_files)
    for event, where in collect(SERVER_EMIT_ENDPOINT, server_files).items():
        emits.setdefault(event, []).extend(where)
    emit_triggers = {}
    for rel, source in server_files:
        handler_positions = [(m.start(), m.group(1)) for m in HANDLE_IN.finditer(source)]
        for m in list(SERVER_EMIT.finditer(source)) + list(SERVER_EMIT_ENDPOINT.finditer(source)):
            enclosing = [name for pos, name in handler_positions if pos < m.start()]
            emit_triggers[f"{rel}:{source.count(chr(10), 0, m.start()) + 1}"] = enclosing[-1] if enclosing else ""
    listeners = collect(MOBILE_ON, mobile_files)
    pushes = collect(MOBILE_PUSH, mobile_files)
    mobile_topics = collect(MOBILE_TOPIC, mobile_files)
    return {
        "topics": topics,
        "mobile_topics": mobile_topics,
        "server_handlers": handlers,
        "server_emits": emits,
        "emit_triggers": emit_triggers,
        "mobile_listeners": listeners,
        "mobile_pushes": pushes,
        "paired_server_to_mobile": sorted(set(emits) & set(listeners)),
        "paired_mobile_to_server": sorted(set(pushes) & set(handlers)),
        "server_events_without_listener": sorted(set(emits) - set(listeners) - BUILTIN_EVENTS),
        "mobile_listeners_without_server_event": sorted(set(listeners) - set(emits) - BUILTIN_EVENTS),
        "mobile_pushes_without_handler": sorted(set(pushes) - set(handlers) - BUILTIN_EVENTS),
        "handlers_without_mobile_push": sorted(set(handlers) - set(pushes)),
    }


def matrix(result: dict) -> list[dict]:
    """One test row per server-emitted event: who triggers it and which bugs to try."""
    rows = []
    pushes = set(result["mobile_pushes"])
    handlers = result["server_handlers"]
    emits = result["server_emits"]
    for event, where in sorted(emits.items()):
        triggers = sorted({t for t in (result["emit_triggers"].get(w) for w in where) if t})
        from_mobile = [h for h in triggers if h in pushes]
        actor_b = "mesmo app" if from_mobile else "phx_actor"
        listened = event in result["mobile_listeners"]
        bugs = ["B46"] if listened else ["B43"]
        bugs += ["B41", "B42"] if listened else []
        if "broadcast" in " ".join(where) or not from_mobile:
            bugs.append("B44")
        rows.append({
            "event": event,
            "emitted_at": ", ".join(where[:3]),
            "triggered_by_handlers": ", ".join(triggers) or "?",
            "actor_b": actor_b,
            "mobile_listens": listened,
            "bugs": ",".join(dict.fromkeys(bugs)),
            "test": (f"ator B dispara {', '.join(triggers) or event}; ator A (app) deve refletir {event} "
                     f"{'na tela' if listened else '(sem listener: confirmar se é esperado)'}; repetir com A reconectando"),
        })
    return rows


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mobile")
    parser.add_argument("server")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = scan(args.mobile, args.server)
    rows = matrix(result)
    if args.json:
        print(json.dumps({**result, "matrix": rows}, ensure_ascii=False, indent=2))
        return 0
    if not result["topics"] and not result["mobile_listeners"]:
        print("nenhum canal Phoenix encontrado (procurei `channel \"...\"` no server e `.on(`/`.push(` no mobile)")
        return 1
    print("tópicos do server:", ", ".join(f"{t} ({m})" for t, m in ((t, w[0]) for t, w in result["topics"].items())) or "-")
    print("tópicos que o app abre:", ", ".join(result["mobile_topics"]) or "-")
    print(f"pareados server→app: {', '.join(result['paired_server_to_mobile']) or '-'}")
    print(f"pareados app→server: {', '.join(result['paired_mobile_to_server']) or '-'}")
    for key, label in (
        ("server_events_without_listener", "server emite e ninguém escuta no app"),
        ("mobile_listeners_without_server_event", "app escuta e o server nunca emite"),
        ("mobile_pushes_without_handler", "app envia e não há handle_in (vai dar phx_error)"),
        ("handlers_without_mobile_push", "handle_in que o app nunca envia (outro ator dispara)"),
    ):
        print(f"{label}: {', '.join(result[key]) or '-'}")
    print("\nmatriz multiusuário (evento | ator B | app escuta | bugs | teste):")
    for row in rows:
        print(f"  {row['event']} | {row['actor_b']} | {'sim' if row['mobile_listens'] else 'não'} | {row['bugs']} | {row['test']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
