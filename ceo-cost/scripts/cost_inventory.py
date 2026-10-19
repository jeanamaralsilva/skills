#!/usr/bin/env python3
"""Lists the paid services an app uses, from its code, and matches each one with data/pricing.csv.

Usage: python3 cost_inventory.py <repo> [<repo> ...] [--json] [--max 5]

Reads, without writing anything and without network:
- Dependencies: package.json, mix.exs, requirements*.txt, pyproject.toml.
- Environment variable NAMES: referenced in code (process.env.X, System.get_env("X"),
  os.environ["X"], os.getenv("X")) and listed in .env.example, .env.sample or .env.template.
  Only the part before "=" is read. Real env files (.env, .env.local, .env.production) are
  never opened, and no value is ever printed.
- Config files: eas.json, fly.toml, railway.json/toml, render.yaml, vercel.json, Procfile,
  supabase/config.toml, firebase.json, google-services.json, GoogleService-Info.plist, Dockerfile.
- CI workflows (.github/workflows): macOS runners and cloud builds started by CI.

Output: file:line, service and signal, plus the matching rows of data/pricing.csv and
data/fees.csv with their price date, and "drains" (likely cost leaks) pointing to
data/levers.csv. Folders like node_modules, _build, deps and .git are skipped by their path
relative to the repo root.

Exit code: 0 ok, 2 bad input or nothing scanned.
"""
import argparse
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data")
MAX_FILE_BYTES = 1_000_000
MAX_FILES = 30000

SKIP_DIRS = {
    "node_modules", "_build", "deps", ".git", ".expo", ".next", "dist", "build", "web-build", "coverage",
    "Pods", ".venv", "venv", "__pycache__", ".turbo", ".gradle", "vendor", ".ceo", ".elixir_ls", "cover",
    ".svelte-kit", ".cache", "tmp", ".pytest_cache", "DerivedData",
}
ENV_EXAMPLES = {".env.example", ".env.sample", ".env.template", ".env.dist"}
SECRET_FILE_RE = re.compile(
    r"^\.env|\.(pem|key|p8|p12|pfx|keystore|jks|dump|sqlite3?|db|mobileprovision|cer|crt)$|^id_(rsa|ed25519|ecdsa)|credentials",
    re.I,
)
CODE_EXT = (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".ex", ".exs", ".py", ".toml", ".yml", ".yaml")
DEP_FILES = {"package.json", "mix.exs", "pyproject.toml"}

APP_CONFIGS = ("app.json", "app.config.ts", "app.config.js")

# Services. "rows" says how to find prices: by service name in pricing.csv/fees.csv, or by metric
# for generic signals (a Postgres URL can live on any host).
SERVICES = {
    "Expo EAS": {"deps": ["eas-cli", "expo-updates", "expo-dev-client"], "files": ["eas.json"]},
    "Apple App Store": {"files": ["ios/Podfile"], "env": [r"APPLE_TEAM_ID", r"ASC_\w+", r"APP_STORE_CONNECT\w*"],
                        "content": (APP_CONFIGS, r"\bbundleIdentifier\b")},
    "Google Play": {"files": ["android/app/build.gradle"], "env": [r"GOOGLE_PLAY\w*"],
                    "content": (APP_CONFIGS, r"\bpackage\b\s*\"?\s*[:=]\s*['\"][a-z][\w]*\.")},
    "Compras no app (lojas)": {"deps": ["react-native-iap", "expo-iap", "react-native-purchases", "expo-in-app-purchases"],
                              "fees": ["Apple App Store", "Google Play"]},
    "GitHub Actions": {"files": [".github/workflows/*"]},
    "Fly.io": {"files": ["fly.toml"], "env": [r"FLY_\w+"]},
    "Railway": {"files": ["railway.json", "railway.toml"], "env": [r"RAILWAY_\w+"]},
    "Render": {"files": ["render.yaml"], "env": [r"RENDER_\w+"]},
    "Vercel": {"deps": ["vercel", "@vercel/*"], "files": ["vercel.json"], "env": [r"VERCEL_\w+"]},
    "Heroku": {"files": ["Procfile"], "env": [r"HEROKU_\w+"]},
    "Container (host a definir)": {"files": ["Dockerfile"], "metric": "compute_month"},
    "Postgres gerenciado (host a definir)": {"deps": ["postgrex", "pg", "postgres", "psycopg", "psycopg2", "psycopg2-binary", "@prisma/client"],
                                            "env": [r"DATABASE_URL", r"POSTGRES_\w+", r"PG(HOST|DATABASE|USER)"], "metric": "db_month"},
    "Supabase": {"deps": ["@supabase/supabase-js", "@supabase/*", "supabase"], "files": ["supabase/config.toml"],
                 "env": [r"(EXPO_PUBLIC_|NEXT_PUBLIC_)?SUPABASE_\w+"]},
    "Firebase": {"deps": ["firebase", "@react-native-firebase/*", "firebase-admin", "@firebase/*"],
                 "files": ["firebase.json", "google-services.json", "GoogleService-Info.plist"], "env": [r"FIREBASE_\w+"]},
    "AWS S3": {"deps": ["@aws-sdk/client-s3", "aws-sdk", "ex_aws_s3", "boto3"], "env": [r"AWS_\w+", r"S3_\w+"]},
    "Armazenamento S3 compatível (host a definir)": {"deps": ["ex_aws", "waffle"], "env": [r"STORAGE_(ENDPOINT|BUCKET|REGION)\w*"],
                                                     "metric": "storage_gb"},
    "AWS CloudFront": {"deps": ["@aws-sdk/client-cloudfront"], "env": [r"CLOUDFRONT_\w+", r"CDN_\w+"]},
    "Sentry": {"deps": ["@sentry/*", "sentry-expo", "sentry", "sentry-sdk"], "env": [r"(EXPO_PUBLIC_)?SENTRY_\w+"]},
    "Datadog": {"deps": ["dd-trace", "@datadog/*", "ddtrace"], "env": [r"DD_\w+", r"DATADOG_\w+"]},
    "Anthropic API": {"deps": ["@anthropic-ai/sdk", "anthropic", "anthropix", "@ai-sdk/anthropic"], "env": [r"ANTHROPIC_\w+", r"CLAUDE_API_KEY"],
                      "hosts": ["api.anthropic.com"]},
    "OpenAI API": {"deps": ["openai", "openai_ex", "@ai-sdk/openai"], "env": [r"OPENAI_\w+"], "hosts": ["api.openai.com"]},
    "Gemini API": {"deps": ["@google/genai", "@google/generative-ai", "google-genai", "google-generativeai", "@ai-sdk/google"],
                   "env": [r"GEMINI_\w+", r"GOOGLE_GENERATIVE_AI_\w+"], "hosts": ["generativelanguage.googleapis.com"]},
    "Stripe": {"deps": ["stripe", "@stripe/*", "stripity_stripe"], "env": [r"(EXPO_PUBLIC_)?STRIPE_\w+"]},
    "Mercado Pago": {"deps": ["mercadopago", "@mercadopago/*"], "env": [r"MERCADO_?PAGO_\w+", r"MP_ACCESS_TOKEN", r"MP_PUBLIC_KEY"]},
    "PostHog": {"deps": ["posthog-react-native", "posthog-js", "posthog-node", "posthog"], "env": [r"(EXPO_PUBLIC_)?POSTHOG_\w+"]},
    "RevenueCat": {"deps": ["react-native-purchases"], "env": [r"REVENUECAT_\w+"]},
    "Google Maps Platform": {"env": [r"(EXPO_PUBLIC_)?GOOGLE_MAPS_\w+"]},
    "E-mail transacional": {"deps": ["resend", "@sendgrid/mail", "postmark", "nodemailer", "swoosh", "bamboo"],
                            "env": [r"RESEND_\w+", r"SENDGRID_\w+", r"POSTMARK_\w+", r"MAILGUN_\w+", r"SMTP_\w+"]},
}

ENV_REF_RE = re.compile(
    r"process\.env\.([A-Z][A-Z0-9_]+)|process\.env\[['\"]([A-Z][A-Z0-9_]+)['\"]\]"
    r"|System\.(?:get_env|fetch_env!?)\(\s*\"([A-Z][A-Z0-9_]+)\""
    r"|os\.environ(?:\.get)?[\[(]\s*['\"]([A-Z][A-Z0-9_]+)['\"]|os\.getenv\(\s*['\"]([A-Z][A-Z0-9_]+)['\"]"
    r"|Deno\.env\.get\(\s*['\"]([A-Z][A-Z0-9_]+)['\"]"
)
ENV_LINE_RE = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=")
NPM_DEP_RE = re.compile(r"^\s*\"(@?[a-z0-9][\w.-]*(?:/[\w.-]+)?)\"\s*:")
HEX_DEP_RE = re.compile(r"\{\s*:([a-z][a-z0-9_]*)\s*,")
PY_DEP_RE = re.compile(r"^\s*['\"]?([A-Za-z0-9][A-Za-z0-9_.-]*)\s*(?:\[[^\]]*\])?\s*(?:[<>=!~;'\",]|$)")
MACOS_RE = re.compile(r"runs-on:\s*\[?\s*['\"]?macos", re.I)
EAS_CLOUD_RE = re.compile(r"\beas\s+(build|workflow:run|update)\b|expo/expo-github-action")
LLM_CACHE_RE = re.compile(r"cache_control|prompt_cache_key|cacheControl|cachedContent|cached_content")
HOSTS = [(service, host) for service, spec in SERVICES.items() for host in spec.get("hosts", [])]


def rel(root, path):
    return os.path.relpath(path, root).replace(os.sep, "/")


def load_csv(name):
    path = os.path.join(DATA, name)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as handle:
        return [row for row in csv.DictReader(handle)]


def dep_matches(name, patterns):
    for pattern in patterns:
        if pattern.endswith("/*") and name.startswith(pattern[:-1]):
            return True
        if name == pattern:
            return True
    return False


def file_matches(relpath, patterns):
    for pattern in patterns:
        if pattern.endswith("/*"):
            if relpath.startswith(pattern[:-1]) and relpath.endswith((".yml", ".yaml")):
                return True
        elif relpath == pattern or relpath.endswith("/" + pattern):
            return True
    return False


ENV_PATTERNS = [(service, re.compile(rf"^(?:{p})$")) for service, spec in SERVICES.items() for p in spec.get("env", [])]


def env_service(name):
    for service, pattern in ENV_PATTERNS:
        if pattern.match(name):
            return service
    return None


class Inventory:
    def __init__(self, repos):
        self.repos = repos
        self.files = 0
        self.walked = 0
        self.read_by_repo = {}
        self.cut_at = None
        self.signals = []
        self.seen = set()
        self.macos_runs = []
        self.eas_in_ci = []
        self.llm_cache_seen = False

    def add(self, repo, path, line, service, kind, name):
        key = (repo, rel(repo, path), service, kind, name)
        if key in self.seen:
            return
        self.seen.add(key)
        self.signals.append({"repo": os.path.basename(os.path.abspath(repo)), "arquivo": rel(repo, path), "linha": line,
                             "servico": service, "sinal": kind, "nome": name})

    def walk(self, root):
        for current, dirs, files in os.walk(root):
            relative = os.path.relpath(current, root)
            parts = [] if relative == "." else relative.split(os.sep)
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not os.path.islink(os.path.join(current, d))
                             and not (d.startswith(".") and d not in (".github",)))
            if parts and parts[0] in ("ios", "android") and len(parts) > 1 and parts[1] in ("build", "Pods"):
                continue
            for name in sorted(files):
                path = os.path.join(current, name)
                if os.path.islink(path):
                    continue
                if name in ENV_EXAMPLES:
                    yield path
                    continue
                if SECRET_FILE_RE.search(name) and name not in ("GoogleService-Info.plist", "google-services.json"):
                    continue
                yield path

    def read(self, path):
        try:
            if os.path.getsize(path) > MAX_FILE_BYTES:
                return None
            with open(path, encoding="utf-8", errors="replace") as handle:
                text = handle.read()
        except OSError:
            return None
        self.analyzed = True
        return text

    def scan_file(self, repo, path):
        name = os.path.basename(path)
        relpath = rel(repo, path)
        for service, spec in SERVICES.items():
            if file_matches(relpath, spec.get("files", [])):
                self.analyzed = True
                self.add(repo, path, 1, service, "config", relpath)
        for service, spec in SERVICES.items():
            names, pattern = spec.get("content", ((), None))
            if name in names and relpath == name:
                for number, line in enumerate((self.read(path) or "").splitlines(), start=1):
                    if re.search(pattern, line):
                        self.add(repo, path, number, service, "config", name)
                        break
        if name in ENV_EXAMPLES:
            # Only the variable name before "=" is kept; the value is dropped right here.
            for number, line in enumerate((self.read(path) or "").splitlines(), start=1):
                match = ENV_LINE_RE.match(line)
                if match:
                    service = env_service(match.group(1))
                    if service:
                        self.add(repo, path, number, service, "env", match.group(1))
            return
        if name in ("GoogleService-Info.plist", "google-services.json") or not (name.endswith(CODE_EXT) or name in DEP_FILES
                                                                                 or name.startswith("requirements") or name in ("Procfile", "Dockerfile")):
            return
        text = self.read(path)
        if text is None:
            return
        lines = text.splitlines()
        if name == "package.json":
            self.scan_deps(repo, path, lines, NPM_DEP_RE, section_re=re.compile(r"\"(dev|peer|optional)?[dD]ependencies\"\s*:\s*\{"))
            for number, line in enumerate(lines, start=1):
                if EAS_CLOUD_RE.search(line):
                    self.eas_in_ci.append(f"{rel(repo, path)}:{number}")
        elif name == "mix.exs":
            self.scan_deps(repo, path, lines, HEX_DEP_RE)
        elif name.startswith("requirements") and name.endswith(".txt"):
            self.scan_deps(repo, path, lines, PY_DEP_RE)
        elif name == "pyproject.toml":
            self.scan_deps(repo, path, lines, re.compile(r"^\s*['\"]([A-Za-z0-9][A-Za-z0-9_.-]*)"))
        if relpath.startswith(".github/workflows/"):
            for number, line in enumerate(lines, start=1):
                if MACOS_RE.search(line):
                    self.macos_runs.append(f"{relpath}:{number}")
                if EAS_CLOUD_RE.search(line):
                    self.eas_in_ci.append(f"{relpath}:{number}")
        for number, line in enumerate(lines, start=1):
            for match in ENV_REF_RE.finditer(line):
                var = next(group for group in match.groups() if group)
                service = env_service(var)
                if service:
                    self.add(repo, path, number, service, "env", var)
            for service, host in HOSTS:
                if host in line:
                    self.add(repo, path, number, service, "endpoint", host)
            if LLM_CACHE_RE.search(line):
                self.llm_cache_seen = True

    def scan_deps(self, repo, path, lines, dep_re, section_re=None):
        inside = section_re is None
        for number, line in enumerate(lines, start=1):
            if section_re is not None:
                if section_re.search(line):
                    inside = True
                    continue
                if inside and line.strip().startswith("}"):
                    inside = False
                    continue
            if not inside:
                continue
            for match in dep_re.finditer(line):
                dep = match.group(1)
                for service, spec in SERVICES.items():
                    if dep_matches(dep.lower(), spec.get("deps", [])):
                        self.add(repo, path, number, service, "dependencia", dep)

    def run(self):
        for repo in self.repos:
            self.read_by_repo[repo] = 0
            for path in self.walk(repo):
                if self.walked >= MAX_FILES:
                    self.cut_at = self.cut_at or repo
                    break
                self.walked += 1
                # Only files actually opened or matched by path count as read; a PNG walked past does not.
                self.analyzed = False
                self.scan_file(repo, path)
                if self.analyzed:
                    self.read_by_repo[repo] += 1
                    self.files += 1
        return self

    def result(self):
        pricing, fees, levers = load_csv("pricing.csv"), load_csv("fees.csv"), load_csv("levers.csv")
        services = sorted({s["servico"] for s in self.signals})
        detail = []
        for service in services:
            spec = SERVICES[service]
            if "metric" in spec:
                rows = [r for r in pricing if r.get("metric") == spec["metric"]]
            else:
                rows = [r for r in pricing if r.get("service") == service]
            fee_names = spec.get("fees", [service])
            fee_rows = [r for r in fees if r.get("provider") in fee_names]
            detail.append({
                "servico": service,
                "sinais": [s for s in self.signals if s["servico"] == service],
                "precos": [{k: r.get(k, "") for k in ("service", "plan", "metric", "included", "price_low", "price_high",
                                                       "currency", "unit", "checked_on", "source")} for r in rows],
                "taxas": [{k: r.get(k, "") for k in ("provider", "product", "condition", "fee_pct", "fee_fixed",
                                                      "currency", "checked_on", "source")} for r in fee_rows],
            })
        drains = []
        lever_by_id = {r.get("id"): r for r in levers}

        def drain(lever_id, where, what):
            lever = lever_by_id.get(lever_id, {})
            drains.append({"alavanca": lever_id, "onde": where, "o_que": what,
                           "fonte": lever.get("source", ""), "checked_on": lever.get("checked_on", "")})

        if self.macos_runs:
            drain("CI-LINUX", self.macos_runs[:5], "job de CI em runner macOS (minuto mais caro que Linux)")
        if self.eas_in_ci:
            drain("EAS-GATILHO", sorted(set(self.eas_in_ci))[:5], "build ou update na nuvem disparado por script ou CI: confira em que evento roda")
        llm = [s for s in services if s in ("Anthropic API", "OpenAI API", "Gemini API")]
        if llm and not self.llm_cache_seen:
            drain("IA-CACHE", llm, "SDK de IA sem sinal de prompt caching no código")
        storage = {"AWS S3", "Armazenamento S3 compatível (host a definir)", "Supabase", "Firebase"} & set(services)
        if storage and "AWS CloudFront" not in services:
            drain("CDN", sorted(storage), "arquivos servidos sem CDN detectada no código (pode haver no painel)")
        name = lambda repo: os.path.basename(os.path.abspath(repo))
        return {"arquivos": self.files, "por_repo": {name(r): n for r, n in self.read_by_repo.items()},
                "cortado_em": name(self.cut_at) if self.cut_at else None,
                "nao_verificados": [name(r) for r, n in self.read_by_repo.items() if n == 0],
                "servicos": detail, "ralos": drains}


def render(result, limit):
    out = [f"{result['arquivos']} arquivos lidos. {len(result['servicos'])} serviço(s) com sinal no código.",
           "Só nomes de variáveis: nenhum valor de ambiente foi lido. Preço: reconfira a URL antes de afirmar."]
    if result.get("cortado_em"):
        out.append(f"AVISO: varredura cortada no limite de {MAX_FILES} arquivos, no repo {result['cortado_em']};"
                   " o que vem depois não foi lido.")
    for repo in result.get("nao_verificados", []):
        out.append(f"AVISO: repo {repo} não verificado (0 arquivos lidos); ausência de serviço ali não prova nada.")
    for item in result["servicos"]:
        out.append(f"\n## {item['servico']}")
        for sig in item["sinais"][:limit]:
            out.append(f"- {sig['repo']}/{sig['arquivo']}:{sig['linha']}  {sig['sinal']}: {sig['nome']}")
        if len(item["sinais"]) > limit:
            out.append(f"- ... +{len(item['sinais']) - limit} sinal(is)")
        for row in item["precos"][:limit]:
            price = row["price_low"] if row["price_low"] == row["price_high"] else f"{row['price_low']}-{row['price_high']}"
            out.append(f"  preço: {row['service']} {row['plan']} {row['metric']} incl. {row['included'] or '0'}"
                       f" | {price} {row['currency']}/{row['unit']} | {row['checked_on']} | {row['source']}")
        if len(item["precos"]) > limit:
            out.append(f"  ... +{len(item['precos']) - limit} linha(s) de preço em data/pricing.csv")
        for row in item["taxas"][:limit]:
            fixed = f" + {row['fee_fixed']} {row['currency']}" if row["fee_fixed"] else ""
            out.append(f"  taxa: {row['provider']} {row['product']} ({row['condition']}) {row['fee_pct']}%{fixed}"
                       f" | {row['checked_on']} | {row['source']}")
        if not item["precos"] and not item["taxas"]:
            out.append("  sem linha em data/pricing.csv: consulte a página oficial de preço antes de estimar")
    if result["ralos"]:
        out.append("\n## Possíveis ralos")
        for item in result["ralos"]:
            out.append(f"- [{item['alavanca']}] {item['o_que']}: {', '.join(item['onde'])}")
    return "\n".join(out)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("repos", nargs="+", help="pasta(s) do repo: app, servidor ou monorepo")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--max", type=int, default=5, help="sinais e preços por serviço no texto (padrão 5)")
    args = parser.parse_args(argv)
    for repo in args.repos:
        if repo.startswith("-") or any(ord(ch) < 32 for ch in repo):
            print(f"error: caminho inválido: {repo!r}", file=sys.stderr)
            return 2
        if not os.path.isdir(repo):
            print(f"error: {repo} não é uma pasta", file=sys.stderr)
            return 2
    if args.max < 1:
        print("error: --max precisa ser 1 ou mais", file=sys.stderr)
        return 2
    result = Inventory(args.repos).run().result()
    if result["arquivos"] == 0:
        print("error: 0 arquivos varridos; confira o caminho (pastas como node_modules e _build são ignoradas)", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else render(result, args.max))
    return 0


if __name__ == "__main__":
    sys.exit(main())
