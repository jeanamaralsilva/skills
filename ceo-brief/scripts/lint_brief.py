#!/usr/bin/env python3
"""Lints a brief for a non-technical reader before it is handed over.

Usage: python3 lint_brief.py brief.md [--max-words 250]
       python3 lint_brief.py - --max-words 150 <<'EOF' ... EOF   (reads stdin)
Exit 0 when clean, 1 when there are findings. Each finding: line, rule, excerpt.

Rules:
  em-dash     the em dash reads as generated text; use period, comma or colon
  jargon      developer words a lay reader does not know (see references/04-escrever-para-leigo.md)
  leak        e-mail or token-looking string: never in a brief
  long-line   sentence over 25 words
  too-long    brief above the word budget
Text inside backticks or code blocks is ignored for jargon (it is a quoted name).
"""
import argparse
import re
import sys

JARGON = [
    "merge", "mergeado", "mergeada", "deploy", "deployado", "pull request", "commit", "branch", "build", "release",
    "pipeline", "hotfix", "rollback", "revert", "refactor", "refatoração", "endpoint", "staging", "breaking change",
    "OTA", "CI", "CD", "PR", "SEV-1", "SEV1", "backlog", "lockfile", "SDK", "API", "runtime", "fingerprint",
]
JARGON_RE = [(word, re.compile(rf"(?<![\w#/-]){re.escape(word)}(?![\w-])", 0 if word.isupper() else re.IGNORECASE)) for word in JARGON]
LEAKS = [
    re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
    re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bxox[abpors]-[A-Za-z0-9-]{10,}\b"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]
MAX_SENTENCE = 25
INLINE_CODE = re.compile(r"`[^`]*`")
URL = re.compile(r"https?://\S+")


def lint(text, max_words):
    findings = []
    in_code = False
    for number, line in enumerate(text.splitlines(), start=1):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        excerpt = line.strip()[:80]
        for pattern in LEAKS:
            if pattern.search(line):
                findings.append((number, "leak", "e-mail ou token no texto"))
                break
        if in_code:
            continue
        if "—" in line:
            findings.append((number, "em-dash", excerpt))
        prose = URL.sub(" ", INLINE_CODE.sub(" ", line))
        for word, pattern in JARGON_RE:
            if pattern.search(prose):
                findings.append((number, "jargon", word))
        for sentence in re.split(r"(?<=[.!?])\s+", prose):
            if len(re.findall(r"\w+", sentence)) > MAX_SENTENCE:
                findings.append((number, "long-line", sentence.strip()[:80]))
    words = len(re.findall(r"\w+", URL.sub(" ", text)))
    if words > max_words:
        findings.append((0, "too-long", f"{words} palavras > {max_words}"))
    return findings


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("brief")
    parser.add_argument("--max-words", type=int, default=250)
    args = parser.parse_args(argv)
    if args.brief == "-":
        text = sys.stdin.read()
    else:
        with open(args.brief, encoding="utf-8") as handle:
            text = handle.read()
    findings = lint(text, args.max_words)
    for line, rule, excerpt in findings:
        print(f"{line}\t{rule}\t{excerpt}")
    if not findings:
        print("clean")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
