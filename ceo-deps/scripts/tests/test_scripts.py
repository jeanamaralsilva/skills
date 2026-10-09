import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, SCRIPTS)

import deps_scan  # noqa: E402
import detect_stack  # noqa: E402
import expo_check  # noqa: E402
import lint_report  # noqa: E402
import search  # noqa: E402

BUNDLED = {"expo-router": "~57.0.25", "@expo/ui": "~57.0.22", "@shopify/flash-list": "2.0.2", "react-native-screens": "~4.26.0"}


def write(root, rel, content):
    path = os.path.join(str(root), *rel.split("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content if isinstance(content, str) else json.dumps(content))
    return path


def expo_app(root, expo="57.0.4"):
    write(root, "package.json", {"dependencies": {
        "expo": f"~{expo}", "expo-router": "~57.0.4", "@expo/ui": "~57.0.4", "@shopify/flash-list": "2.3.2",
        "react-native-screens": "~4.26.0", "axios": "^1.7.0", "dayjs": "^1", "moment": "^2"}})
    write(root, "node_modules/expo/package.json", {"name": "expo", "version": expo})
    write(root, "node_modules/expo/bundledNativeModules.json", BUNDLED)
    write(root, "node_modules/expo-router/package.json", {"name": "expo-router", "version": "57.0.4", "license": "MIT"})
    write(root, "node_modules/@expo/ui/package.json", {"name": "@expo/ui", "version": "57.0.4", "license": "MIT"})
    write(root, "node_modules/expo-widgets/package.json", {"name": "expo-widgets", "version": "1.0.0", "license": "MIT"})
    write(root, "node_modules/expo-widgets/node_modules/@expo/ui/package.json", {"name": "@expo/ui", "version": "57.0.18"})
    write(root, "node_modules/@shopify/flash-list/package.json", {"name": "@shopify/flash-list", "version": "2.3.2", "license": "MIT"})
    write(root, "node_modules/react-native-screens/package.json", {"name": "react-native-screens", "version": "4.26.1", "license": "MIT"})
    write(root, "node_modules/gpl-lib/package.json", {"name": "gpl-lib", "version": "1.0.0", "license": "GPL-3.0-only"})
    return str(root)


def test_satisfies_tilde_caret_and_exact():
    assert expo_check.satisfies("57.0.30", "~57.0.22")
    assert not expo_check.satisfies("57.0.4", "~57.0.22")
    assert not expo_check.satisfies("57.1.0", "~57.0.22")
    assert expo_check.satisfies("1.9.0", "^1.2.0") and not expo_check.satisfies("2.0.0", "^1.2.0")
    assert not expo_check.satisfies("2.3.2", "2.0.2")


def test_expo_check_reproduces_the_doctor_screenshot(tmp_path):
    result = expo_check.check(expo_app(tmp_path), None)
    kinds = {m["package"]: m["kind"] for m in result["mismatches"]}
    assert kinds == {"expo-router": "patch", "@expo/ui": "patch", "@shopify/flash-list": "minor"}
    assert set(result["duplicates"]) == {"@expo/ui"}
    assert sorted(v for v, _ in result["duplicates"]["@expo/ui"]) == ["57.0.18", "57.0.4"]
    assert result["hermes_v1_regression_risk"] is True


def test_expo_check_clean_after_fix(tmp_path):
    root = expo_app(tmp_path, expo="57.0.27")
    for name, version in (("expo-router", "57.0.25"), ("@expo/ui", "57.0.22"), ("@shopify/flash-list", "2.0.2")):
        write(root, f"node_modules/{name}/package.json", {"name": name, "version": version})
    os.remove(os.path.join(root, "node_modules", "expo-widgets", "node_modules", "@expo", "ui", "package.json"))
    result = expo_check.check(root, None)
    assert result["mismatches"] == [] and result["duplicates"] == {} and not result["hermes_v1_regression_risk"]


def test_expo_check_exit_2_without_bundled_source(tmp_path):
    write(tmp_path, "package.json", {"dependencies": {"expo": "~57.0.4"}})
    code = subprocess.run([sys.executable, os.path.join(SCRIPTS, "expo_check.py"), str(tmp_path)], capture_output=True).returncode
    assert code == 2


def test_detect_stack_multi_repo_findings(tmp_path):
    mobile, server = tmp_path / "mobile", tmp_path / "server"
    write(mobile, "package.json", {"dependencies": {"expo": "~57.0.4", "lib": "github:org/lib"}, "overrides": {"x": "1"}})
    write(mobile, "package-lock.json", "{}")
    write(mobile, "bun.lock", "{}")
    write(server, "mix.exs", 'def project, do: [elixir: "~> 1.15"]\n defp deps, do: [{:phoenix, "~> 1.8.3"}, {:heroicons, github: "tailwindlabs/heroicons", tag: "v2.2.0"}]')
    reports = [detect_stack.inventory(str(mobile)), detect_stack.inventory(str(server))]
    mobile_findings, server_findings = " | ".join(reports[0]["findings"]), " | ".join(reports[1]["findings"])
    assert "mais de um gerenciador" in mobile_findings and "github:org/lib" not in mobile_findings
    assert "lib" in mobile_findings and "overrides" in mobile_findings and "Node não está fixado" in mobile_findings
    assert "sem mix.lock" in server_findings and ":heroicons presa por tag" in server_findings
    assert reports[1]["elixir"][0]["elixir_requirement"] == "~> 1.15"
    assert reports[0]["javascript"][0]["expo"] == "~57.0.4"


def test_deps_scan_coupling_duplicates_unused_and_license(tmp_path):
    root = expo_app(tmp_path)
    for i in range(3):
        write(root, f"src/api/c{i}.ts", "import axios from 'axios'\nimport { Router } from 'expo-router'\n")
    write(root, "src/date.ts", "const m = require('moment')\n")
    write(root, "src/__tests__/a.test.ts", "import axios from 'axios'\n")
    write(root, "app.config.ts", "export default { plugins: ['dayjs-plugin-fake'] }\n")
    result = deps_scan.scan(root, spread=3, context="mobile")
    assert any(c["dep"] == "axios" and c["files"] == 3 for c in result["coupling"])
    assert any(d["group"] == "datas" and d["packages"] == ["dayjs", "moment"] for d in result["duplicates"])
    unused = {u["dep"] for u in result["unused"]}
    assert "dayjs" in unused and "moment" not in unused and "expo-router" not in unused
    assert not any(c["dep"] == "expo-router" for c in result["coupling"])
    assert result["licenses"]["gpl-lib"]["verdict"] == "deny"
    assert result["licenses"]["expo-router"]["verdict"] == "allow"


def test_deps_scan_elixir_usage_and_hex_license(tmp_path):
    write(tmp_path, "mix.exs", 'defp deps, do: [{:phoenix, "~> 1.8"}, {:req, "~> 0.5"}, {:tesla, "~> 1.0"}, {:bcrypt_elixir, "~> 3.0"}, {:credo, "~> 1.7", only: [:dev, :test]}, {:nimble_csv, "~> 1.2"}, {:sweet_xml, "~> 0.7"}]')
    for i in range(2):
        write(tmp_path, f"lib/app/client{i}.ex", "defmodule App.C do\n  def get, do: Req.get!(\"x\")\nend\n")
    write(tmp_path, "lib/app/accounts.ex", "defmodule App.Accounts do\n  def h(p), do: Bcrypt.hash_pwd_salt(p)\nend\n")
    write(tmp_path, "lib/app/export.ex", "defmodule App.Export do\n  NimbleCSV.define(P, [])\nend\n")
    write(tmp_path, "test/app/client_test.exs", "Req.get!(\"x\")\n")
    write(tmp_path, "deps/req/hex_metadata.config", '{<<"licenses">>,[<<"Apache-2.0">>]}.\n')
    result = deps_scan.scan(str(tmp_path), spread=2, context="saas")
    assert any(c["dep"] == "req" and c["files"] == 2 for c in result["coupling"])
    assert {u["dep"] for u in result["unused"]} == {"tesla"}
    assert any(d["group"] == "cliente HTTP" for d in result["duplicates"])
    assert result["licenses"]["req"] == {"license": "Apache-2.0", "verdict": "allow"}


def test_license_or_expression_takes_most_permissive():
    policy = {row["spdx"]: row for row in deps_scan.load_csv("licenses.csv")}
    assert deps_scan.classify("(MIT OR GPL-3.0-only)", policy, "mobile") == "allow"
    assert deps_scan.classify("AGPL-3.0-only", policy, "saas") == "deny"
    assert deps_scan.classify("Some-Custom-License", policy, "saas") == "review"


def test_lint_report_reads_stdin():
    result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "lint_report.py"), "-"],
                            input="Tudo alinhado ao SDK.\n", capture_output=True, text=True)
    assert result.returncode == 0
    assert lint_report.lint("Ficou robusto — ok\n", 350)


def test_data_csvs_are_well_formed_and_sourced():
    data_dir = os.path.join(SCRIPTS, "..", "data")
    for domain in search.DOMAINS:
        rows = search.load_rows(data_dir, [domain])
        assert rows, f"{domain}.csv missing or empty"
        ids = [row["id"] for _, row in rows]
        assert len(ids) == len(set(ids))
        for _, row in rows:
            assert None not in row and all(v != "" for v in row.values()), row
            assert row["source"].startswith("https://"), row["id"]


def test_every_file_cited_in_skill_md_exists():
    import re
    skill_root = os.path.join(SCRIPTS, "..")
    skill_md = open(os.path.join(skill_root, "SKILL.md"), encoding="utf-8").read()
    cited = set(re.findall(r"`((?:references|agents|assets|scripts|data)/[\w./-]+)`", skill_md))
    assert cited
    assert [p for p in cited if not os.path.exists(os.path.join(skill_root, p))] == []


def test_lint_accepts_dependency_evidence():
    text = (
        "- **P1** Dois lockfiles (bun e npm) → manter só o bun `package.json:5`\n"
        "- **P2** heroicons por tag → usar ref com SHA `mix.exs:72`\n"
        "- **P1** 25 pacotes fora do SDK [cmd: npx expo install --check] → rodar --fix [cmd: npx expo-doctor]\n"
    )
    assert lint_report.lint(text, 400) == []


import lock_audit  # noqa: E402

MIX_LOCK = '''%{
  "bandit": {:hex, :bandit, "1.10.3", "abc", [:mix], [], "hexpm", "def"},
  "req": {:hex, :req, "0.5.17", "abc", [:mix], [], "hexpm", "def"},
  "heroicons": {:git, "https://github.com/tailwindlabs/heroicons.git", "0435d4ca", [tag: "v2.2.0"]},
}
'''
BUN_LOCK = '''{
  "lockfileVersion": 1,
  "packages": {
    "@expo/ui": ["@expo/ui@57.0.4", "", {}, "sha512-x"],
    "axios": ["axios@1.14.1", "", {}, "sha512-y"],
  }
}
'''


def test_lock_audit_reads_exact_versions_and_skips_gitignored(tmp_path):
    write(tmp_path, "mix.lock", MIX_LOCK)
    write(tmp_path, "bun.lock", BUN_LOCK)
    write(tmp_path, "package-lock.json", {"packages": {"node_modules/left-pad": {"version": "1.0.0"}}})
    write(tmp_path, ".gitignore", "# npm lock is not tracked\npackage-lock.json\n")
    found = {(p["ecosystem"], p["name"], p["version"]) for p in lock_audit.lock_packages(str(tmp_path))}
    assert found == {("Hex", "bandit", "1.10.3"), ("Hex", "req", "0.5.17"), ("npm", "@expo/ui", "57.0.4"), ("npm", "axios", "1.14.1")}


def test_lock_audit_query_reports_vulns(monkeypatch):
    class Response:
        def __init__(self, payload):
            self.payload = payload
        def __enter__(self):
            return self
        def __exit__(self, *exc):
            return False
        def read(self):
            return json.dumps(self.payload).encode()

    def fake_urlopen(request, timeout):
        queries = json.loads(request.data)["queries"]
        return Response({"results": [{"vulns": [{"id": "GHSA-655f-mp8p-96gv"}]} if q["package"]["name"] == "req" else {} for q in queries]})

    monkeypatch.setattr(lock_audit.urllib.request, "urlopen", fake_urlopen)
    packages = [{"ecosystem": "Hex", "name": "req", "version": "0.5.17", "lock": "mix.lock"},
                {"ecosystem": "Hex", "name": "jason", "version": "1.4.4", "lock": "mix.lock"}]
    assert lock_audit.query_osv(packages) == [{**packages[0], "vulns": ["GHSA-655f-mp8p-96gv"]}]


def test_lock_audit_without_network_is_not_clean(tmp_path, monkeypatch):
    write(tmp_path, "mix.lock", MIX_LOCK)
    def offline(*args, **kwargs):
        raise lock_audit.urllib.error.URLError("blocked")
    monkeypatch.setattr(lock_audit.urllib.request, "urlopen", offline)
    assert lock_audit.main([str(tmp_path), "--query"]) == 2


def test_detect_stack_flags_gitignored_lock_and_sdk_runtime_policy(tmp_path):
    write(tmp_path, "package.json", {"dependencies": {"expo": "~57.0.27"}})
    write(tmp_path, "bun.lock", "{}")
    write(tmp_path, "package-lock.json", "{}")
    write(tmp_path, ".gitignore", "package-lock.json\n")
    write(tmp_path, "app.config.ts", 'export default { runtimeVersion: { policy: "sdkVersion" } }')
    report = detect_stack.inventory(str(tmp_path))
    findings = " | ".join(report["findings"])
    assert report["lockfiles"] == ["bun.lock"] and report["ignored_lockfiles"] == ["package-lock.json"]
    assert "mais de um gerenciador" not in findings
    assert "está no .gitignore" in findings and "policy sdkVersion" in findings
