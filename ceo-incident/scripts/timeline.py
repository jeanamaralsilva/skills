#!/usr/bin/env python3
"""Builds an incident timeline from local sources, as deterministic Markdown or JSON.

Usage:
  python3 timeline.py [--events .ceo/incidents/AAAA-MM-DD.md] [--repo PATH ...] [--ref REF]
                      [--since AAAA-MM-DD[THH:MM]] [--until ...] [--tz=-03:00] [--json]

Sources:
  - events file: lines the agent writes while handling the incident, one per event:
        - 2026-10-19 14:05 detectado: alerta de erro 500 no login
        - 14:20 mitigado: rollback do servidor para a versão anterior
    A line with only HH:MM takes the date from the file name (AAAA-MM-DD.md). The word before
    ':' is the type when it is one of TYPES; otherwise the type is "nota".
  - git, per --repo: commits on --ref (default HEAD) and tags created in the window.
    Read only: git runs with --no-optional-locks, never fetches.

Window: --since/--until. Without --since, it starts 24 h before the first event.
Naive times use --tz (default Z). Output times are shown in --tz.
Text is untrusted: masked (e-mail, phone, CPF, tokens) and cut. Never executed.

Exit code: 0 ok, 2 bad input.
"""
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import cut, mask, parse_moment, parse_tz, safe_arg  # noqa: E402

TIMEOUT = 30
MAX_TEXT = 160
MAX_COMMITS = 200
LOOKBACK = dt.timedelta(hours=24)
TYPES = ["inicio", "detectado", "declarado", "comunicado", "decisao", "mitigado", "deploy", "ota", "loja",
         "resolvido", "nota"]
MILESTONES = [("detectar", "inicio", "detectado"), ("mitigar", "inicio", "mitigado"), ("resolver", "inicio", "resolvido")]
EVENT_RE = re.compile(
    r"^\s*[-*]\s+(?:(?P<date>\d{4}-\d{2}-\d{2})[ T])?(?P<time>\d{2}:\d{2}(?::\d{2})?)\s*(?P<tz>Z|[+-]\d{2}:?\d{2})?\s+(?P<rest>.+)$"
)
FILE_DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")


def from_git_date(stamp):
    """git prints UTC as 'Z', which datetime.fromisoformat only accepts from Python 3.11."""
    stamp = stamp.strip()
    return dt.datetime.fromisoformat(stamp[:-1] + "+00:00" if stamp.endswith("Z") else stamp)


def run_git(repo, *args):
    cmd = ["git", "--no-optional-locks", "-C", repo, *args]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT, check=False)
    except FileNotFoundError:
        return False, "", "git não encontrado"
    except subprocess.TimeoutExpired:
        return False, "", f"tempo esgotado ({TIMEOUT}s)"
    if proc.returncode != 0:
        last = proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else f"saída {proc.returncode}"
        return False, "", cut(mask(last), MAX_TEXT)
    return True, proc.stdout, ""


def read_events(path, default_tz, warnings):
    match = FILE_DATE_RE.search(os.path.basename(path))
    file_date = match.group(1) if match else None
    events = []
    with open(path, encoding="utf-8", errors="replace") as handle:
        for number, line in enumerate(handle, start=1):
            found = EVENT_RE.match(line)
            if not found:
                continue
            date = found.group("date") or file_date
            if not date:
                warnings.append(f"linha {number} sem data e o nome do arquivo não tem AAAA-MM-DD: ignorada")
                continue
            stamp = f"{date}T{found.group('time')}{found.group('tz') or ''}"
            try:
                moment = parse_moment(stamp, default_tz)
            except ValueError as exc:
                warnings.append(f"linha {number}: {exc}")
                continue
            kind, sep, text = found.group("rest").partition(":")
            kind = kind.strip().lower()
            if not sep or kind not in TYPES:
                kind, text = "nota", found.group("rest")
            events.append({"at": moment, "source": "eventos", "type": kind, "text": cut(mask(text.strip()), MAX_TEXT)})
    return events


def read_git(repo, ref, since, until, warnings):
    name = os.path.basename(os.path.abspath(repo)) or repo
    window = [f"--since={since.isoformat()}"] + ([f"--until={until.isoformat()}"] if until else [])
    ok, out, err = run_git(repo, "log", f"--max-count={MAX_COMMITS + 1}", "--format=%h%x1f%cI%x1f%s", *window, ref, "--")
    items = []
    if not ok:
        warnings.append(f"{name}: git log falhou ({err})")
        return items
    lines = [line for line in out.splitlines() if line.strip()]
    if len(lines) > MAX_COMMITS:
        warnings.append(f"{name}: mais de {MAX_COMMITS} commits na janela, mostrando os {MAX_COMMITS} mais novos; estreite --since")
        lines = lines[:MAX_COMMITS]
    for line in lines:
        short, stamp, subject = (line.split("\x1f") + ["", ""])[:3]
        items.append({"at": from_git_date(stamp), "source": f"git:{name}", "type": "commit",
                      "text": cut(mask(f"{short} {subject}"), MAX_TEXT)})
    ok, out, err = run_git(repo, "for-each-ref", "--format=%(refname:short)%09%(creatordate:iso-strict)", "refs/tags")
    if not ok:
        warnings.append(f"{name}: tags não lidas ({err})")
        return items
    for line in out.splitlines():
        tag, _, stamp = line.partition("\t")
        if not stamp:
            continue
        moment = from_git_date(stamp)
        if moment >= since and (until is None or moment <= until):
            items.append({"at": moment, "source": f"git:{name}", "type": "tag", "text": cut(mask(tag), MAX_TEXT)})
    return items


def milestones(events):
    first = {}
    for item in sorted(events, key=lambda e: e["at"]):
        if item["source"] == "eventos" and item["type"] not in first:
            first[item["type"]] = item["at"]
    result = []
    for label, start, end in MILESTONES:
        if start in first and end in first:
            minutes = int((first[end] - first[start]).total_seconds() // 60)
            result.append({"ate": label, "de": start, "para": end, "minutos": minutes})
    return result


def build(args):
    tz = parse_tz(args.tz)
    warnings = []
    events = []
    if args.events:
        if not os.path.isfile(args.events):
            raise ValueError(f"arquivo de eventos não encontrado: {args.events}")
        events = read_events(args.events, tz, warnings)
    since = parse_moment(args.since, tz) if args.since else None
    until = parse_moment(args.until, tz) if args.until else None
    if since is None and events:
        since = min(item["at"] for item in events) - LOOKBACK
    if args.repo and since is None:
        raise ValueError("sem --since e sem eventos: informe --since para ler o git")
    ref = safe_arg(args.ref, "--ref")
    if any(ch.isspace() for ch in ref):
        raise ValueError("--ref inválido: sem espaço")
    items = list(events)
    for repo in args.repo or []:
        safe_arg(repo, "--repo")
        if not os.path.isdir(repo):
            warnings.append(f"repo não encontrado: {os.path.basename(repo)}")
            continue
        items.extend(read_git(repo, ref, since, until, warnings))
    items.sort(key=lambda item: (item["at"].astimezone(dt.timezone.utc), item["source"] != "eventos", item["source"],
                                 item["type"], item["text"]))
    marks = milestones(events)
    items = [dict(item, at=item["at"].astimezone(tz).isoformat(timespec="minutes")) for item in items]
    if not events:
        warnings.append("sem arquivo de eventos: a linha do tempo só tem git; anote detecção, mitigação e resolução")
    return {
        "fuso": args.tz,
        "janela": {"desde": since.astimezone(tz).isoformat(timespec="minutes") if since else None,
                   "ate": until.astimezone(tz).isoformat(timespec="minutes") if until else None},
        "itens": items,
        "marcos": marks,
        "warnings": warnings,
    }


def to_markdown(result):
    lines = [f"# Linha do tempo (fuso {result['fuso']})", ""]
    window = result["janela"]
    lines.append(f"Janela do git: {window['desde'] or 'n/a'} até {window['ate'] or 'agora'}")
    lines.append("")
    lines.append("| Quando | Fonte | Tipo | O quê |")
    lines.append("|---|---|---|---|")
    for item in result["itens"]:
        when = item["at"][:16].replace("T", " ")
        text = item["text"].replace("|", "\\|")
        lines.append(f"| {when} | {item['source']} | {item['type']} | {text} |")
    if result["marcos"]:
        lines.extend(["", "Tempos (a partir do primeiro registro de cada tipo):"])
        for mark in result["marcos"]:
            lines.append(f"- até {mark['ate']}: {mark['minutos']} min ({mark['de']} → {mark['para']})")
    if result["warnings"]:
        lines.extend(["", "Avisos:"])
        lines.extend(f"- {w}" for w in result["warnings"])
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Linha do tempo do incidente a partir de fontes locais.")
    parser.add_argument("--events", help="arquivo de eventos, ex.: .ceo/incidents/2026-10-19.md")
    parser.add_argument("--repo", action="append", help="repositório git (pode repetir)")
    parser.add_argument("--ref", default="HEAD", help="ramo ou ref lido no git (padrão HEAD)")
    parser.add_argument("--since", help="início da janela do git")
    parser.add_argument("--until", help="fim da janela do git")
    parser.add_argument("--tz", default="Z", help="fuso para horas sem fuso e para a saída (ex.: -03:00)")
    parser.add_argument("--json", action="store_true", help="saída em JSON")
    args = parser.parse_args(argv)
    if not args.events and not args.repo:
        parser.error("informe --events, --repo ou os dois")
    try:
        result = build(args)
    except ValueError as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        sys.stdout.write(to_markdown(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
