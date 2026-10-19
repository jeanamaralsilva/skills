#!/usr/bin/env python3
"""Checks every skill folder before publishing: frontmatter, size limits and marketplace entries."""
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
DANGEROUS = re.compile(r"\|\s*(ba|z)?sh\b|rm\s+-rf\s+[/~]|\$\((curl|wget)|base64\s+(-d|--decode)|ignore (all|previous|the above) instructions", re.I)
MAX_NAME, MAX_DESCRIPTION, MAX_COMPATIBILITY, MAX_SKILL_LINES = 64, 1024, 500, 500


def frontmatter(text):
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        return None
    fields = {}
    for line in match.group(1).splitlines():
        key, sep, value = line.partition(":")
        if sep and not line.startswith(" "):
            fields[key.strip()] = value.strip().strip('"').strip("'")
    return fields


def main():
    errors = []
    skill_dirs = sorted(p.parent for p in ROOT.glob("*/SKILL.md"))
    for skill in skill_dirs:
        text = (skill / "SKILL.md").read_text(encoding="utf-8")
        fields = frontmatter(text)
        where = f"{skill.name}/SKILL.md"
        if fields is None:
            errors.append(f"{where}: missing YAML frontmatter")
            continue
        name, description = fields.get("name", ""), fields.get("description", "")
        if name != skill.name:
            errors.append(f"{where}: name '{name}' must match the folder name")
        if not NAME_RE.match(name) or len(name) > MAX_NAME:
            errors.append(f"{where}: name must be kebab-case, up to {MAX_NAME} chars")
        if not description or len(description) > MAX_DESCRIPTION:
            errors.append(f"{where}: description must have 1 to {MAX_DESCRIPTION} chars (has {len(description)})")
        if len(fields.get("compatibility", "")) > MAX_COMPATIBILITY:
            errors.append(f"{where}: compatibility over {MAX_COMPATIBILITY} chars")
        if text.count("\n") > MAX_SKILL_LINES:
            errors.append(f"{where}: over {MAX_SKILL_LINES} lines, move detail to references/")
        for ref in re.findall(r"`((?:references|scripts|assets|agents|data)/[\w./-]+)`", text):
            if not (skill / ref).exists():
                errors.append(f"{where}: points to missing file {ref}")
        for data_file in sorted(skill.glob("data/*.csv")):
            with data_file.open(encoding="utf-8") as handle:
                header = next(csv.reader(handle), [])
            if "source" not in header:
                errors.append(f"{skill.name}/data/{data_file.name}: needs a 'source' column")
            with data_file.open(encoding="utf-8") as handle:
                for line_number, line in enumerate(handle, start=1):
                    if DANGEROUS.search(line):
                        errors.append(f"{skill.name}/data/{data_file.name}:{line_number}: pipe-to-shell, destructive command or injected instruction in data")

    marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
    listed = {path.removeprefix("./") for plugin in marketplace["plugins"] for path in plugin["skills"]}
    for skill in skill_dirs:
        if skill.name not in listed:
            errors.append(f".claude-plugin/marketplace.json: {skill.name} is not listed")
    for name in listed - {s.name for s in skill_dirs}:
        errors.append(f".claude-plugin/marketplace.json: {name} has no SKILL.md")

    for error in errors:
        print(f"error: {error}")
    print(f"{len(skill_dirs)} skills checked, {len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
