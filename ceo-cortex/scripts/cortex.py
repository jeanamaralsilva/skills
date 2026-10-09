#!/usr/bin/env python3
"""
cortex - a terminal-native memory network for coding agents.

Zero external dependencies (Python 3.8+ standard library only). Stores durable
engineering knowledge - decisions, conventions, patterns, anti-patterns, bugs -
as a small graph in SQLite so that any agent (or human) can recall it across
sessions instead of re-deriving it every time.

Why this exists: large-codebase context does not fit in an LLM's window, which
is the documented root cause of AI code duplication and convention drift. cortex
is the persistent layer that survives the window: write a fact once, recall it
forever, and link related facts into a navigable network.

Quick start:
    cortex remember "Auth tokens live in HttpOnly cookies, never localStorage" \\
        --kind decision --tags auth,security --source PR#412 --confidence 0.95
    cortex search "where do we keep auth tokens"
    cortex link m_1a2b3c4d m_5e6f7a8b --rel supports
    cortex neighbors m_1a2b3c4d --depth 2
    cortex stats

Storage location (first match wins):
    --db PATH  >  $CORTEX_DB  >  $CORTEX_HOME/cortex.db  >  ~/.cortex/cortex.db
Add `--json` to any command for machine-readable output (for agent pipelines).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

# --- Domain vocabulary -------------------------------------------------------
# A small, fixed vocabulary keeps the network semantically meaningful instead of
# degenerating into free-text tags nobody can query. Extend deliberately.
KINDS = (
    "decision",     # a choice that constrains future work ("we use X, not Y")
    "convention",   # a rule the codebase follows (naming, layering, error style)
    "pattern",      # a reusable approach worth repeating
    "antipattern",  # a mistake to avoid (especially recurring AI mistakes)
    "bug",          # a defect + its root cause / fix
    "fact",         # a stable truth about the system or domain
    "glossary",     # a term and its meaning in this project's language
    "todo",         # a deferred action with enough context to resume
    "note",         # catch-all when nothing above fits
)

RELATIONS = (
    "relates",      # generic association
    "supports",     # A is evidence/rationale for B
    "contradicts",  # A conflicts with B (flag for human resolution)
    "duplicates",   # A and B say the same thing (dedupe candidate)
    "depends-on",   # A requires B to hold
    "supersedes",   # A replaces B (B is now stale)
    "refines",      # A is a more specific version of B
)

# Patterns that almost certainly indicate a secret. Refusing to persist these by
# default keeps credentials out of a store that agents read back verbatim.
_SECRET_PATTERNS = (
    re.compile(r"AKIA[0-9A-Z]{16}"),                         # AWS access key id
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),       # PEM private key
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"),             # GitHub token
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}"),           # Slack token
    re.compile(r"(?i)\b(api[_-]?key|secret|passwd|password|token)\b\s*[:=]\s*\S{6,}"),
)

_TOKEN_RE = re.compile(r"[^a-z0-9_]+")


# --- Small helpers -----------------------------------------------------------
def _now() -> str:
    """UTC timestamp in RFC 3339 form (sorts lexicographically by time)."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _new_uid() -> str:
    """Short, stable, human-typable id."""
    return "m_" + uuid.uuid4().hex[:8]


def _tokenize(text: str) -> list[str]:
    return [t for t in _TOKEN_RE.split(text.lower()) if len(t) >= 2]


def _parse_tags(raw: Optional[str]) -> list[str]:
    if not raw:
        return []
    seen: dict[str, None] = {}  # dedupe, preserve order
    for tag in raw.split(","):
        tag = tag.strip().lower()
        if tag:
            seen.setdefault(tag, None)
    return list(seen)


def _find_secret(text: str) -> Optional[str]:
    for pat in _SECRET_PATTERNS:
        m = pat.search(text)
        if m:
            return m.group(0)[:24] + "..."
    return None


class CortexError(Exception):
    """User-facing error: print the message, exit non-zero, no traceback."""


# --- Storage -----------------------------------------------------------------
def resolve_db_path(explicit: Optional[str]) -> Path:
    if explicit:
        return Path(explicit).expanduser()
    if os.environ.get("CORTEX_DB"):
        return Path(os.environ["CORTEX_DB"]).expanduser()
    if os.environ.get("CORTEX_HOME"):
        return Path(os.environ["CORTEX_HOME"]).expanduser() / "cortex.db"
    return Path.home() / ".cortex" / "cortex.db"


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS memories (
            uid        TEXT PRIMARY KEY,
            kind       TEXT NOT NULL,
            text       TEXT NOT NULL,
            tags       TEXT NOT NULL DEFAULT '',
            scope      TEXT NOT NULL DEFAULT 'global',
            source     TEXT NOT NULL DEFAULT '',
            confidence REAL NOT NULL DEFAULT 0.8,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            deleted    INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS links (
            src        TEXT NOT NULL,
            dst        TEXT NOT NULL,
            rel        TEXT NOT NULL,
            created_at TEXT NOT NULL,
            PRIMARY KEY (src, dst, rel),
            FOREIGN KEY (src) REFERENCES memories(uid) ON DELETE CASCADE,
            FOREIGN KEY (dst) REFERENCES memories(uid) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_mem_kind  ON memories(kind);
        CREATE INDEX IF NOT EXISTS idx_mem_scope ON memories(scope);
        CREATE INDEX IF NOT EXISTS idx_link_src  ON links(src);
        CREATE INDEX IF NOT EXISTS idx_link_dst  ON links(dst);
        """
    )
    conn.commit()
    return conn


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    d = dict(row)
    d["tags"] = [t for t in d.get("tags", "").split(",") if t]
    d.pop("deleted", None)
    return d


def _get(conn: sqlite3.Connection, uid: str) -> sqlite3.Row:
    row = conn.execute(
        "SELECT * FROM memories WHERE uid = ? AND deleted = 0", (uid,)
    ).fetchone()
    if row is None:
        raise CortexError(f"no memory with id '{uid}' (use `cortex list` to see ids)")
    return row


def _kind_scope_filter(args: argparse.Namespace) -> tuple[str, list[Any]]:
    """WHERE clause + params for the kind/scope filters shared by search and list."""
    where = ["deleted = 0"]
    params: list[Any] = []
    if args.kind:
        where.append("kind = ?")
        params.append(args.kind)
    if args.scope:
        where.append("scope = ?")
        params.append(args.scope)
    return " AND ".join(where), params


# --- Ranking -----------------------------------------------------------------
def _score(row: sqlite3.Row, query_tokens: list[str], now: datetime) -> float:
    """Keyword relevance with tag, recency and confidence boosts.

    Intentionally NOT semantic-embedding search - this is honest keyword scoring
    with prefix matching, which needs no model and no extra dependency. Tags are
    weighted heavily because they are deliberate, high-signal labels.
    """
    tags = [t for t in row["tags"].split(",") if t]
    doc_tokens = set(_tokenize(row["text"])) | set(tags)
    tag_set = set(tags)

    score = 0.0
    for q in set(query_tokens):
        if q in doc_tokens:
            score += 1.0
        elif any(dt.startswith(q) or q.startswith(dt) for dt in doc_tokens):
            score += 0.5  # partial / prefix (auth ~ authentication)
        if q in tag_set:
            score += 2.0  # exact tag hit dominates

    if score == 0.0 and query_tokens:
        return 0.0

    try:
        age_days = (now - datetime.fromisoformat(row["updated_at"])).days
        score += max(0.0, 1.0 - age_days / 365.0) * 0.5  # fresher ranks higher
    except (ValueError, TypeError):
        pass
    score += float(row["confidence"]) * 0.5
    return score


# --- Commands ----------------------------------------------------------------
def cmd_remember(conn: sqlite3.Connection, args: argparse.Namespace) -> dict[str, Any]:
    text = args.text.strip()
    if not text:
        raise CortexError("refusing to store empty memory")
    if args.kind not in KINDS:
        raise CortexError(f"unknown --kind '{args.kind}'. valid: {', '.join(KINDS)}")

    leaked = _find_secret(text)
    if leaked and not args.force:
        raise CortexError(
            f"text looks like it contains a secret ({leaked}). cortex is read "
            "back verbatim by agents - do not store credentials. Re-run with "
            "--force only if you are certain it is safe."
        )

    if not 0.0 <= args.confidence <= 1.0:
        raise CortexError("--confidence must be between 0.0 and 1.0")

    uid = _new_uid()
    now = _now()
    conn.execute(
        "INSERT INTO memories (uid, kind, text, tags, scope, source, confidence,"
        " created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?)",
        (uid, args.kind, text, ",".join(_parse_tags(args.tags)), args.scope,
         args.source or "", args.confidence, now, now),
    )
    conn.commit()
    return _row_to_dict(_get(conn, uid))


def cmd_recall(conn: sqlite3.Connection, args: argparse.Namespace) -> dict[str, Any]:
    row = _get(conn, args.id)
    out = _row_to_dict(row)
    out["links"] = _links_of(conn, args.id)
    return out


def cmd_search(conn: sqlite3.Connection, args: argparse.Namespace) -> list[dict[str, Any]]:
    clause, params = _kind_scope_filter(args)
    rows = conn.execute(f"SELECT * FROM memories WHERE {clause}", params).fetchall()

    want_tags = set(_parse_tags(args.tags))
    if want_tags:
        rows = [r for r in rows
                if want_tags <= {t for t in r["tags"].split(",") if t}]

    query_tokens = _tokenize(args.query or "")
    now = datetime.now(timezone.utc)
    scored = [(r, _score(r, query_tokens, now)) for r in rows]
    if query_tokens:
        scored = [(r, s) for r, s in scored if s > 0]
    scored.sort(key=lambda rs: (rs[1], rs[0]["updated_at"]), reverse=True)

    results = []
    for row, sc in scored[: args.limit]:
        d = _row_to_dict(row)
        d["score"] = round(sc, 3)
        results.append(d)
    return results


def cmd_list(conn: sqlite3.Connection, args: argparse.Namespace) -> list[dict[str, Any]]:
    clause, params = _kind_scope_filter(args)
    rows = conn.execute(
        f"SELECT * FROM memories WHERE {clause} ORDER BY updated_at DESC LIMIT ?",
        params + [args.limit],
    ).fetchall()
    return [_row_to_dict(r) for r in rows]


def cmd_link(conn: sqlite3.Connection, args: argparse.Namespace) -> dict[str, Any]:
    if args.rel not in RELATIONS:
        raise CortexError(f"unknown --rel '{args.rel}'. valid: {', '.join(RELATIONS)}")
    if args.src == args.dst:
        raise CortexError("cannot link a memory to itself")
    _get(conn, args.src)  # validate both endpoints exist
    _get(conn, args.dst)
    try:
        conn.execute(
            "INSERT INTO links (src, dst, rel, created_at) VALUES (?,?,?,?)",
            (args.src, args.dst, args.rel, _now()),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise CortexError(f"link {args.src} -[{args.rel}]-> {args.dst} already exists")
    return {"src": args.src, "rel": args.rel, "dst": args.dst}


def cmd_unlink(conn: sqlite3.Connection, args: argparse.Namespace) -> dict[str, Any]:
    cur = conn.execute(
        "DELETE FROM links WHERE src = ? AND dst = ? AND rel = ?",
        (args.src, args.dst, args.rel),
    )
    conn.commit()
    if cur.rowcount == 0:
        raise CortexError("no such link to remove")
    return {"removed": {"src": args.src, "rel": args.rel, "dst": args.dst}}


def _links_of(conn: sqlite3.Connection, uid: str) -> list[dict[str, str]]:
    out = []
    for r in conn.execute("SELECT rel, dst FROM links WHERE src = ?", (uid,)):
        out.append({"direction": "out", "rel": r["rel"], "other": r["dst"]})
    for r in conn.execute("SELECT rel, src FROM links WHERE dst = ?", (uid,)):
        out.append({"direction": "in", "rel": r["rel"], "other": r["src"]})
    return out


def cmd_neighbors(conn: sqlite3.Connection, args: argparse.Namespace) -> dict[str, Any]:
    _get(conn, args.id)  # validate root exists
    visited = {args.id: 0}
    frontier = [args.id]
    edges: list[dict[str, str]] = []
    for _ in range(args.depth):
        nxt = []
        for uid in frontier:
            for r in conn.execute(
                "SELECT src, dst, rel FROM links WHERE src = ? OR dst = ?", (uid, uid)
            ):
                edges.append({"src": r["src"], "rel": r["rel"], "dst": r["dst"]})
                for other in (r["src"], r["dst"]):
                    if other not in visited:
                        visited[other] = visited[uid] + 1
                        nxt.append(other)
        frontier = nxt
        if not frontier:
            break

    # dedupe edges, then resolve node previews
    uniq = {(e["src"], e["rel"], e["dst"]): e for e in edges}
    nodes = {}
    for uid in visited:
        row = conn.execute(
            "SELECT uid, kind, text FROM memories WHERE uid = ? AND deleted = 0", (uid,)
        ).fetchone()
        if row:
            nodes[uid] = {"uid": uid, "kind": row["kind"],
                          "text": row["text"], "depth": visited[uid]}
    return {"root": args.id, "nodes": list(nodes.values()),
            "edges": list(uniq.values())}


def cmd_update(conn: sqlite3.Connection, args: argparse.Namespace) -> dict[str, Any]:
    row = _get(conn, args.id)
    sets: list[str] = []
    params: list[Any] = []
    if args.text is not None:
        sets.append("text = ?")
        params.append(args.text.strip())
    if args.confidence is not None:
        if not 0.0 <= args.confidence <= 1.0:
            raise CortexError("--confidence must be between 0.0 and 1.0")
        sets.append("confidence = ?")
        params.append(args.confidence)
    if args.source is not None:
        sets.append("source = ?")
        params.append(args.source)
    if args.add_tags:
        merged = _parse_tags(",".join(
            [t for t in row["tags"].split(",") if t] + [args.add_tags]
        ))
        sets.append("tags = ?")
        params.append(",".join(merged))
    if not sets:
        raise CortexError("nothing to update (pass --text/--confidence/--source/--add-tags)")
    sets.append("updated_at = ?")
    params.append(_now())
    params.append(args.id)
    conn.execute(f"UPDATE memories SET {', '.join(sets)} WHERE uid = ?", params)
    conn.commit()
    return _row_to_dict(_get(conn, args.id))


def cmd_forget(conn: sqlite3.Connection, args: argparse.Namespace) -> dict[str, Any]:
    _get(conn, args.id)
    if args.hard:
        conn.execute("DELETE FROM memories WHERE uid = ?", (args.id,))
    else:
        conn.execute(
            "UPDATE memories SET deleted = 1, updated_at = ? WHERE uid = ?",
            (_now(), args.id),
        )
    conn.commit()
    return {"forgotten": args.id, "hard": bool(args.hard)}


def cmd_stats(conn: sqlite3.Connection, args: argparse.Namespace) -> dict[str, Any]:
    by_kind = {r["kind"]: r["n"] for r in conn.execute(
        "SELECT kind, COUNT(*) n FROM memories WHERE deleted = 0 GROUP BY kind")}
    by_scope = {r["scope"]: r["n"] for r in conn.execute(
        "SELECT scope, COUNT(*) n FROM memories WHERE deleted = 0 GROUP BY scope")}
    total = conn.execute(
        "SELECT COUNT(*) n FROM memories WHERE deleted = 0").fetchone()["n"]
    links = conn.execute("SELECT COUNT(*) n FROM links").fetchone()["n"]
    return {"total": total, "links": links,
            "by_kind": by_kind, "by_scope": by_scope}


def cmd_export(conn: sqlite3.Connection, args: argparse.Namespace) -> Any:
    mems = [_row_to_dict(r) for r in conn.execute(
        "SELECT * FROM memories WHERE deleted = 0 ORDER BY created_at")]
    links = [dict(r) for r in conn.execute(
        "SELECT src, dst, rel, created_at FROM links ORDER BY created_at")]
    return {"memories": mems, "links": links}


# --- Rendering ---------------------------------------------------------------
def _fmt_memory(d: dict[str, Any], compact: bool = False) -> str:
    head = f"{d['uid']}  [{d['kind']}]"
    if "score" in d:
        head += f"  (score {d['score']})"
    tags = " ".join(f"#{t}" for t in d.get("tags", []))
    meta = f"scope={d['scope']} conf={d['confidence']}"
    if d.get("source"):
        meta += f" src={d['source']}"
    lines = [head, f"  {d['text']}"]
    if tags or not compact:
        lines.append(f"  {tags}  {meta}".rstrip())
    if d.get("links"):
        for ln in d["links"]:
            arrow = "->" if ln["direction"] == "out" else "<-"
            lines.append(f"  {arrow} [{ln['rel']}] {ln['other']}")
    return "\n".join(lines)


def render(result: Any, command: str) -> str:
    if isinstance(result, list):
        if not result:
            return "(no matches)"
        return "\n\n".join(_fmt_memory(d, compact=True) for d in result)
    if command == "stats":
        parts = [f"total memories: {result['total']}   links: {result['links']}"]
        if result["by_kind"]:
            parts.append("by kind:  " + ", ".join(
                f"{k}={v}" for k, v in sorted(result["by_kind"].items())))
        if result["by_scope"]:
            parts.append("by scope: " + ", ".join(
                f"{k}={v}" for k, v in sorted(result["by_scope"].items())))
        return "\n".join(parts)
    if command == "neighbors":
        lines = [f"network around {result['root']} ({len(result['nodes'])} nodes, "
                 f"{len(result['edges'])} edges):"]
        for n in sorted(result["nodes"], key=lambda x: x["depth"]):
            indent = "  " * (n["depth"] + 1)
            preview = n["text"][:70] + ("..." if len(n["text"]) > 70 else "")
            lines.append(f"{indent}{n['uid']} [{n['kind']}] {preview}")
        for e in result["edges"]:
            lines.append(f"  {e['src']} -[{e['rel']}]-> {e['dst']}")
        return "\n".join(lines)
    if command == "export":
        return json.dumps(result, indent=2, ensure_ascii=False)
    if isinstance(result, dict) and "uid" in result:
        return _fmt_memory(result)
    return json.dumps(result, indent=2, ensure_ascii=False)


# --- CLI wiring --------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cortex", description="Terminal memory network for coding agents.")
    p.add_argument("--db", help="path to the SQLite store (overrides env vars)")
    p.add_argument("--json", action="store_true",
                   help="emit JSON instead of human-readable text")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("remember", help="store a new memory")
    s.add_argument("text")
    s.add_argument("--kind", default="note", help=f"one of: {', '.join(KINDS)}")
    s.add_argument("--tags", help="comma-separated, e.g. auth,security")
    s.add_argument("--scope", default="global",
                   help="logical bucket, e.g. global or a project name")
    s.add_argument("--source", help="provenance, e.g. PR#412 or src/auth.py:88")
    s.add_argument("--confidence", type=float, default=0.8)
    s.add_argument("--force", action="store_true",
                   help="store even if it looks like a secret")
    s.set_defaults(func=cmd_remember)

    s = sub.add_parser("recall", help="show one memory and its links")
    s.add_argument("id")
    s.set_defaults(func=cmd_recall)

    s = sub.add_parser("search", help="ranked keyword search")
    s.add_argument("query")
    s.add_argument("--kind")
    s.add_argument("--scope")
    s.add_argument("--tags", help="require all of these comma-separated tags")
    s.add_argument("--limit", type=int, default=8)
    s.set_defaults(func=cmd_search)

    s = sub.add_parser("list", help="list recent memories")
    s.add_argument("--kind")
    s.add_argument("--scope")
    s.add_argument("--limit", type=int, default=20)
    s.set_defaults(func=cmd_list)

    s = sub.add_parser("link", help="connect two memories")
    s.add_argument("src")
    s.add_argument("dst")
    s.add_argument("--rel", default="relates", help=f"one of: {', '.join(RELATIONS)}")
    s.set_defaults(func=cmd_link)

    s = sub.add_parser("unlink", help="remove a link")
    s.add_argument("src")
    s.add_argument("dst")
    s.add_argument("--rel", required=True)
    s.set_defaults(func=cmd_unlink)

    s = sub.add_parser("neighbors", help="traverse the network from a memory")
    s.add_argument("id")
    s.add_argument("--depth", type=int, default=1)
    s.set_defaults(func=cmd_neighbors)

    s = sub.add_parser("update", help="edit a memory in place")
    s.add_argument("id")
    s.add_argument("--text")
    s.add_argument("--confidence", type=float)
    s.add_argument("--source")
    s.add_argument("--add-tags", dest="add_tags")
    s.set_defaults(func=cmd_update)

    s = sub.add_parser("forget", help="soft-delete (or --hard delete) a memory")
    s.add_argument("id")
    s.add_argument("--hard", action="store_true")
    s.set_defaults(func=cmd_forget)

    s = sub.add_parser("stats", help="counts by kind/scope and link total")
    s.set_defaults(func=cmd_stats)

    s = sub.add_parser("export", help="dump the whole store as JSON")
    s.set_defaults(func=cmd_export)

    s = sub.add_parser("init", help="create the store if it does not exist")
    s.set_defaults(func=lambda conn, args: {"db": str(resolve_db_path(args.db)),
                                            "status": "ready"})
    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    db_path = resolve_db_path(args.db)
    try:
        conn = connect(db_path)
        try:
            result = args.func(conn, args)
        finally:
            conn.close()
    except CortexError as e:
        print(f"cortex: {e}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(render(result, args.command))
    return 0


if __name__ == "__main__":
    try:
        code = main()
    except BrokenPipeError:
        # Downstream closed the pipe (e.g. `cortex list | head`); exit quietly.
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        code = 0
    sys.exit(code)
