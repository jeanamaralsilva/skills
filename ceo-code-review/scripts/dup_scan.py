#!/usr/bin/env python3
"""
dup_scan - find copy-paste duplication in a codebase, no dependencies.

AI-assisted code clones at roughly 4x the human rate (GitClear 2024); "copy /
paste" has overtaken "reuse". This scanner is the mechanical gate that frees a
reviewer's attention for architecture: it flags repeated blocks so a human (or
agent) can decide whether to extract a shared function.

It detects Type-1/Type-2 clones - exact and whitespace/comment-reformatted
copies - using normalized sliding windows with greedy extension to report the
*maximal* duplicated region rather than dozens of overlapping fragments. It does
NOT detect Type-4 semantic clones (same behavior, different code); that still
needs human judgment, which is the point.

Usage:
    dup_scan .                         # scan current tree
    dup_scan src/ --min-lines 6        # only blocks of 6+ lines
    dup_scan . --ext .py,.ts --json    # restrict languages, machine output
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Optional

from _scan_common import (DEFAULT_CODE_EXTS, add_common_filter_args, iter_files,
                          resolve_filters, resolve_root, run_cli)

# Duplication is worth catching in shell and SQL too, not just app languages.
DUP_EXTS = DEFAULT_CODE_EXTS + (".sh", ".sql")
_HASH_EXTS = {".py", ".rb", ".sh", ".yml", ".yaml", ".toml", ".pl", ".r"}
_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)


def _strip_comments(text: str, ext: str) -> str:
    """Best-effort comment removal so reformatting doesn't hide a clone.

    Heuristic by design: it can over-strip a `//` or `#` inside a string
    literal, which is acceptable for a duplication signal.
    """
    if ext in _HASH_EXTS:
        return "\n".join(line.split("#", 1)[0] for line in text.splitlines())
    text = _BLOCK_COMMENT.sub("", text)  # /* ... */
    return "\n".join(line.split("//", 1)[0] for line in text.splitlines())


def _significant_lines(path: Path, ext: str, min_chars: int) -> list[tuple[int, str]]:
    """Return [(original_line_no, normalized_text)] for non-trivial lines."""
    try:
        raw = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []
    out: list[tuple[int, str]] = []
    for lineno, original in enumerate(_strip_comments(raw, ext).splitlines(), start=1):
        norm = re.sub(r"\s+", " ", original.strip())
        if len(norm) >= min_chars:
            out.append((lineno, norm))
    return out


def _find_clones(files: list[tuple[Path, list[tuple[int, str]]]], window: int):
    """Greedy maximal-clone detection over normalized lines.

    Seeds on identical N-line windows, then extends both copies forward while
    lines keep matching, so a 40-line paste is one finding, not 35.
    """
    # Flatten to per-file normalized-text arrays for O(1) line comparison.
    norm = [[t for _, t in lines] for _, lines in files]
    seen: dict[str, tuple[int, int]] = {}        # window hash -> first (file, idx)
    consumed: set[tuple[int, int]] = set()        # window-start positions already in a clone
    clones: list[dict[str, Any]] = []

    for fi, arr in enumerate(norm):
        limit = len(arr) - window + 1
        for i in range(max(0, limit)):
            if (fi, i) in consumed:
                continue
            key = "\n".join(arr[i:i + window])
            if key not in seen:
                seen[key] = (fi, i)
                continue
            f1, j = seen[key]
            # Extend the match forward in both copies.
            length = window
            while (j + length < len(norm[f1]) and i + length < len(arr)
                   and norm[f1][j + length] == arr[i + length]):
                length += 1
            for k in range(length):
                consumed.add((f1, j + k))
                consumed.add((fi, i + k))
            a_lines = files[f1][1]
            b_lines = files[fi][1]
            clones.append({
                "lines": length,
                "a": {"file": str(files[f1][0]),
                      "start": a_lines[j][0], "end": a_lines[j + length - 1][0]},
                "b": {"file": str(files[fi][0]),
                      "start": b_lines[i][0], "end": b_lines[i + length - 1][0]},
                "snippet": "\n".join(arr[i:i + min(length, 6)]),
            })
    clones.sort(key=lambda c: c["lines"], reverse=True)
    return clones


def scan(root: Path, exts: set[str], ignores: set[str],
         window: int, min_chars: int) -> dict[str, Any]:
    files = [(p, _significant_lines(p, p.suffix, min_chars)) for p in iter_files(root, exts, ignores)]
    files = [(p, lines) for p, lines in files if lines]
    significant = sum(len(lines) for _, lines in files)
    clones = _find_clones(files, window)

    covered: set[tuple[str, int]] = set()
    for c in clones:
        for side in ("a", "b"):
            for ln in range(c[side]["start"], c[side]["end"] + 1):
                covered.add((c[side]["file"], ln))
    pct = round(100.0 * len(covered) / significant, 1) if significant else 0.0
    return {
        "files_scanned": len(files),
        "significant_lines": significant,
        "duplicate_blocks": len(clones),
        "duplicated_lines": len(covered),
        "duplication_pct": pct,
        "clones": clones,
    }


def render(report: dict[str, Any]) -> str:
    head = (f"scanned {report['files_scanned']} files, "
            f"{report['significant_lines']} significant lines\n"
            f"duplicate blocks: {report['duplicate_blocks']}   "
            f"duplicated lines: {report['duplicated_lines']} "
            f"(~{report['duplication_pct']}%)")
    if not report["clones"]:
        return head + "\n\nNo copy-paste duplication found above the threshold."
    parts = [head, ""]
    for n, c in enumerate(report["clones"], start=1):
        parts.append(
            f"[{n}] {c['lines']} duplicated lines\n"
            f"    A: {c['a']['file']}:{c['a']['start']}-{c['a']['end']}\n"
            f"    B: {c['b']['file']}:{c['b']['start']}-{c['b']['end']}\n"
            f"    | " + "\n    | ".join(c["snippet"].splitlines())
        )
    parts.append("\nConsider extracting shared logic into one function/module.")
    return "\n".join(parts)


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(prog="dup_scan",
                                description="Find copy-paste duplication.")
    add_common_filter_args(p)
    p.add_argument("--min-lines", type=int, default=5,
                   help="minimum block length to flag (default 5)")
    p.add_argument("--min-chars", type=int, default=8,
                   help="ignore normalized lines shorter than this (default 8)")
    args = p.parse_args(argv)

    root = resolve_root(args.path, "dup_scan")
    exts, ignores = resolve_filters(args.ext, args.ignore, DUP_EXTS)
    report = scan(root, exts, ignores, max(2, args.min_lines), args.min_chars)
    print(json.dumps(report, indent=2, ensure_ascii=False) if args.json else render(report))
    return 0


if __name__ == "__main__":
    run_cli(main)
