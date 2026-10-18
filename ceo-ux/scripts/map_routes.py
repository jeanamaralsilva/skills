#!/usr/bin/env python3
"""Builds a first screen map of an app from its source, before anyone reads a file by hand.

Usage: python map_routes.py <repo-root> [--json]

Detects, in this order, and reports every one found:
  expo-router      files under app/ (or src/app/): (group) folders, [param] segments, _layout
  react-navigation <X.Screen name="..." component={...}> and createXNavigator calls
  next-app         app/**/page.tsx
  flutter          GoRoute(path: ...) and MaterialPageRoute / routes: {...}
  compose          composable("route") inside NavHost
  swiftui          NavigationStack / TabView / .sheet / .navigationDestination occurrences
The output is a starting point for the code-mapper agent, not the final map:
dynamic routes built at runtime do not show up here.
"""
import argparse
import json
import os
import re
import sys

SKIP_DIRS = {"node_modules", ".git", "build", "dist", ".expo", "Pods", ".next", "android/app/build", "ios/build"}
CODE_EXT = (".tsx", ".ts", ".jsx", ".js", ".dart", ".kt", ".swift")

RN_SCREEN = re.compile(
    r"<(\w+)\.Screen\b[^>]*?\bname=\{?[\"']([^\"']+)[\"']\}?"
    r"(?:[^>]*?\b(?:component=\{(\w+)\}|getComponent=\{\(\)\s*=>\s*(\w+)\}))?",
    re.S,
)
RN_NAVIGATOR = re.compile(r"\bcreate\w*?(NativeStack|BottomTab|MaterialTopTab|Stack|Tab|Drawer)Navigator\w*\s*(?:<[^>()]*>)?\s*\(")
FLUTTER_ROUTE = re.compile(r"GoRoute\s*\([^)]*?path:\s*[\"']([^\"']+)[\"']", re.S)
COMPOSE_ROUTE = re.compile(r"\bcomposable\s*(?:<[^>]+>)?\s*\(\s*(?:route\s*=\s*)?[\"']([^\"']+)[\"']")
REEXPORT = re.compile(r"export\s*\{\s*default[^}]*\}\s*from\s*[\"']([^\"']+)[\"']")
ALIAS_ROOTS = ("src", ".")
SOURCE_EXT = (".tsx", ".ts", ".jsx", ".js")


def resolve_reexport(root: str, path: str) -> str | None:
    """Follow `export { default } from '...'` so a thin route points at the real screen file."""
    try:
        text = open(path, encoding="utf-8", errors="ignore").read()
    except OSError:
        return None
    match = REEXPORT.search(text)
    if not match:
        return None
    spec = match.group(1)
    if spec.startswith(("@/", "~/")):
        bases = [os.path.join(root, alias, spec[2:]) for alias in ALIAS_ROOTS]
    elif spec.startswith("."):
        bases = [os.path.normpath(os.path.join(os.path.dirname(path), spec))]
    else:
        return None
    for base in bases:
        for candidate in [base + ext for ext in SOURCE_EXT] + [os.path.join(base, "index" + ext) for ext in SOURCE_EXT]:
            if os.path.isfile(candidate):
                return os.path.relpath(candidate, root)
    return None


SWIFT_NAV = re.compile(r"\b(NavigationStack|NavigationSplitView|TabView|\.sheet|\.fullScreenCover|\.navigationDestination)\b")


def walk_files(root: str):
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for name in files:
            if name.endswith(CODE_EXT):
                yield os.path.join(current, name)


def expo_router_routes(root: str) -> list[dict]:
    routes = []
    for base in ("app", os.path.join("src", "app")):
        app_dir = os.path.join(root, base)
        if not os.path.isdir(app_dir):
            continue
        for path in walk_files(app_dir):
            rel = os.path.relpath(path, app_dir)
            stem, ext = os.path.splitext(rel)
            if ext not in (".tsx", ".ts", ".jsx", ".js") or stem.endswith("+html"):
                continue
            if "__tests__" in stem.split(os.sep) or re.search(r"\.(test|spec)$", stem):
                continue
            parts = stem.split(os.sep)
            is_layout = parts[-1] == "_layout"
            if parts[-1] in ("index", "_layout"):
                parts = parts[:-1]
            url = "/" + "/".join(p for p in parts if not (p.startswith("(") and p.endswith(")")))
            routes.append({
                "kind": "layout" if is_layout else "screen",
                "route": url.replace("//", "/"),
                "groups": [p for p in stem.split(os.sep) if p.startswith("(")],
                "file": os.path.relpath(path, root),
                "target": resolve_reexport(root, path),
            })
    return sorted(routes, key=lambda r: (r["route"], r["kind"]))


def next_app_routes(root: str) -> list[dict]:
    routes = []
    for base in ("app", os.path.join("src", "app")):
        app_dir = os.path.join(root, base)
        if not os.path.isdir(app_dir):
            continue
        for path in walk_files(app_dir):
            if os.path.basename(path) in ("page.tsx", "page.jsx", "page.js"):
                rel = os.path.relpath(os.path.dirname(path), app_dir)
                parts = [] if rel == "." else rel.split(os.sep)
                url = "/" + "/".join(p for p in parts if not p.startswith("("))
                routes.append({"kind": "page", "route": url, "file": os.path.relpath(path, root)})
    return sorted(routes, key=lambda r: r["route"])


def scan_sources(root: str) -> dict[str, list[dict]]:
    found = {"react-navigation": [], "navigators": [], "flutter": [], "compose": [], "swiftui": []}
    for path in walk_files(root):
        rel = os.path.relpath(path, root)
        try:
            text = open(path, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for match in RN_SCREEN.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            found["react-navigation"].append({
                "navigator": match.group(1), "name": match.group(2),
                "component": match.group(3) or match.group(4), "file": f"{rel}:{line}",
            })
        for match in RN_NAVIGATOR.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            found["navigators"].append({"type": match.group(1), "file": f"{rel}:{line}"})
        if path.endswith(".dart"):
            for match in FLUTTER_ROUTE.finditer(text):
                found["flutter"].append({"route": match.group(1), "file": rel})
        if path.endswith(".kt"):
            for match in COMPOSE_ROUTE.finditer(text):
                found["compose"].append({"route": match.group(1), "file": rel})
        if path.endswith(".swift"):
            kinds = sorted(set(SWIFT_NAV.findall(text)))
            if kinds:
                found["swiftui"].append({"file": rel, "uses": kinds})
    return found


def build_map(root: str) -> dict:
    sources = scan_sources(root)
    next_routes = next_app_routes(root)
    result = {
        "root": os.path.abspath(root),
        "expo-router": [] if next_routes else expo_router_routes(root),
        "next-app": next_routes,
        **sources,
    }
    result["detected"] = [k for k, v in result.items() if isinstance(v, list) and v]
    return result


def render_text(screen_map: dict) -> str:
    lines = [f"root: {screen_map['root']}", f"detected: {', '.join(screen_map['detected']) or 'nothing'}"]
    for route in screen_map["expo-router"]:
        target = f" -> {route['target']}" if route.get("target") else ""
        lines.append(f"[expo-router] {route['kind']:6} {route['route']:30} {route['file']}{target}")
    for route in screen_map["next-app"]:
        lines.append(f"[next-app]    page   {route['route']:30} {route['file']}")
    for nav in screen_map["navigators"]:
        lines.append(f"[navigator]   {nav['type']:12} {nav['file']}")
    for screen in screen_map["react-navigation"]:
        lines.append(f"[rn-screen]   {screen['name']:30} {screen['component'] or '-':20} {screen['file']}")
    for route in screen_map["flutter"]:
        lines.append(f"[flutter]     {route['route']:30} {route['file']}")
    for route in screen_map["compose"]:
        lines.append(f"[compose]     {route['route']:30} {route['file']}")
    for item in screen_map["swiftui"]:
        lines.append(f"[swiftui]     {','.join(item['uses']):40} {item['file']}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    screen_map = build_map(args.root)
    print(json.dumps(screen_map, indent=2, ensure_ascii=False) if args.json else render_text(screen_map))
    return 0 if screen_map["detected"] else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
