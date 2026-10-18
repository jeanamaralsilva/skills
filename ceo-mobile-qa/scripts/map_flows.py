#!/usr/bin/env python3
"""Screens, actions and states of a React Native / Expo app, and the test matrix they imply.

Usage: python map_flows.py <mobile-repo> [--json] [--screen <substring>]

Reads expo-router files under app/ (or src/app/), and falls back to any *Screen.tsx under
src/. For every screen it lists the tappable actions (Pressable, TouchableOpacity, Button,
Link) with their label, whether the handler writes something (mutation, push, fetch), and
which UI states the file handles (loading, empty, error). Then it expands each action into
the paths worth testing: feliz, triste, duplo-toque, sem-rede, background-no-meio.
Static only: it never runs the app. Dynamic routes keep their [param] segments.
"""
import argparse
import json
import os
import re
import sys

SKIP_DIRS = {"node_modules", ".git", "__tests__", "ios", "android", ".expo", "dist", "build"}
ROUTE_EXT = (".tsx", ".jsx", ".ts", ".js")
ACTION_TAGS = ("Pressable", "TouchableOpacity", "TouchableHighlight", "TouchableWithoutFeedback", "Button", "Link", "Chip", "IconButton", "ListItem")
OPEN_TAG = re.compile(r"<(" + "|".join(ACTION_TAGS) + r")\b")
ON_PRESS = re.compile(r"onPress=\{(.*?)\}\s*(?:\w+=|/?>|$)", re.S)
LABEL_ATTR = re.compile(r"(?:title|accessibilityLabel|aria-label|label)=\"([^\"]+)\"")
TEST_ID = re.compile(r"testID=\"([^\"]+)\"")
TEXT_IN_CHILDREN = re.compile(r">\s*([^<{][^<{]*?)\s*<|<Text[^>]*>\s*([^<{]+?)\s*</Text>")
MUTATION_HINTS = ("mutate(", "mutateAsync(", ".push(", "fetch(", "axios.", "api.post", "api.put", "api.delete", "supabase.", "upload(", "save(", "submit(", "send(", "create(", "delete(", "update(")
STATE_HINTS = {
    "loading": re.compile(r"\b(isPending|isLoading|isFetching|Skeleton|Spinner|ActivityIndicator|loading)\b"),
    "error": re.compile(r"\b(isError|error|ErrorState|ErrorBoundary|onError|catch)\b"),
    "empty": re.compile(r"(EmptyState|ListEmptyComponent|length === 0|length == 0|isEmpty|Nenhum|Nothing here|No results)"),
}


def read(path: str) -> str:
    try:
        with open(path, encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


def route_files(repo: str) -> list[tuple[str, str]]:
    """(route, file) pairs. expo-router first; *Screen files as fallback."""
    for base in ("app", "src/app"):
        root = os.path.join(repo, base)
        if os.path.isdir(root):
            pairs = []
            for dirpath, dirnames, filenames in os.walk(root):
                dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
                for name in filenames:
                    stem, ext = os.path.splitext(name)
                    if ext not in ROUTE_EXT or stem.startswith(("_", "+")) or stem.endswith((".test", ".spec")):
                        continue
                    rel = os.path.relpath(os.path.join(dirpath, stem), root).replace(os.sep, "/")
                    route = "/" + (rel[:-5] if rel.endswith("index") else rel)
                    pairs.append((route, os.path.join(dirpath, name)))
            return sorted(pairs)
    pairs = []
    for dirpath, dirnames, filenames in os.walk(repo):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if re.search(r"(Screen|-screen|\.screen)\.(tsx|jsx)$", name):
                pairs.append(("/" + os.path.splitext(name)[0], os.path.join(dirpath, name)))
    return sorted(pairs)


def mutation_names(source: str) -> set[str]:
    names = set(re.findall(r"const\s+(\w+)\s*=\s*useMutation", source))
    names |= set(re.findall(r"mutationFn:\s*(\w+)", source))
    names |= set(re.findall(r"(?:const|function)\s+(\w+)[^\n]*(?:=>|\{)[^\n]*(?:channel\.push|fetch\(|axios\.|api\.(?:post|put|delete))", source))
    return names


def elements(source: str):
    """(tag, attrs, children, start) for every action tag; attrs may contain `{...}` with `>` inside."""
    for match in OPEN_TAG.finditer(source):
        tag, i, depth, quote = match.group(1), match.end(), 0, ""
        while i < len(source):
            ch = source[i]
            if quote:
                quote = "" if ch == quote else quote
            elif ch in "\"'":
                quote = ch
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            elif ch == ">" and depth == 0:
                break
            i += 1
        attrs = source[match.end():i]
        if attrs.rstrip().endswith("/"):
            yield tag, attrs, "", match.start()
            continue
        close = source.find(f"</{tag}>", i)
        yield tag, attrs, source[i + 1:close] if close != -1 else "", match.start()


def actions_of(source: str) -> list[dict]:
    muts = mutation_names(source)
    found = []
    for tag, attrs, children, start in elements(source):
        handler_match = ON_PRESS.search(attrs)
        handler = handler_match.group(1).strip() if handler_match else ""
        label = ""
        if children:
            m = TEXT_IN_CHILDREN.search(">" + children + "<")
            if m:
                label = (m.group(1) or m.group(2) or "").strip()
        for regex in (LABEL_ATTR, TEST_ID):
            if label:
                break
            m = regex.search(attrs)
            if m:
                label = m.group(1)
        if not label:
            label = handler or tag
        is_mutation = any(hint in handler for hint in MUTATION_HINTS) or any(re.search(rf"\b{re.escape(n)}\b", handler) for n in muts)
        found.append({"tag": tag, "label": label[:60], "handler": handler[:80], "mutation": bool(is_mutation),
                      "line": source.count("\n", 0, start) + 1})
    return found


def scan(repo: str) -> dict:
    screens = []
    for route, path in route_files(repo):
        source = read(path)
        screens.append({
            "route": route,
            "file": os.path.relpath(path, repo).replace(os.sep, "/"),
            "dynamic": "[" in route,
            "actions": actions_of(source),
            "states": {name: bool(regex.search(source)) for name, regex in STATE_HINTS.items()},
            "has_query": bool(re.search(r"\buse(?:Query|InfiniteQuery|SWR)\b|\.get\(|fetch\(", source)),
            "has_socket": bool(re.search(r"channel\.(?:on|push)|socket\.|Socket\(", source)),
        })
    return {"repo": os.path.abspath(repo), "screens": screens}


def matrix(result: dict) -> list[dict]:
    rows = []
    for screen in result["screens"]:
        if screen["dynamic"]:
            rows.append({"screen": screen["route"], "action": "(abrir)", "path": "deep-link-frio", "bugs": "B28,B29",
                         "why": "rota com parâmetro: abrir com app fechado, aberto e deslogado"})
        if screen["has_query"] and not screen["states"]["error"]:
            rows.append({"screen": screen["route"], "action": "(carregar)", "path": "erro-sem-tratamento", "bugs": "B12",
                         "why": "busca dado mas não trata erro no arquivo"})
        if screen["has_query"] and not screen["states"]["empty"]:
            rows.append({"screen": screen["route"], "action": "(carregar)", "path": "vazio", "bugs": "",
                         "why": "busca dado mas não tem estado vazio"})
        if screen["has_socket"]:
            rows.append({"screen": screen["route"], "action": "(tempo real)", "path": "reconexao", "bugs": "B41,B42,B43",
                         "why": "usa canal: derrubar socket no meio e conferir rejoin e dado perdido"})
        for action in screen["actions"]:
            base = {"screen": screen["route"], "action": action["label"], "line": action["line"]}
            rows.append({**base, "path": "feliz", "bugs": "", "why": "faz o que o rótulo promete"})
            rows.append({**base, "path": "triste", "bugs": "B27,B33", "why": "entrada inválida, permissão negada, teclado cobrindo"})
            if action["mutation"]:
                rows.append({**base, "path": "duplo-toque", "bugs": "B01", "why": "escreve dado: tocar 2-5x rápido"})
                rows.append({**base, "path": "sem-rede", "bugs": "B12,B13,B40", "why": "escreve dado: modo avião antes e durante"})
                rows.append({**base, "path": "background-no-meio", "bugs": "B15,B18", "why": "Home durante a escrita e voltar"})
    return rows


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--screen", help="only screens whose route contains this")
    args = parser.parse_args(argv)
    result = scan(args.repo)
    if args.screen:
        result["screens"] = [s for s in result["screens"] if args.screen in s["route"]]
    rows = matrix(result)
    if args.json:
        print(json.dumps({**result, "matrix": rows}, ensure_ascii=False, indent=2))
        return 0
    if not result["screens"]:
        print("nenhuma tela encontrada (procurei app/, src/app/ e *Screen.tsx)")
        return 1
    print(f"{len(result['screens'])} telas, {sum(len(s['actions']) for s in result['screens'])} ações, {len(rows)} casos na matriz\n")
    for screen in result["screens"]:
        missing = [k for k, v in screen["states"].items() if not v]
        flags = (" [dinâmica]" if screen["dynamic"] else "") + (" [tempo real]" if screen["has_socket"] else "")
        print(f"{screen['route']}{flags}  {screen['file']}  estados faltando: {', '.join(missing) or 'nenhum'}")
        for action in screen["actions"]:
            print(f"   - {action['label']}{' [escreve]' if action['mutation'] else ''}  (linha {action['line']})")
    print("\nmatriz (tela | ação | caminho | bugs | por quê):")
    for row in rows:
        print(f"  {row['screen']} | {row['action']} | {row['path']} | {row['bugs'] or '-'} | {row['why']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
