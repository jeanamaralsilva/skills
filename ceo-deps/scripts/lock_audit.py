#!/usr/bin/env python3
"""Exact versions from lockfiles, checked against OSV, without installing anything.

Usage: python lock_audit.py <repo> [--query] [--emit osv-batch.json] [--skip-scope @empresa ...] [--json]

Reads mix.lock, bun.lock, package-lock.json (v1 to v3) and pnpm-lock.yaml (top-level entries),
which is what actually ships, not the ranges in the manifest. With --query it asks
api.osv.dev/v1/querybatch about every package@version (Hex, npm). Without network,
it says so, writes the batch with --emit so it can be sent from another machine,
and prints advisory search links: an empty answer is never reported as "clean".
Every package name and version goes to api.osv.dev; `--skip-scope @empresa` (repeatable)
keeps private npm scopes out of the query and of --emit, and the summary says how many were
sent and how many skipped.
Exit 1 when a vulnerability is found, 2 when the check could not run.
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

from _common import git_ignored

OSV_BATCH = "https://api.osv.dev/v1/querybatch"
MIX_ENTRY = re.compile(r'"([\w]+)":\s*\{:hex,\s*:\w+,\s*"([^"]+)"')
# name comes from the value: the key of a nested entry is a path ("@babel/core/semver": ["semver@6.3.0", ...])
BUN_ENTRY = re.compile(r'^\s{4}"[^"]+":\s*\["((?:@[^/"]+/)?[^@"]+)@([^"]+)"', re.M)
PNPM_ENTRY = re.compile(r"^\s{2}'?/?((?:@[^/@']+/)?[^@/'\s]+)@([0-9][^:'(\s]*)'?:", re.M)
ADVISORY_SEARCH = {
    "Hex": "https://github.com/advisories?query=ecosystem%3Aerlang+{name}",
    "npm": "https://github.com/advisories?query=ecosystem%3Anpm+{name}",
}


def read(path: str) -> str:
    try:
        with open(path, encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


def lock_packages(repo: str) -> list[dict]:
    packages: dict[tuple[str, str, str], dict] = {}

    def add(ecosystem, name, version, source):
        if git_ignored(repo, source):
            return
        if version and re.match(r"\d", version):
            packages.setdefault((ecosystem, name, version), {"ecosystem": ecosystem, "name": name, "version": version, "lock": source})

    for name, version in MIX_ENTRY.findall(read(os.path.join(repo, "mix.lock"))):
        add("Hex", name, version, "mix.lock")
    for name, version in BUN_ENTRY.findall(read(os.path.join(repo, "bun.lock"))):
        add("npm", name, version, "bun.lock")
    package_lock = read(os.path.join(repo, "package-lock.json"))
    if package_lock:
        try:
            data = json.loads(package_lock)
        except ValueError:
            data = {}
        for path, meta in data.get("packages", {}).items():
            if path.startswith("node_modules/") and "version" in meta:
                add("npm", path.split("node_modules/")[-1], meta["version"], "package-lock.json")
        if "packages" not in data:  # lockfileVersion 1: nested "dependencies" trees
            pending = list(data.get("dependencies", {}).items())
            while pending:
                name, meta = pending.pop()
                if meta.get("version"):  # bundled or link entries have no version to look up
                    add("npm", name, meta["version"], "package-lock.json")
                pending += meta.get("dependencies", {}).items()
    for name, version in PNPM_ENTRY.findall(read(os.path.join(repo, "pnpm-lock.yaml"))):
        add("npm", name, version, "pnpm-lock.yaml")
    return sorted(packages.values(), key=lambda p: (p["ecosystem"], p["name"], p["version"]))


def split_scopes(packages: list[dict], scopes: list[str]) -> tuple[list[dict], list[dict]]:
    """(sent, skipped): npm packages under a private scope never leave the machine."""
    prefixes = tuple("@" + s.strip().lstrip("@").rstrip("/") + "/" for s in scopes if s.strip())
    skipped = [p for p in packages if prefixes and p["ecosystem"] == "npm" and p["name"].startswith(prefixes)]
    return [p for p in packages if p not in skipped], skipped


def batch(packages: list[dict]) -> dict:
    return {"queries": [{"package": {"name": p["name"], "ecosystem": p["ecosystem"]}, "version": p["version"]} for p in packages]}


def query_osv(packages: list[dict], timeout: int = 30) -> list[dict]:
    """Returns packages with their vuln ids. Raises on network failure."""
    found = []
    for start in range(0, len(packages), 1000):
        chunk = packages[start:start + 1000]
        request = urllib.request.Request(OSV_BATCH, data=json.dumps(batch(chunk)).encode(), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=timeout) as response:
            results = json.load(response).get("results", [])
        for package, result in zip(chunk, results):
            ids = [v["id"] for v in result.get("vulns", [])]
            if ids:
                found.append({**package, "vulns": ids})
    return found


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo")
    parser.add_argument("--query", action="store_true", help="ask api.osv.dev (needs network)")
    parser.add_argument("--emit", help="write the OSV querybatch body to this file")
    parser.add_argument("--skip-scope", action="append", default=[], metavar="@empresa",
                        help="npm scope never sent to OSV nor written by --emit (repeatable)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    packages = lock_packages(args.repo)
    if not packages:
        print("nenhum lockfile suportado (mix.lock, bun.lock, package-lock.json, pnpm-lock.yaml)")
        return 2
    packages, skipped = split_scopes(packages, args.skip_scope)
    if args.emit:
        with open(args.emit, "w", encoding="utf-8") as handle:
            json.dump(batch(packages), handle)
    locks = sorted({p["lock"] for p in packages + skipped})
    summary = (f"{len(packages) + len(skipped)} pacotes com versão exata em {', '.join(locks)} "
               f"({len(packages)} para o OSV, {len(skipped)} pulados por --skip-scope)")
    if not args.query:
        print(summary + ". Rode com --query para consultar o OSV.")
        return 0
    try:
        vulnerable = query_osv(packages)
    except (urllib.error.URLError, OSError, ValueError) as error:
        print(f"{summary}. OSV inacessível ({error}): vulnerabilidades NÃO verificadas.")
        print("Alternativas: rode este script numa máquina com rede, `osv-scanner scan -r .`, `mix hex.audit`, `bun audit`,")
        print("ou confira à mão: " + ", ".join(sorted({u.split("+{")[0] for u in ADVISORY_SEARCH.values()})))
        return 2
    if args.json:
        print(json.dumps({"checked": len(packages), "skipped": len(skipped), "vulnerable": vulnerable}, indent=2))
    else:
        print(summary + f"; {len(vulnerable)} com advisory no OSV")
        for item in vulnerable:
            print(f"! {item['ecosystem']} {item['name']}@{item['version']} ({item['lock']}): {', '.join(item['vulns'][:6])}")
    return 1 if vulnerable else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
