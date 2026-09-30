#!/usr/bin/env python3
"""Lints a ceo-analytics report for the AI tells the user does not want.

Usage: python lint_report.py report.md [--max-words 350]
       python lint_report.py - <<'EOF' ... EOF    (reads stdin, no file needed)
Exit 0 when clean, 1 when there are findings. Each finding: line, rule, excerpt.

Rules:
  em-dash         the em dash is the easiest tell of generated text
  jargon          filler words in PT and EN (robusto, abrangente, seamless...)
  vague-fix       recommendations with no concrete change ("melhorar a acessibilidade")
  unsourced-number a % or ratio on a line with no [medido]/[fonte:]/[estimado] tag
  no-evidence     a finding bullet ("- **P0..P3**") with no file:line, screen or print
  too-long        report above the word budget
"""
import argparse
import re
import sys

JARGON = [
    "robusto", "robusta", "abrangente", "elegante", "aproveitando", "vale ressaltar",
    "garantindo assim", "mergulhar", "de forma eficiente", "experiência fluida",
    "robust", "comprehensive", "seamless", "leverage", "delve", "cutting-edge",
    "unlock", "elevate", "empower", "game-changer",
]
VAGUE = [
    "melhorar a acessibilidade", "melhorar a usabilidade", "melhorar a experiência",
    "otimizar a interface", "tornar mais intuitivo", "considerar melhorias",
    "improve accessibility", "improve usability", "make it more intuitive",
]
NUMBER = re.compile(r"\d+(?:[.,]\d+)?\s*(?:%|:1\b)")
SOURCE_TAG = re.compile(r"\[(?:medido|fonte:[^\]]+|estimado)\]", re.IGNORECASE)
FINDING = re.compile(r"^\s*[-*]\s+\*\*P[0-3]\b")
EVIDENCE = re.compile(r"(`[^`]+\.(?:tsx?|jsx?|swift|kt|dart|vue|heex|pen)(?::\d+)?`|\[tela:[^\]]+\]|\[print:[^\]]+\])")


def lint(text: str, max_words: int) -> list[tuple[int, str, str]]:
    findings: list[tuple[int, str, str]] = []
    in_code = False
    for number, line in enumerate(text.splitlines(), start=1):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        lower = line.lower()
        excerpt = line.strip()[:80]
        if "—" in line:
            findings.append((number, "em-dash", excerpt))
        for word in JARGON:
            if re.search(rf"\b{re.escape(word)}\b", lower):
                findings.append((number, "jargon", word))
        for phrase in VAGUE:
            if phrase in lower:
                findings.append((number, "vague-fix", phrase))
        if NUMBER.search(line) and not SOURCE_TAG.search(line):
            findings.append((number, "unsourced-number", excerpt))
        if FINDING.match(line) and not EVIDENCE.search(line):
            findings.append((number, "no-evidence", excerpt))
    words = len(re.findall(r"\w+", text))
    if words > max_words:
        findings.append((0, "too-long", f"{words} words > {max_words}"))
    return findings


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report")
    parser.add_argument("--max-words", type=int, default=350)
    args = parser.parse_args(argv)
    if args.report == "-":
        findings = lint(sys.stdin.read(), args.max_words)
    else:
        with open(args.report, encoding="utf-8") as handle:
            findings = lint(handle.read(), args.max_words)
    for line, rule, excerpt in findings:
        print(f"{line}\t{rule}\t{excerpt}")
    if not findings:
        print("clean")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
