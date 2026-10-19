"""Tests for ugly_scan. Run from scripts/: python -m pytest -q tests"""
import os
import subprocess
import sys

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(*args):
    return subprocess.run([sys.executable, os.path.join(SCRIPTS, "ugly_scan.py"), *args], capture_output=True, text=True)


def test_repo_inside_a_build_folder_is_still_scanned(tmp_path):
    repo = tmp_path / "build" / "app"  # repo clonado dentro de ~/build/
    (repo / "src").mkdir(parents=True)
    (repo / "dist").mkdir()
    (repo / "src" / "Home.tsx").write_text("export const H = () => <Text>Loading...</Text>;\n")
    (repo / "dist" / "bundle.js").write_text("x = <Text>Loading</Text>;\n")
    result = run(str(repo))
    assert result.returncode == 0, result.stderr
    assert "src/Home.tsx:1" in result.stdout and "dist/" not in result.stdout


def test_zero_files_scanned_is_an_error_not_clean(tmp_path):
    (tmp_path / "README.md").write_text("nada\n")
    result = run(str(tmp_path))
    assert result.returncode == 2
    assert "nenhum arquivo" in result.stderr and "0 pistas" not in result.stdout
