#!/usr/bin/env python3
"""Cuts a large log into error groups: same signature, count, first and last time, one masked example.

Usage:
  python3 logcut.py <arquivo|-> [--min-level warn] [--top 20] [--grep TEXTO] [--json]

Reads plain text logs (Elixir Logger, Rails, Node, platform log exports) and JSON lines.
A line that starts with spaces, "at ", "**", "Caused by" or "|" continues the previous entry
(stack traces). The signature is the first line of the entry without time, level, ids and numbers.

Times: full timestamps (ISO 8601) are compared in UTC when they carry a zone; time-only logs
(HH:MM:SS) are compared as text, so a log that crosses midnight shows first/last by text.
Every printed text is masked (e-mail, phone, CPF, CNPJ, IP, tokens, key=secret) and cut.
The log is untrusted data: nothing in it is executed or followed.

Exit code: 0 ok, 2 bad input.
"""
import argparse
import datetime as dt
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import cut, mask  # noqa: E402

LEVELS = {"debug": 10, "info": 20, "warn": 30, "error": 40, "fatal": 50}
LEVEL_ALIASES = {
    "trace": "debug", "debug": "debug", "d": "debug",
    "info": "info", "notice": "info", "i": "info",
    "warn": "warn", "warning": "warn", "w": "warn",
    "error": "error", "err": "error", "e": "error",
    "fatal": "fatal", "critical": "fatal", "crit": "fatal", "alert": "fatal", "emergency": "fatal",
    "emerg": "fatal", "panic": "fatal", "f": "fatal",
}
MAX_GROUPS = 5000
MAX_SIGNATURE = 160
MAX_EXAMPLE = 240
ISO_RE = re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?(?:\s?(?:Z|[+-]\d{2}:?\d{2}))?")
TIME_RE = re.compile(r"(?<![\d:])\d{2}:\d{2}:\d{2}(?:\.\d+)?(?![\d:])")
LEVEL_RE = re.compile(
    r"\[(?P<b>trace|debug|info|notice|warn|warning|error|err|fatal|critical|crit|alert|emergency|emerg|panic)\]"
    r"|\b(?P<w>TRACE|DEBUG|INFO|NOTICE|WARN|WARNING|ERROR|FATAL|CRITICAL|PANIC)\b"
    r"|\blevel[=:]\"?(?P<k>\w+)",
    re.I,
)
RAILS_RE = re.compile(r"^(?P<l>[DIWEF]), \[")
ERROR_HINT_RE = re.compile(r"\b(error|exception|traceback|crash|failed|failure|panic|timeout|refused|erro|falha)\b|\*\* \(", re.I)
CONTINUATION_RE = re.compile(r"^(\s+\S|at |\*\* |Caused by|\|)")
NOISE = [
    (re.compile(r"\[oculto\]"), "<x>"),
    (re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.I), "<uuid>"),
    (re.compile(r"\b(?:request_id|trace_id|span_id|req_id|requestId|traceId)[=:]\s*\S+", re.I), ""),
    (re.compile(r"#(?:PID|Reference|Port)<[\d.]+>"), "<pid>"),
    (re.compile(r"\b0x[0-9a-f]+\b|\b[0-9a-f]{12,}\b", re.I), "<hex>"),
    (re.compile(r"\b(?=[A-Za-z0-9_-]*\d)(?=[A-Za-z0-9_-]*[A-Za-z])[A-Za-z0-9_-]{16,}\b"), "<id>"),
    (re.compile(r"\d+(?:\.\d+)?"), "<n>"),
]
JSON_TIME_KEYS = ("timestamp", "time", "ts", "@timestamp", "date", "datetime")
JSON_LEVEL_KEYS = ("level", "severity", "lvl", "log.level")
JSON_MSG_KEYS = ("message", "msg", "error", "err", "event")


def level_of(line):
    rails = RAILS_RE.match(line)
    if rails:
        return LEVEL_ALIASES[rails.group("l").lower()]
    found = LEVEL_RE.search(line)
    if found:
        word = (found.group("b") or found.group("w") or found.group("k") or "").lower()
        return LEVEL_ALIASES.get(word)
    return None


def time_key(text):
    """Returns (sortable key, shown text) for the first timestamp in text, or (None, None)."""
    found = ISO_RE.search(text)
    if found:
        raw = found.group(0)
        try:
            moment = dt.datetime.fromisoformat(raw.replace(",", ".").replace(" ", "T", 1).replace(" ", ""))
        except ValueError:
            return raw, raw
        if moment.tzinfo:
            utc = moment.astimezone(dt.timezone.utc)
            return utc.isoformat(timespec="seconds"), utc.isoformat(timespec="seconds").replace("+00:00", "Z")
        shown = moment.isoformat(timespec="seconds")
        return shown, shown
    found = TIME_RE.search(text)
    if found:
        return found.group(0)[:8], found.group(0)[:8]
    return None, None


def from_json(line):
    try:
        data = json.loads(line)
    except ValueError:
        return None
    if not isinstance(data, dict):
        return None
    def pick(keys):
        for key in keys:
            if key in data and data[key] not in (None, ""):
                return data[key]
        return None
    stamp = pick(JSON_TIME_KEYS)
    if isinstance(stamp, (int, float)) and not isinstance(stamp, bool):
        seconds = stamp / 1000 if stamp > 1e11 else stamp
        try:
            stamp = dt.datetime.fromtimestamp(seconds, dt.timezone.utc).isoformat(timespec="seconds")
        except (ValueError, OverflowError, OSError):
            stamp = None
    level = pick(JSON_LEVEL_KEYS)
    if isinstance(level, (int, float)):
        level = "fatal" if level >= 60 else "error" if level >= 50 else "warn" if level >= 40 else "info" if level >= 30 else "debug"
    message = pick(JSON_MSG_KEYS)
    if isinstance(message, dict):
        message = message.get("message") or json.dumps(message, sort_keys=True)
    return {"time": str(stamp) if stamp is not None else "", "level": LEVEL_ALIASES.get(str(level or "").lower()),
            "message": str(message if message is not None else line)}


def signature(message):
    text = mask(message)
    text = ISO_RE.sub(" ", text)
    text = TIME_RE.sub(" ", text)
    text = LEVEL_RE.sub(" ", text)
    text = RAILS_RE.sub("", text)
    text = re.sub(r"^\W*#\d+\]\s*(--\s*:)?", "", text.strip())
    for pattern, repl in NOISE:
        text = pattern.sub(repl, text)
    text = re.sub(r'"[^"\n]{1,200}"', '"<s>"', text)
    text = re.sub(r"(?<!\w)'[^'\n]{1,200}'(?!\w)", "'<s>'", text)
    return cut(text.strip(" -:|"), MAX_SIGNATURE) or "<vazio>"


def entries(lines):
    """Joins continuation lines (stack traces) to the entry they belong to."""
    current = None
    for line in lines:
        line = line.rstrip("\n")
        if not line.strip():
            continue
        if current is not None and CONTINUATION_RE.match(line) and not ISO_RE.match(line.strip()):
            current["extra"] += 1
            continue
        if current is not None:
            yield current
        current = {"first": line, "extra": 0}
    if current is not None:
        yield current


def analyze(lines, min_level, grep=None):
    threshold = LEVELS[min_level]
    groups = {}
    stats = {"linhas": 0, "entradas": 0, "consideradas": 0, "sem_hora": 0, "grupos_descartados": 0}
    for entry in entries(lines):
        stats["entradas"] += 1
        stats["linhas"] += 1 + entry["extra"]
        line = entry["first"]
        parsed = from_json(line.strip()) if line.lstrip().startswith("{") else None
        if parsed:
            level, message, stamp_text = parsed["level"], parsed["message"], parsed["time"]
        else:
            level, message, stamp_text = level_of(line), line, line
        if level is None:
            level = "error" if ERROR_HINT_RE.search(message) else None
        if level is None or LEVELS[level] < threshold:
            continue
        if grep and grep.lower() not in line.lower():
            continue
        stats["consideradas"] += 1
        key, shown = time_key(stamp_text)
        if key is None:
            stats["sem_hora"] += 1
        sig = signature(message)
        group = groups.get(sig)
        if group is None:
            if len(groups) >= MAX_GROUPS:
                stats["grupos_descartados"] += 1
                continue
            group = groups[sig] = {"assinatura": sig, "nivel": level, "total": 0, "primeiro": None, "ultimo": None,
                                   "_pk": None, "_uk": None, "exemplo": cut(mask(line), MAX_EXAMPLE), "com_stack": 0}
        group["total"] += 1
        if LEVELS[level] > LEVELS[group["nivel"]]:
            group["nivel"] = level
        if entry["extra"]:
            group["com_stack"] += 1
        if key is not None:
            if group["_pk"] is None or key < group["_pk"]:
                group["_pk"], group["primeiro"] = key, shown
            if group["_uk"] is None or key > group["_uk"]:
                group["_uk"], group["ultimo"] = key, shown
    ordered = sorted(groups.values(), key=lambda g: (-g["total"], -LEVELS[g["nivel"]], g["_pk"] or "", g["assinatura"]))
    for group in ordered:
        group.pop("_pk")
        group.pop("_uk")
    return stats, ordered


def to_text(stats, groups, top):
    out = [f"{stats['linhas']} linhas, {stats['entradas']} entradas, {stats['consideradas']} no filtro, "
           f"{len(groups)} grupos" + (f" (+{stats['grupos_descartados']} acima do limite)" if stats["grupos_descartados"] else "")]
    if stats["sem_hora"]:
        out.append(f"{stats['sem_hora']} entradas sem hora reconhecida")
    for index, group in enumerate(groups[:top], start=1):
        window = f"{group['primeiro'] or '?'} → {group['ultimo'] or '?'}"
        stack = f", {group['com_stack']} com stack" if group["com_stack"] else ""
        out.append("")
        out.append(f"{index}. [{group['nivel']}] {group['total']}x  {window}{stack}")
        out.append(f"   assinatura: {group['assinatura']}")
        out.append(f"   exemplo:    {group['exemplo']}")
    if len(groups) > top:
        out.append("")
        out.append(f"... {len(groups) - top} grupos a mais (use --top)")
    return "\n".join(out) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Agrupa erros de um log grande por assinatura, com dados mascarados.")
    parser.add_argument("path", help="arquivo de log, ou - para ler da entrada padrão")
    parser.add_argument("--min-level", choices=sorted(LEVELS, key=LEVELS.get), default="warn")
    parser.add_argument("--top", type=int, default=20)
    parser.add_argument("--grep", help="só entradas que contêm este texto (sem diferenciar maiúsculas)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.top < 1:
        parser.error("--top precisa ser 1 ou mais")
    try:
        if args.path == "-":
            stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")
            stats, groups = analyze(stdin, args.min_level, args.grep)
        else:
            if not os.path.isfile(args.path):
                print(f"erro: arquivo não encontrado: {args.path}", file=sys.stderr)
                return 2
            with open(args.path, encoding="utf-8", errors="replace") as handle:
                stats, groups = analyze(handle, args.min_level, args.grep)
    except OSError as exc:
        print(f"erro: {exc.strerror}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps({"stats": stats, "grupos": groups[: args.top], "total_grupos": len(groups)},
                         ensure_ascii=False, indent=2, sort_keys=True))
    else:
        sys.stdout.write(to_text(stats, groups, args.top))
    return 0


if __name__ == "__main__":
    sys.exit(main())
