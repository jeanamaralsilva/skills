#!/usr/bin/env python3
"""
_scan_common - shared helpers for the file-scanning tools (dup_scan, context_map).

Extracted so the two scanners don't duplicate file-walking, ignore rules, and
CLI plumbing - the same DRY principle this skill enforces on reviewed code.
Stdlib only. Imported as a sibling module (the running script's directory is on
sys.path, so `from _scan_common import ...` resolves regardless of cwd).
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Callable

# Directories that are never source worth scanning.
DEFAULT_IGNORES = {
    ".git", "node_modules", "dist", "build", "out", "target", "vendor",
    ".venv", "venv", "__pycache__", ".next", ".nuxt", "coverage", ".idea",
}

# Canonical code-file extensions, shared so the scanners agree on one list.
DEFAULT_CODE_EXTS = (
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".go", ".rs", ".rb",
    ".c", ".cc", ".cpp", ".h", ".hpp", ".cs", ".kt", ".swift", ".php", ".scala",
)


def iter_files(root: Path, exts: set[str], ignores: set[str]):
    """Yield files under root whose suffix is in exts, skipping ignored dirs."""
    if root.is_file():
        if root.suffix in exts:
            yield root
        return
    for path in sorted(root.rglob("*")):
        if path.is_dir() or any(part in ignores for part in path.parts):
            continue
        if path.suffix in exts:
            yield path


def add_common_filter_args(parser: argparse.ArgumentParser) -> None:
    """Register the path / --ext / --ignore / --json options both tools share."""
    parser.add_argument("path", nargs="?", default=".", help="file or directory")
    parser.add_argument("--ext", help="comma-separated extensions, e.g. .py,.ts")
    parser.add_argument("--ignore", help="extra comma-separated dir names to skip")
    parser.add_argument("--json", action="store_true",
                        help="emit JSON instead of human-readable text")


def resolve_root(path_str: str, prog: str) -> Path:
    """Expand and validate the target path, or exit 1 with a clear message."""
    root = Path(path_str).expanduser()
    if not root.exists():
        print(f"{prog}: path not found: {root}", file=sys.stderr)
        raise SystemExit(1)
    return root


def resolve_filters(ext_arg: str | None, ignore_arg: str | None,
                    default_exts: tuple[str, ...]) -> tuple[set[str], set[str]]:
    """Build the (extensions, ignored-dirs) sets from CLI args."""
    exts = ({e if e.startswith(".") else "." + e for e in ext_arg.split(",")}
            if ext_arg else set(default_exts))
    ignores = DEFAULT_IGNORES | (
        {d.strip() for d in ignore_arg.split(",")} if ignore_arg else set())
    return exts, ignores


def run_cli(main_func: Callable[[], int]) -> None:
    """Run a CLI main() and exit, suppressing BrokenPipeError from `| head` etc."""
    try:
        code = main_func()
    except BrokenPipeError:
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        code = 0
    sys.exit(code)
