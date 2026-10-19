import json
import os
import subprocess
import sys

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(tool, *args, env=None):
    result = subprocess.run([sys.executable, os.path.join(SCRIPTS, tool), *args],
                            capture_output=True, text=True, env={**os.environ, **(env or {})})
    return result


def test_dup_scan_finds_copied_block(tmp_path):
    block = "".join(f"    total = total + item.value * {i}\n" for i in range(8))
    for name in ("a.py", "b.py"):
        (tmp_path / name).write_text(f"def f(items):\n    total = 0\n{block}    return total\n")
    result = run("dup_scan.py", str(tmp_path), "--min-lines", "5", "--json")
    assert result.returncode in (0, 1), result.stderr
    payload = json.loads(result.stdout)
    assert "a.py" in result.stdout and "b.py" in result.stdout, payload


def test_context_map_lists_symbols(tmp_path):
    (tmp_path / "m.py").write_text("def used():\n    return 1\n\ndef caller():\n    return used()\n")
    result = run("context_map.py", str(tmp_path), "--json")
    assert result.returncode == 0, result.stderr
    assert "used" in result.stdout and "caller" in result.stdout


def test_cortex_remember_and_search_roundtrip(tmp_path):
    db = str(tmp_path / "c.db")
    remembered = run("cortex.py", "--db", db, "remember", "Req client lives in lib/app/http.ex", "--kind", "convention")
    assert remembered.returncode == 0, remembered.stderr
    found = run("cortex.py", "--db", db, "--json", "search", "Req client")
    assert found.returncode == 0, found.stderr
    assert "lib/app/http.ex" in found.stdout


def test_scanners_ignore_dirs_only_below_the_scanned_root(tmp_path):
    repo = tmp_path / "build" / "app"  # repo cloned inside ~/build/
    (repo / "dist").mkdir(parents=True)
    (repo / "m.py").write_text("def used():\n    return 1\n\ndef caller():\n    return used()\n")
    (repo / "dist" / "bundle.py").write_text("def generated():\n    return 2\n")
    result = run("context_map.py", str(repo), "--json")
    assert result.returncode == 0, result.stderr
    files = json.loads(result.stdout)["loc_by_file"]
    assert list(files) == ["m.py"]


def test_scanners_exit_2_when_nothing_was_scanned(tmp_path):
    (tmp_path / "notes.txt").write_text("not code\n")
    for tool in ("dup_scan.py", "context_map.py"):
        result = run(tool, str(tmp_path))
        assert result.returncode == 2, tool
        assert "0 files scanned" in result.stderr and "not a clean result" in result.stderr


def test_cortex_update_refuses_secret_like_remember(tmp_path):
    db = str(tmp_path / "c.db")
    created = json.loads(run("cortex.py", "--db", db, "--json", "remember", "Req client lives in http.ex").stdout)
    leaked = run("cortex.py", "--db", db, "update", created["uid"], "--text", "api_key = sk_live_abcdef123456")
    assert leaked.returncode == 1 and "secret" in leaked.stderr
    found = run("cortex.py", "--db", db, "--json", "recall", created["uid"])
    assert "sk_live" not in found.stdout
    forced = run("cortex.py", "--db", db, "update", created["uid"], "--text", "api_key = sk_live_abcdef123456", "--force")
    assert forced.returncode == 0, forced.stderr


def test_cortex_default_store_is_per_project(tmp_path):
    env = {k: v for k, v in os.environ.items() if k not in ("CORTEX_HOME", "CORTEX_DB")}
    for name in ("a", "b"):
        (tmp_path / name / "src").mkdir(parents=True)
        subprocess.run(["git", "init", "-q", str(tmp_path / name)], check=True)
    def cortex(cwd, *args, extra=None):
        return subprocess.run([sys.executable, os.path.join(SCRIPTS, "cortex.py"), *args], cwd=cwd,
                              capture_output=True, text=True, env={**env, **(extra or {})})
    assert cortex(tmp_path / "a" / "src", "remember", "cliente A usa Stripe").returncode == 0
    assert (tmp_path / "a" / ".cortex" / "cortex.db").exists()
    assert (tmp_path / "a" / ".cortex" / ".gitignore").read_text() == "*\n"
    status = subprocess.run(["git", "status", "--porcelain"], cwd=tmp_path / "a", capture_output=True, text=True).stdout
    assert ".cortex" not in status
    assert "Stripe" not in cortex(tmp_path / "b", "--json", "search", "Stripe").stdout
    shared = {"CORTEX_HOME": str(tmp_path / "shared")}
    assert cortex(tmp_path / "a", "remember", "global note", extra=shared).returncode == 0
    assert "global note" in cortex(tmp_path / "b", "--json", "search", "global", extra=shared).stdout
