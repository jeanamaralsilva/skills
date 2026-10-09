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
