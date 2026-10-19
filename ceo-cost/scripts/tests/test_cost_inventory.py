import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import cost_inventory  # noqa: E402

FAKE_SECRET = "sk-live-" + "x" * 30


def write(root, rel, content):
    path = os.path.join(str(root), *rel.split("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content if isinstance(content, str) else json.dumps(content, indent=2))
    return path


def run(*roots):
    return cost_inventory.Inventory([str(r) for r in roots]).run().result()


def services(result):
    return {item["servico"] for item in result["servicos"]}


def mobile_app(root):
    write(root, "package.json", {"name": "app", "dependencies": {"expo": "~54.0.0", "expo-updates": "1.0.0",
                                                                  "@sentry/react-native": "7.0.0",
                                                                  "@supabase/supabase-js": "2.0.0",
                                                                  "@anthropic-ai/sdk": "0.50.0"},
                                 "scripts": {"ship": "eas build --platform all"}})
    write(root, "eas.json", {"build": {"production": {}}})
    write(root, ".env.example", f"EXPO_PUBLIC_SUPABASE_URL=https://example.invalid\nANTHROPIC_API_KEY={FAKE_SECRET}\n")
    write(root, ".env", f"OPENAI_API_KEY={FAKE_SECRET}\n")
    write(root, ".env.production", "STRIPE_SECRET_KEY=nope\n")
    write(root, "src/ai.ts", "const key = process.env.ANTHROPIC_API_KEY;\n")
    write(root, ".github/workflows/ci.yml", "jobs:\n  ios:\n    runs-on: macos-latest\n    steps:\n      - run: eas build -p ios\n")
    write(root, "node_modules/stripe/package.json", {"name": "stripe"})


def server(root):
    write(root, "mix.exs", "defp deps do\n  [\n    {:phoenix, \"~> 1.8\"},\n    {:postgrex, \">= 0.0.0\"},\n"
                           "    {:stripity_stripe, \"~> 3.0\"},\n    {:ex_aws_s3, \"~> 2.0\"}\n  ]\nend\n")
    write(root, "fly.toml", "app = 'x'\n")
    write(root, "Dockerfile", "FROM elixir\n")
    write(root, "config/runtime.exs", "url = System.get_env(\"DATABASE_URL\")\nkey = System.fetch_env!(\"STRIPE_SECRET_KEY\")\n")


def test_detects_services_from_deps_configs_env_and_ci(tmp_path):
    mobile_app(tmp_path / "app")
    server(tmp_path / "api")
    result = run(tmp_path / "app", tmp_path / "api")
    found = services(result)
    for expected in ("Expo EAS", "Sentry", "Supabase", "Anthropic API", "GitHub Actions", "Fly.io", "Stripe",
                     "AWS S3", "Postgres gerenciado (host a definir)", "Container (host a definir)"):
        assert expected in found, expected
    drains = {d["alavanca"] for d in result["ralos"]}
    assert {"CI-LINUX", "EAS-GATILHO", "IA-CACHE"} <= drains


def test_never_reads_real_env_files_nor_prints_values(tmp_path, capsys):
    mobile_app(tmp_path)
    result = run(tmp_path)
    assert "OpenAI API" not in services(result)  # only in .env, which is never opened
    names = [s for item in result["servicos"] for s in item["sinais"]]
    assert all(not s["arquivo"].startswith(".env") or s["arquivo"] == ".env.example" for s in names)
    assert cost_inventory.main([str(tmp_path)]) == 0
    assert cost_inventory.main([str(tmp_path), "--json"]) == 0
    out = capsys.readouterr().out
    assert FAKE_SECRET not in out and "example.invalid" not in out
    assert "ANTHROPIC_API_KEY" in out


def test_signal_has_file_and_line(tmp_path):
    server(tmp_path)
    result = run(tmp_path)
    stripe = next(item for item in result["servicos"] if item["servico"] == "Stripe")
    places = {(s["arquivo"], s["linha"], s["nome"]) for s in stripe["sinais"]}
    assert ("mix.exs", 5, "stripity_stripe") in places
    assert ("config/runtime.exs", 2, "STRIPE_SECRET_KEY") in places


def test_skips_ignored_folders_by_relative_path(tmp_path):
    repo = tmp_path / "build" / "repo"  # "build" above the repo must not hide it
    write(repo, "package.json", {"dependencies": {"@sentry/react-native": "7"}})
    write(repo, "node_modules/openai/package.json", {"dependencies": {"openai": "1"}})
    found = services(run(repo))
    assert "Sentry" in found and "OpenAI API" not in found


def test_dependency_names_only_inside_dependency_blocks(tmp_path):
    write(tmp_path, "package.json", {"name": "stripe", "scripts": {"openai": "node x"}, "dependencies": {"expo": "1"}})
    found = services(run(tmp_path))
    assert "Stripe" not in found and "OpenAI API" not in found


def test_pricing_rows_carry_date_and_source(tmp_path):
    write(tmp_path, "fly.toml", "app='x'\n")
    item = next(i for i in run(tmp_path)["servicos"] if i["servico"] == "Fly.io")
    assert item["precos"], "Fly.io deve ter linhas em data/pricing.csv"
    assert all(r["source"].startswith("https://") and r["checked_on"] for r in item["precos"])


def test_bad_input_and_empty_scan_exit_2(tmp_path, capsys):
    assert cost_inventory.main([str(tmp_path / "nope")]) == 2
    empty = tmp_path / "empty"
    empty.mkdir()
    assert cost_inventory.main([str(empty)]) == 2
    assert "0 arquivos" in capsys.readouterr().err


def test_rejects_dash_path(tmp_path, capsys):
    assert cost_inventory.main(["--", "-repo"]) == 2
    assert "caminho inválido" in capsys.readouterr().err


def test_every_detected_service_has_a_known_spec():
    for service, spec in cost_inventory.SERVICES.items():
        assert spec.get("deps") or spec.get("files") or spec.get("env"), service


def test_store_accounts_from_app_config_and_ai_endpoint(tmp_path):
    write(tmp_path, "app.json", '{\n  "expo": {\n    "ios": {"bundleIdentifier": "com.example.app"},\n'
                                '    "android": {"package": "com.example.app"}\n  }\n}\n')
    write(tmp_path, "google-services.json", {"project_info": {}})
    write(tmp_path, "supabase/functions/ai/index.ts",
          "const url = 'https://generativelanguage.googleapis.com/v1/models';\nconst k = Deno.env.get('GEMINI_API_KEY');\n")
    result = run(tmp_path)
    found = services(result)
    assert {"Apple App Store", "Google Play", "Firebase", "Gemini API"} <= found
    gemini = next(i for i in result["servicos"] if i["servico"] == "Gemini API")
    assert {s["sinal"] for s in gemini["sinais"]} == {"endpoint", "env"}
    assert "IA-CACHE" in {d["alavanca"] for d in result["ralos"]}
    play = next(i for i in result["servicos"] if i["servico"] == "Google Play")
    assert play["taxas"] and all(t["source"].startswith("https://") for t in play["taxas"])


def test_files_count_only_what_was_read_and_png_only_exits_2(tmp_path, capsys):
    for name in ("a.png", "b.png", "c.png"):
        (tmp_path / name).write_bytes(b"\x89PNG")
    assert run(tmp_path)["arquivos"] == 0
    assert cost_inventory.main([str(tmp_path)]) == 2
    assert "0 arquivos" in capsys.readouterr().err
    write(tmp_path, "app.js", "fetch('x')\n")
    assert run(tmp_path)["arquivos"] == 1


def test_max_files_cut_is_reported_and_unread_repo_is_unverified(tmp_path, monkeypatch, capsys):
    first, second = tmp_path / "first", tmp_path / "second"
    for i in range(3):
        write(first, f"f{i}.js", "x\n")
    write(second, "fly.toml", "app='x'\n")
    monkeypatch.setattr(cost_inventory, "MAX_FILES", 2)
    result = run(first, second)
    assert result["cortado_em"] == "first"
    assert result["nao_verificados"] == ["second"]
    assert "Fly.io" not in services(result)
    assert cost_inventory.main([str(first), str(second)]) == 0
    out = capsys.readouterr().out
    assert "cortada" in out and "first" in out and "não verificado" in out and "second" in out
