#!/usr/bin/env python3
"""
context_map - a structural map of a codebase, no dependencies.

LLMs cannot hold a large repo in their context window - the documented root
cause of duplicated code and broken local conventions. Before writing or
reviewing code you must see the whole shape: which symbols exist, their
signatures (so you can reason about every parameter), and which ones are
load-bearing (referenced by many others) versus throwaway helpers.

This is a stdlib approximation of Aider's tree-sitter + PageRank repo map. It
uses Python's `ast` for .py (exact) and pragmatic regex for other languages,
then ranks symbols by how often their name is referenced across the repo -
the same insight Aider encodes: a function called by 20 others is more important
context than a private helper called once. Changing a high-reference signature
ripples widely, which is exactly the scalability question to ask in review.

It does NOT build a true call graph or PageRank (no tree-sitter); reference
counts are identifier-frequency heuristics. Honest and good enough to navigate.

Usage:
    context_map .                       # map the whole tree
    context_map src/ --top 15           # show the 15 most-referenced symbols
    context_map . --ext .py,.ts --json  # restrict languages, machine output
"""

from __future__ import annotations

import argparse
import ast
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Optional

from _scan_common import (DEFAULT_CODE_EXTS, add_common_filter_args, iter_files,
                          resolve_filters, resolve_root, run_cli)

_IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")

# Pragmatic declaration patterns for non-Python languages. Each yields the
# symbol name in group "name"; the matched line becomes the signature.
_REGEX_RULES = (
    (r"^\s*(?:export\s+)?(?:public\s+|private\s+|protected\s+|static\s+|async\s+)*"
     r"class\s+(?P<name>[A-Za-z_]\w*)", "class"),
    (r"^\s*(?:export\s+)?(?:interface|trait|struct|enum|type)\s+(?P<name>[A-Za-z_]\w*)", "type"),
    (r"^\s*(?:export\s+)?(?:public\s+|private\s+|protected\s+|static\s+|async\s+)*"
     r"func(?:tion)?\s+(?P<name>[A-Za-z_]\w*)\s*\(", "func"),
    (r"^\s*func\s+\([^)]*\)\s+(?P<name>[A-Za-z_]\w*)\s*\(", "func"),      # Go method
    (r"^\s*(?:export\s+)?fn\s+(?P<name>[A-Za-z_]\w*)\s*[(<]", "func"),     # Rust
    (r"^\s*(?:export\s+)?(?:const|let)\s+(?P<name>[A-Za-z_]\w*)\s*=\s*"
     r"(?:async\s+)?\([^)]*\)\s*=>", "func"),                              # JS arrow
    (r"^\s*def\s+(?P<name>[A-Za-z_]\w*)", "func"),                          # Ruby/py-like
)
_COMPILED_RULES = [(re.compile(p), kind) for p, kind in _REGEX_RULES]


def _signature_py(node: ast.AST) -> str:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        try:
            return f"{node.name}({ast.unparse(node.args)})"
        except Exception:
            return f"{node.name}(...)"
    if isinstance(node, ast.ClassDef):
        bases = ", ".join(ast.unparse(b) for b in node.bases) if node.bases else ""
        return f"class {node.name}" + (f"({bases})" if bases else "")
    return getattr(node, "name", "?")


def _extract_python(path: Path, rel: str) -> list[dict[str, Any]]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except (SyntaxError, ValueError):
        return _extract_regex(path, rel)  # fall back if it doesn't parse
    out: list[dict[str, Any]] = []
    for node in tree.body:  # module-level only, then class methods one level down
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.append({"name": node.name, "kind": "func", "file": rel,
                        "line": node.lineno, "sig": _signature_py(node),
                        "private": node.name.startswith("_")})
        elif isinstance(node, ast.ClassDef):
            out.append({"name": node.name, "kind": "class", "file": rel,
                        "line": node.lineno, "sig": _signature_py(node),
                        "private": node.name.startswith("_")})
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    out.append({"name": sub.name, "kind": "method", "file": rel,
                                "line": sub.lineno,
                                "sig": f"{node.name}.{_signature_py(sub)}",
                                "private": sub.name.startswith("_")})
    return out


def _extract_regex(path: Path, rel: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return out
    for lineno, line in enumerate(lines, start=1):
        for pat, kind in _COMPILED_RULES:
            m = pat.match(line)
            if m:
                name = m.group("name")
                out.append({"name": name, "kind": kind, "file": rel,
                            "line": lineno, "sig": line.strip()[:100],
                            "private": name.startswith("_")})
                break  # one symbol per line
    return out


def build_map(root: Path, exts: set[str], ignores: set[str]) -> dict[str, Any]:
    files = list(iter_files(root, exts, ignores))
    base = root if root.is_dir() else root.parent
    symbols: list[dict[str, Any]] = []
    token_counts: Counter[str] = Counter()
    loc_by_file: dict[str, int] = {}

    for path in files:
        rel = str(path.relative_to(base))
        text = path.read_text(encoding="utf-8", errors="ignore")
        loc_by_file[rel] = text.count("\n") + 1
        token_counts.update(_IDENT.findall(text))
        if path.suffix == ".py":
            symbols.extend(_extract_python(path, rel))
        else:
            symbols.extend(_extract_regex(path, rel))

    # reference count = global identifier frequency minus the definitions themselves
    defs_named: Counter[str] = Counter(s["name"] for s in symbols)
    for s in symbols:
        name = s["name"]
        refs = token_counts.get(name, 0) - defs_named[name]
        s["refs"] = max(0, refs) if len(name) >= 3 else 0  # short names too noisy

    symbols.sort(key=lambda s: (s["refs"], s["file"], s["line"]), reverse=True)
    return {
        "files_scanned": len(files),
        "total_loc": sum(loc_by_file.values()),
        "total_symbols": len(symbols),
        "symbols": symbols,
        "loc_by_file": loc_by_file,
    }


def render(m: dict[str, Any], top: int) -> str:
    parts = [f"{m['files_scanned']} files, {m['total_loc']} lines, "
             f"{m['total_symbols']} symbols\n"]

    hotspots = [s for s in m["symbols"] if s["refs"] > 0][:top]
    if hotspots:
        parts.append(f"most-referenced symbols (load-bearing - changing these ripples):")
        for s in hotspots:
            tag = "·private" if s["private"] else ""
            parts.append(f"  {s['refs']:>4} refs  {s['kind']:<6} {s['sig']}  "
                         f"({s['file']}:{s['line']}){tag}")
        parts.append("")

    parts.append("structure by file:")
    by_file: dict[str, list[dict[str, Any]]] = {}
    for s in m["symbols"]:
        by_file.setdefault(s["file"], []).append(s)
    for rel in sorted(by_file):
        parts.append(f"  {rel}  ({m['loc_by_file'].get(rel, 0)} lines)")
        for s in sorted(by_file[rel], key=lambda x: x["line"]):
            marker = {"class": "C", "type": "T", "method": "·", "func": "f"}.get(s["kind"], "?")
            parts.append(f"      {marker} {s['sig']}")
    return "\n".join(parts)


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(prog="context_map",
                                description="Structural map of a codebase.")
    add_common_filter_args(p)
    p.add_argument("--top", type=int, default=20, help="how many hotspots to show")
    args = p.parse_args(argv)

    root = resolve_root(args.path, "context_map")
    exts, ignores = resolve_filters(args.ext, args.ignore, DEFAULT_CODE_EXTS)
    m = build_map(root, exts, ignores)
    print(json.dumps(m, indent=2, ensure_ascii=False) if args.json else render(m, args.top))
    return 0


if __name__ == "__main__":
    run_cli(main)
