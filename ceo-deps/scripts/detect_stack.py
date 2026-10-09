#!/usr/bin/env python3
"""Inventory of one or more repos before any dependency audit.

Usage: python detect_stack.py <repo> [<repo> ...] [--json]

For each repo it reports: ecosystems (by manifest), package managers and lockfiles
(missing or more than one JS lockfile is a finding), toolchain pins (.nvmrc,
.tool-versions, mise.toml, engines, packageManager), framework versions that drive
compatibility (expo, react-native, phoenix, elixir requirement), git dependencies,
overrides/resolutions, update bots and CI. With several repos it also lists the
ecosystems they share, which is where version skew between server and mobile lives.
"""
import argparse
import json
import os
import re
import sys

from _common import git_ignored

SKIP_DIRS = {"node_modules", ".git", "deps", "_build", "build", "dist", ".expo", "Pods", ".gradle", "vendor", "target"}
MANIFESTS = {
    "package.json": "javascript",
    "mix.exs": "elixir",
    "pubspec.yaml": "dart",
    "pyproject.toml": "python",
    "requirements.txt": "python",
    "go.mod": "go",
    "Cargo.toml": "rust",
    "Gemfile": "ruby",
    "composer.json": "php",
    "build.gradle": "jvm-gradle",
    "build.gradle.kts": "jvm-gradle",
    "pom.xml": "jvm-maven",
    "Package.swift": "swift-spm",
    "Podfile": "swift-cocoapods",
}
JS_LOCKS = {"package-lock.json": "npm", "pnpm-lock.yaml": "pnpm", "yarn.lock": "yarn", "bun.lock": "bun", "bun.lockb": "bun"}
OTHER_LOCKS = {
    "mix.lock": "elixir", "pubspec.lock": "dart", "poetry.lock": "python", "uv.lock": "python",
    "go.sum": "go", "Cargo.lock": "rust", "Gemfile.lock": "ruby", "composer.lock": "php",
    "gradle.lockfile": "jvm-gradle", "Package.resolved": "swift-spm", "Podfile.lock": "swift-cocoapods",
}
TOOLCHAIN_FILES = (".nvmrc", ".node-version", ".tool-versions", "mise.toml", ".mise.toml", ".python-version", ".ruby-version")
BOT_FILES = (".github/dependabot.yml", ".github/dependabot.yaml", "renovate.json", "renovate.json5", ".github/renovate.json", ".renovaterc", ".renovaterc.json")
GIT_SPEC = re.compile(r"^(git\+|git:|github:|https?://github\.com|[\w.-]+/[\w.-]+(#.*)?$)")
MIX_GIT = re.compile(r"\{:(\w+)\s*,[^}]*?\b(github|git):\s*\"([^\"]+)\"([^}]*)\}", re.S)
MIX_ELIXIR = re.compile(r"elixir:\s*\"([^\"]+)\"")
MIX_DEP = re.compile(r"\{:(\w+)\s*,\s*\"([^\"]+)\"")


def find_files(root: str, names) -> list[str]:
    found = []
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not (d.startswith(".") and d != ".github")]
        depth = os.path.relpath(current, root).count(os.sep)
        if depth > 3:
            dirs[:] = []
        for name in files:
            if name in names:
                found.append(os.path.relpath(os.path.join(current, name), root))
    return sorted(found)


def read_json(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return {}


def js_details(root: str, manifest: str) -> dict:
    data = read_json(os.path.join(root, manifest))
    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
    return {
        "manifest": manifest,
        "expo": deps.get("expo"),
        "react-native": deps.get("react-native"),
        "react": deps.get("react"),
        "typescript": deps.get("typescript"),
        "engines": data.get("engines"),
        "packageManager": data.get("packageManager"),
        "overrides": sorted({**data.get("overrides", {}), **data.get("resolutions", {})}),
        "git_deps": sorted(name for name, spec in deps.items() if isinstance(spec, str) and GIT_SPEC.match(spec) and not spec[:1].isdigit()),
        "dependency_count": len(data.get("dependencies", {})),
        "dev_dependency_count": len(data.get("devDependencies", {})),
    }


def mix_details(root: str, manifest: str) -> dict:
    try:
        text = open(os.path.join(root, manifest), encoding="utf-8").read()
    except OSError:
        return {"manifest": manifest}
    elixir = MIX_ELIXIR.search(text)
    deps = dict(MIX_DEP.findall(text))
    git = [{"dep": m.group(1), "source": m.group(3), "pinned_by": "ref" if "ref:" in m.group(4) else ("tag" if "tag:" in m.group(4) else "branch/none")} for m in MIX_GIT.finditer(text)]
    return {
        "manifest": manifest,
        "elixir_requirement": elixir.group(1) if elixir else None,
        "phoenix": deps.get("phoenix"),
        "phoenix_live_view": deps.get("phoenix_live_view"),
        "ecto_sql": deps.get("ecto_sql"),
        "dependency_count": len(deps) + len(git),
        "git_deps": git,
    }


def inventory(root: str) -> dict:
    manifests = find_files(root, set(MANIFESTS))
    all_locks = find_files(root, set(JS_LOCKS) | set(OTHER_LOCKS))
    ignored_locks = [l for l in all_locks if git_ignored(root, l)]
    locks = [l for l in all_locks if l not in ignored_locks]
    ecosystems = sorted({MANIFESTS[os.path.basename(m)] for m in manifests})
    findings = []
    js_projects = []
    for manifest in [m for m in manifests if os.path.basename(m) == "package.json"]:
        folder = os.path.dirname(manifest)
        folder_locks = [l for l in locks if os.path.dirname(l) == folder and os.path.basename(l) in JS_LOCKS]
        details = js_details(root, manifest)
        details["lockfiles"] = folder_locks
        managers = sorted({JS_LOCKS[os.path.basename(l)] for l in folder_locks})
        details["package_managers"] = managers
        if len(managers) > 1:
            findings.append(f"{manifest}: mais de um gerenciador de pacotes ({', '.join(managers)}); escolha um e apague os outros lockfiles")
        if not folder_locks and not folder:
            findings.append(f"{manifest}: sem lockfile commitado; install não é determinístico")
        if details["git_deps"]:
            findings.append(f"{manifest}: dependências por git ({', '.join(details['git_deps'])}); fora do npm audit e sem checksum do registry")
        if details["overrides"]:
            findings.append(f"{manifest}: overrides/resolutions ativos ({', '.join(details['overrides'])}); confirme se ainda são necessários")
        js_projects.append(details)
    mix_projects = [mix_details(root, m) for m in manifests if os.path.basename(m) == "mix.exs"]
    for project in mix_projects:
        if not any(os.path.dirname(l) == os.path.dirname(project["manifest"]) and l.endswith("mix.lock") for l in locks):
            findings.append(f"{project['manifest']}: sem mix.lock commitado")
        for dep in project.get("git_deps", []):
            if dep["pinned_by"] != "ref":
                findings.append(f"{project['manifest']}: dep git :{dep['dep']} presa por {dep['pinned_by']}; prefira ref: com SHA completo")
    for lock in ignored_locks:
        findings.append(f"{lock} existe localmente mas está no .gitignore: quem rodar o outro gerenciador instala versões diferentes do lock oficial")
    for config in ("app.json", "app.config.ts", "app.config.js"):
        text = open(os.path.join(root, config), encoding="utf-8", errors="ignore").read() if os.path.isfile(os.path.join(root, config)) else ""
        if re.search(r"policy[\"']?\s*:\s*[\"']sdkVersion", text):
            findings.append(f"{config}: runtimeVersion com policy sdkVersion; mudança nativa dentro do mesmo SDK não muda o runtime e um update OTA pode chegar a um binário sem o código nativo novo (use fingerprint ou appVersion)")
    toolchain = {name: open(os.path.join(root, name), encoding="utf-8", errors="ignore").read().strip()[:200]
                 for name in TOOLCHAIN_FILES if os.path.isfile(os.path.join(root, name))}
    if "javascript" in ecosystems and not ({".nvmrc", ".node-version", ".tool-versions", "mise.toml", ".mise.toml"} & set(toolchain)) \
            and not any(p.get("engines") for p in js_projects):
        findings.append("Node não está fixado (.nvmrc, .tool-versions, mise.toml ou engines)")
    if "elixir" in ecosystems and not ({".tool-versions", "mise.toml", ".mise.toml"} & set(toolchain)):
        findings.append("Elixir/OTP não estão fixados (.tool-versions ou mise.toml)")
    bots = [b for b in BOT_FILES if os.path.isfile(os.path.join(root, b))]
    if not bots:
        findings.append("sem Dependabot nem Renovate: atualizações e alertas dependem de alguém lembrar")
    workflows_dir = os.path.join(root, ".github", "workflows")
    workflows = sorted(os.listdir(workflows_dir)) if os.path.isdir(workflows_dir) else []
    return {
        "root": os.path.abspath(root),
        "ecosystems": ecosystems,
        "manifests": manifests,
        "lockfiles": locks,
        "ignored_lockfiles": ignored_locks,
        "javascript": js_projects,
        "elixir": mix_projects,
        "toolchain": toolchain,
        "bots": bots,
        "ci_workflows": workflows,
        "findings": findings,
    }


def render(report: dict) -> str:
    lines = [f"# {report['root']}", f"ecossistemas: {', '.join(report['ecosystems']) or 'nenhum'}",
             f"lockfiles: {', '.join(report['lockfiles']) or 'nenhum'}",
             f"toolchain: {', '.join(f'{k}={v}' for k, v in report['toolchain'].items()) or 'não fixado'}",
             f"bots: {', '.join(report['bots']) or 'nenhum'} | CI: {', '.join(report['ci_workflows']) or 'nenhum'}"]
    for js in report["javascript"]:
        lines.append(f"[js] {js['manifest']} expo={js['expo']} rn={js['react-native']} pm={','.join(js['package_managers']) or '-'} deps={js['dependency_count']}+{js['dev_dependency_count']}dev")
    for mix in report["elixir"]:
        lines.append(f"[elixir] {mix['manifest']} elixir={mix.get('elixir_requirement')} phoenix={mix.get('phoenix')} lv={mix.get('phoenix_live_view')} deps={mix.get('dependency_count')}")
    lines += [f"! {f}" for f in report["findings"]]
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("roots", nargs="+")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    reports = [inventory(root) for root in args.roots]
    shared = sorted(set.intersection(*(set(r["ecosystems"]) for r in reports))) if len(reports) > 1 else []
    if args.json:
        print(json.dumps({"repos": reports, "shared_ecosystems": shared}, indent=2, ensure_ascii=False))
    else:
        print("\n\n".join(render(r) for r in reports))
        if len(reports) > 1:
            print(f"\necossistemas em comum: {', '.join(shared) or 'nenhum'}")
    return 0 if any(r["ecosystems"] for r in reports) else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
