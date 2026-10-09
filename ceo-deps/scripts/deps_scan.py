#!/usr/bin/env python3
"""Coupling, functional duplication, unused candidates and licenses for JS and Elixir projects.

Usage: python deps_scan.py <project> [--json] [--spread 10] [--context saas|mobile]

coupling     how many source files touch each dependency. A third-party lib used in
             many files is hard to swap; it should sit behind one wrapper module
             (Adapter / Iron Law 20 of phxagents).
duplicates   two packages from the same functional group (two HTTP clients, two date
             libs...) declared together. Groups come from data/functional-groups.csv.
unused       declared dependencies with zero references in source. Candidates only:
             CLIs, presets and libraries another lib loads at runtime (sweet_xml for
             ExAws, hackney for Swoosh) have no import of their own. Expo config
             plugins named in app.json/app.config.* count as used. Confirm with
             `npx knip` or `mix deps.unlock --check-unused` before removing anything.
licenses     license of every installed package (node_modules/*/package.json or
             deps/*/hex_metadata.config) classified by data/licenses.csv for the
             chosen context. Exit 1 when a package is classified deny.
"""
import argparse
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
SKIP_DIRS = {"node_modules", ".git", "deps", "_build", "build", "dist", ".expo", "ios", "android", "coverage", "priv"}
JS_EXT = (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs")
JS_IMPORT = re.compile(r"""(?:from\s+|require\(\s*|import\(\s*|import\s+)["']((?:@[\w.-]+/)?[\w.-]+)""")
CONFIG_ONLY = re.compile(r"^(@types/|@babel/|babel-|eslint|@eslint/|prettier|typescript$|jest|@testing-library/|ts-|tsx$|@tsconfig/|patch-package|husky|lint-staged|expo-dev-client$|expo-build-properties$|@expo/config-plugins$|react-native-svg-transformer$)")
ELIXIR_MODULES = {
    "phoenix_live_view": ["Phoenix.LiveView", "Phoenix.Component"], "phoenix_ecto": ["Phoenix.Ecto"],
    "phoenix_html": ["Phoenix.HTML"], "phoenix_live_dashboard": ["Phoenix.LiveDashboard"],
    "ecto_sql": ["Ecto.Adapters.SQL", "Ecto.Migration", "Ecto.Query"], "bcrypt_elixir": ["Bcrypt"],
    "argon2_elixir": ["Argon2"], "cors_plug": ["CORSPlug"], "ex_aws": ["ExAws"], "ex_aws_s3": ["ExAws.S3"],
    "telemetry_metrics": ["Telemetry.Metrics"], "telemetry_poller": [":telemetry_poller"],
    "httpoison": ["HTTPoison"], "dns_cluster": ["DNSCluster"], "lazy_html": ["LazyHTML"],
    "nimble_csv": ["NimbleCSV"], "oban_web": ["Oban.Web"], "waffle_ecto": ["Waffle.Ecto"], "ex_machina": ["ExMachina"],
    "phoenix_live_reload": ["Phoenix.LiveReloader", "live_reload"], "plug_attack": ["PlugAttack"], "sweet_xml": ["SweetXml"],
}
JS_INFRA = re.compile(r"^(react|react-native|react-dom|react-native-web|expo|expo-[\w-]+|@expo/[\w-]+|react-native-safe-area-context|react-native-reanimated|react-native-gesture-handler|react-native-screens|@testing-library/[\w-]+)$")
JS_IMPLICIT = re.compile(r"^(react-native-screens|react-native-worklets|react-native-nitro-modules|react-native-safe-area-context|react-dom|react-native-web|@react-native-firebase/app|react-native-edge-to-edge|expo-[\w-]+)$")
TEST_PATH = re.compile(r"(__tests__|\.test\.|\.spec\.|jest\.setup|/test/|^test/|e2e/)")
ELIXIR_IMPLICIT = {"sweet_xml", "hackney", "certifi", "ssl_verify_fun", "castore", "tzdata", "telemetry", "mime", "decimal"}
APP_CONFIGS = ("app.json", "app.config.ts", "app.config.js", "app.config.mjs", "babel.config.js", "metro.config.js")
ELIXIR_INFRA = {"oban", "phoenix", "phoenix_live_view", "phoenix_html", "phoenix_ecto", "ecto", "ecto_sql", "postgrex",
                "jason", "gettext", "telemetry_metrics", "telemetry_poller", "plug", "bandit", "plug_cowboy"}
MIX_DEP = re.compile(r"\{:(\w+)\s*,([^{}]*)\}")
HEX_LICENSE = re.compile(r"<<\"licenses\">>\s*,\s*\[(.*?)\]", re.S)


def load_csv(name: str) -> list[dict]:
    path = os.path.join(DATA, name)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def source_files(root: str, ext: tuple[str, ...], subdirs: list[str] | None = None):
    bases = [os.path.join(root, d) for d in subdirs] if subdirs else [root]
    for base in bases:
        for current, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
            for name in files:
                if name.endswith(ext):
                    yield os.path.join(current, name)


def camelize(dep: str) -> str:
    return "".join(part.capitalize() for part in dep.split("_"))


def js_usage(root: str, deps: list[str]) -> dict[str, list[str]]:
    usage = {dep: [] for dep in deps}
    for path in source_files(root, JS_EXT):
        try:
            text = open(path, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for spec in set(JS_IMPORT.findall(text)):
            if spec in usage:
                usage[spec].append(os.path.relpath(path, root))
    return usage


def elixir_usage(root: str, deps: list[str]) -> dict[str, list[str]]:
    patterns = {}
    for dep in deps:
        modules = ELIXIR_MODULES.get(dep, [camelize(dep)])
        alternatives = "|".join(re.escape(m) for m in modules)
        patterns[dep] = re.compile(rf"(?<![\w.])(?:{alternatives})(?![\w])")
    usage = {dep: [] for dep in deps}
    files = list(source_files(root, (".ex", ".exs", ".heex"), ["lib", "config", "test"]))
    for path in files:
        try:
            text = open(path, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for dep, pattern in patterns.items():
            if pattern.search(text):
                usage[dep].append(os.path.relpath(path, root))
    return usage


def js_licenses(root: str) -> dict[str, str]:
    licenses = {}
    modules = os.path.join(root, "node_modules")
    if not os.path.isdir(modules):
        return licenses
    for entry in os.listdir(modules):
        folders = [os.path.join(entry, s) for s in os.listdir(os.path.join(modules, entry))] if entry.startswith("@") else [entry]
        for folder in folders:
            try:
                data = json.load(open(os.path.join(modules, folder, "package.json"), encoding="utf-8"))
            except (OSError, ValueError):
                continue
            value = data.get("license") or data.get("licenses") or "NOASSERTION"
            if isinstance(value, list):
                value = " OR ".join(v.get("type", "?") if isinstance(v, dict) else str(v) for v in value)
            elif isinstance(value, dict):
                value = value.get("type", "NOASSERTION")
            licenses[data.get("name", folder)] = str(value)
    return licenses


def hex_licenses(root: str) -> dict[str, str]:
    licenses = {}
    deps_dir = os.path.join(root, "deps")
    if not os.path.isdir(deps_dir):
        return licenses
    for dep in os.listdir(deps_dir):
        meta = os.path.join(deps_dir, dep, "hex_metadata.config")
        if not os.path.isfile(meta):
            continue
        match = HEX_LICENSE.search(open(meta, encoding="utf-8", errors="ignore").read())
        names = re.findall(r"<<\"([^\"]+)\">>", match.group(1)) if match else []
        licenses[dep] = " OR ".join(names) or "NOASSERTION"
    return licenses


def classify(license_expr: str, policy: dict[str, dict], context: str) -> str:
    """Most permissive option of an OR expression wins; unknown ids are review."""
    column = "saas_policy" if context == "saas" else "mobile_policy"
    rank = {"allow": 0, "review": 1, "deny": 2}
    options = [o.strip(" ()") for o in re.split(r"\s+OR\s+|/", license_expr) if o.strip(" ()")]
    verdicts = []
    for option in options or ["NOASSERTION"]:
        row = policy.get(option) or policy.get(option.replace(" ", "-"))
        verdicts.append(row[column] if row else "review")
    return min(verdicts, key=lambda v: rank.get(v, 1))


def scan(root: str, spread: int, context: str) -> dict:
    groups = load_csv("functional-groups.csv")
    policy = {row["spdx"]: row for row in load_csv("licenses.csv")}
    result = {"project": os.path.abspath(root), "ecosystems": [], "coupling": [], "duplicates": [], "unused": [], "licenses": {}}
    package = os.path.join(root, "package.json")
    if os.path.isfile(package):
        data = json.load(open(package, encoding="utf-8"))
        runtime = list(data.get("dependencies", {}))
        dev = list(data.get("devDependencies", {}))
        usage = js_usage(root, runtime + dev)
        config_text = "".join(open(os.path.join(root, c), encoding="utf-8", errors="ignore").read() for c in APP_CONFIGS if os.path.isfile(os.path.join(root, c)))
        for dep in usage:
            if not usage[dep] and (f'"{dep}"' in config_text or f"'{dep}'" in config_text):
                usage[dep].append("(config plugin)")
        result["ecosystems"].append("javascript")
        prod_usage = {d: [f for f in files if not TEST_PATH.search(f)] for d, files in usage.items()}
        result["coupling"] += [{"ecosystem": "javascript", "dep": d, "files": len(f), "examples": sorted(f)[:3]} for d, f in prod_usage.items() if len(f) >= spread and not JS_INFRA.match(d)]
        result["unused"] += [{"ecosystem": "javascript", "dep": d} for d in runtime if not usage[d] and not CONFIG_ONLY.match(d) and not JS_IMPLICIT.match(d)]
        declared = set(runtime + dev)
        for group in (g for g in groups if g["ecosystem"] in ("javascript", "any")):
            hits = sorted(declared & set(group["packages"].split(";")))
            if len(hits) > 1:
                result["duplicates"].append({"group": group["group"], "packages": hits, "hint": group["keep_hint"]})
        result["licenses"].update({k: {"license": v, "verdict": classify(v, policy, context)} for k, v in js_licenses(root).items()})
    mix = os.path.join(root, "mix.exs")
    if os.path.isfile(mix):
        tuples = MIX_DEP.findall(open(mix, encoding="utf-8").read())
        deps = sorted({name for name, _ in tuples})
        tooling = {name for name, opts in tuples if "only:" in opts or "runtime: false" in opts}
        usage = elixir_usage(root, deps)
        result["ecosystems"].append("elixir")
        lib_usage = {d: [f for f in files if f.startswith("lib" + os.sep)] for d, files in usage.items()}
        result["coupling"] += [{"ecosystem": "elixir", "dep": d, "files": len(f), "examples": sorted(f)[:3]} for d, f in lib_usage.items() if len(f) >= spread and d not in ELIXIR_INFRA]
        result["unused"] += [{"ecosystem": "elixir", "dep": d} for d in deps if not usage[d] and d not in ELIXIR_INFRA and d not in tooling and d not in ELIXIR_IMPLICIT]
        declared = set(deps)
        for group in (g for g in groups if g["ecosystem"] in ("elixir", "any")):
            hits = sorted(declared & set(group["packages"].split(";")))
            if len(hits) > 1:
                result["duplicates"].append({"group": group["group"], "packages": hits, "hint": group["keep_hint"]})
        result["licenses"].update({k: {"license": v, "verdict": classify(v, policy, context)} for k, v in hex_licenses(root).items()})
    result["coupling"].sort(key=lambda c: -c["files"])
    return result


def render(result: dict, context: str) -> str:
    lines = [f"projeto: {result['project']} ({', '.join(result['ecosystems']) or 'nada detectado'})"]
    for c in result["coupling"]:
        lines.append(f"acoplamento {c['dep']}: {c['files']} arquivos (ex.: {', '.join(c['examples'])})")
    for d in result["duplicates"]:
        lines.append(f"duplicação funcional [{d['group']}]: {', '.join(d['packages'])} -> {d['hint']}")
    if result["unused"]:
        lines.append("sem uso no código (candidatas, confirme com knip/mix): " + ", ".join(u["dep"] for u in result["unused"]))
    if result["licenses"]:
        counts = {}
        for item in result["licenses"].values():
            counts[item["verdict"]] = counts.get(item["verdict"], 0) + 1
        lines.append(f"licenças ({context}): " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
        for name, item in sorted(result["licenses"].items()):
            if item["verdict"] == "deny":
                lines.append(f"! licença bloqueada {name}: {item['license']}")
    else:
        lines.append("licenças: sem node_modules/deps instalados; rode o install ou use osv-scanner --licenses")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--spread", type=int, default=10, help="files touching a lib before it counts as spread coupling")
    parser.add_argument("--context", choices=("saas", "mobile"), default="mobile")
    args = parser.parse_args(argv)
    result = scan(args.project, args.spread, args.context)
    print(json.dumps(result, indent=2, ensure_ascii=False) if args.json else render(result, args.context))
    if not result["ecosystems"]:
        return 2
    return 1 if any(i["verdict"] == "deny" for i in result["licenses"].values()) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
