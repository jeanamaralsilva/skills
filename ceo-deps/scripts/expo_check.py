#!/usr/bin/env python3
"""Offline version of the expo-doctor checks that matter most for dependencies.

Usage: python expo_check.py <project> [--bundled bundledNativeModules.json] [--json]

1. SDK alignment: compares every dependency in package.json with the range the
   installed Expo SDK pins in bundledNativeModules.json (the same source
   `npx expo install --check` uses). Reports minor and patch mismatches.
2. Duplicate native modules: walks node_modules and lists every package from the
   bundled list (or with an expo-module.config.json) installed at more than one path.
3. Hermes V1 regression: expo 55 to 57 below 57.0.9 is flagged, as expo-doctor does.

Without node_modules, pass --bundled with the file fetched from
https://raw.githubusercontent.com/expo/expo/sdk-<N>/packages/expo/bundledNativeModules.json
and the script uses the versions declared in package.json.
Exit 1 when it finds a mismatch, a duplicate or the Hermes case. It does not replace
`npx expo-doctor`; it lets the audit run where installing is not possible.
"""
import argparse
import json
import os
import re
import sys

VERSION = re.compile(r"(\d+)\.(\d+)\.(\d+)")


def parse(version: str):
    match = VERSION.search(version or "")
    return tuple(int(x) for x in match.groups()) if match else None


def satisfies(installed: str, wanted: str) -> bool:
    have, base = parse(installed), parse(wanted)
    if not have or not base:
        return True
    wanted = wanted.strip()
    if wanted.startswith("~"):
        return have[:2] == base[:2] and have >= base
    if wanted.startswith("^"):
        if base[0] == 0:
            return have[:2] == base[:2] and have >= base
        return have[0] == base[0] and have >= base
    if wanted.startswith(">="):
        return have >= base
    return have == base


def mismatch_kind(installed: str, wanted: str) -> str:
    have, base = parse(installed), parse(wanted)
    if not have or not base:
        return "unknown"
    if have[0] != base[0]:
        return "major"
    return "minor" if have[1] != base[1] else "patch"


def read_json(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return {}


def installed_version(project: str, name: str, declared: str) -> str:
    data = read_json(os.path.join(project, "node_modules", name, "package.json"))
    return data.get("version") or declared


def native_copies(project: str, names: set[str]) -> dict[str, list[tuple[str, str]]]:
    """Every installed copy of a native module (nested ones included), keyed by package name."""
    copies: dict[str, list[tuple[str, str]]] = {}
    for current, dirs, files in os.walk(os.path.join(project, "node_modules")):
        dirs[:] = [d for d in dirs if d not in {".bin", ".cache"}]
        parent = os.path.basename(os.path.dirname(current))
        grandparent = os.path.basename(os.path.dirname(os.path.dirname(current)))
        base = os.path.basename(current)
        if parent == "node_modules" and not base.startswith("@"):
            name = base
        elif parent.startswith("@") and grandparent == "node_modules":
            name = f"{parent}/{base}"
        else:
            continue
        if "package.json" not in files:
            continue
        if name in names or "expo-module.config.json" in files:
            version = read_json(os.path.join(current, "package.json")).get("version", "?")
            copies.setdefault(name, []).append((version, os.path.relpath(current, project)))
    return {name: sorted(paths) for name, paths in copies.items() if len(paths) > 1}


def check(project: str, bundled_path: str | None) -> dict:
    package = read_json(os.path.join(project, "package.json"))
    declared = {**package.get("dependencies", {}), **package.get("devDependencies", {})}
    excluded = set(package.get("expo", {}).get("install", {}).get("exclude", []))
    bundled_path = bundled_path or os.path.join(project, "node_modules", "expo", "bundledNativeModules.json")
    bundled = read_json(bundled_path)
    mismatches = []
    for name, wanted in sorted(bundled.items()):
        if name not in declared or name in excluded:
            continue
        have = installed_version(project, name, declared[name])
        if not satisfies(have, wanted):
            mismatches.append({"package": name, "expected": wanted, "found": have, "kind": mismatch_kind(have, wanted)})
    expo_version = installed_version(project, "expo", declared.get("expo", ""))
    expo_parsed = parse(expo_version)
    hermes = bool(expo_parsed and 55 <= expo_parsed[0] <= 57 and expo_parsed < (57, 0, 9))
    duplicates = native_copies(project, set(bundled)) if os.path.isdir(os.path.join(project, "node_modules")) else {}
    return {
        "project": os.path.abspath(project),
        "bundled_source": bundled_path if bundled else None,
        "expo": expo_version,
        "mismatches": mismatches,
        "duplicates": duplicates,
        "hermes_v1_regression_risk": hermes,
        "excluded": sorted(excluded),
        "has_node_modules": os.path.isdir(os.path.join(project, "node_modules")),
    }


def render(result: dict) -> str:
    lines = [f"expo {result['expo']} | fonte das versões: {result['bundled_source'] or 'NÃO ENCONTRADA (passe --bundled)'}"]
    if not result["has_node_modules"]:
        lines.append("sem node_modules: 'encontrado' é o range declarado no package.json e duplicatas nativas não são verificáveis (rode npx expo-doctor depois do install)")
    if result["hermes_v1_regression_risk"]:
        lines.append("! Hermes V1: expo 55-57 abaixo de 57.0.9 tem regressão de memória. Rode: npx expo install expo@^57.0.9 --fix")
    for name, paths in result["duplicates"].items():
        lines.append(f"! duplicata nativa {name}: " + "; ".join(f"{v} em {p}" for v, p in paths) + f" (descubra quem puxa: npm why {name})")
    for m in result["mismatches"]:
        lines.append(f"- {m['kind']:5} {m['package']:32} esperado {m['expected']:10} encontrado {m['found']}")
    if not (result["mismatches"] or result["duplicates"] or result["hermes_v1_regression_risk"]):
        lines.append("ok: alinhado ao SDK, sem duplicata nativa, sem regressão Hermes conhecida")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project")
    parser.add_argument("--bundled")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = check(args.project, args.bundled)
    print(json.dumps(result, indent=2, ensure_ascii=False) if args.json else render(result))
    if not result["bundled_source"]:
        return 2
    return 1 if (result["mismatches"] or result["duplicates"] or result["hermes_v1_regression_risk"]) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
