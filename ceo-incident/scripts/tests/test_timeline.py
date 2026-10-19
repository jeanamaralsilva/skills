import json
import os
import shutil
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, SCRIPTS)

import timeline  # noqa: E402

GIT = shutil.which("git")

EVENTS = """\
# Incidente: login fora do ar

## Linha do tempo
- 2026-10-19 13:50 inicio: primeiros erros 500 no login (pelo log)
- 14:05 detectado: cliente reclamou no suporte, contato maria@example.com
- 14:10 declarado: SEV2, comandante assumiu
- 14:25 mitigado: rollback do servidor para o deploy anterior
- 14:30 qualquer coisa sem tipo conhecido
- 15:00 resolvido: taxa de erro normal por 30 min
texto solto que não é evento
- sem hora aqui
"""


def sh(cwd, *args, date=None):
    env = dict(os.environ, GIT_AUTHOR_NAME="Dev", GIT_AUTHOR_EMAIL="dev@example.com",
               GIT_COMMITTER_NAME="Dev", GIT_COMMITTER_EMAIL="dev@example.com")
    if date:
        env.update(GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
    subprocess.run([GIT, *args], cwd=cwd, env=env, check=True, capture_output=True, timeout=30)


@pytest.fixture
def repo(tmp_path):
    path = tmp_path / "server"
    path.mkdir()
    sh(path, "init", "-q", "-b", "main")
    commits = [
        ("2026-10-18T10:00:00-03:00", "chore: base antiga"),
        ("2026-10-19T13:40:00-03:00", "feat(auth): novo fluxo de sessão (#42)"),
        ("2026-10-19T14:20:00-03:00", "Revert \"feat(auth): novo fluxo de sessão (#42)\" token ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123"),
    ]
    for index, (date, msg) in enumerate(commits):
        (path / f"f{index}.txt").write_text(str(index))
        sh(path, "add", f"f{index}.txt")
        sh(path, "commit", "-q", "-m", msg, date=date)
        if index == 1:
            sh(path, "tag", "-a", "v2.4.0", "-m", "release", date=date)
    return path


@pytest.fixture
def events(tmp_path):
    path = tmp_path / "2026-10-19.md"
    path.write_text(EVENTS, encoding="utf-8")
    return path


def run_json(*args):
    out = subprocess.run([sys.executable, os.path.join(SCRIPTS, "timeline.py"), *args, "--json"],
                         capture_output=True, text=True, timeout=60, check=True).stdout
    return json.loads(out), out


def test_events_and_git_merge_sorted_with_milestones(repo, events):
    result, _ = run_json("--events", str(events), "--repo", str(repo), "--tz", "-03:00")
    kinds = [(item["at"][11:16], item["type"]) for item in result["itens"]]
    assert kinds[0] == ("13:40", "commit") and kinds[1] == ("13:40", "tag")
    assert ("13:50", "inicio") in kinds and ("14:20", "commit") in kinds
    assert all(item["text"] != "base antiga" for item in result["itens"])
    assert not any("base antiga" in item["text"] for item in result["itens"])
    assert {m["ate"]: m["minutos"] for m in result["marcos"]} == {"detectar": 15, "mitigar": 35, "resolver": 70}
    notes = [item for item in result["itens"] if item["type"] == "nota"]
    assert len(notes) == 1


def test_masks_untrusted_text(repo, events):
    _, raw = run_json("--events", str(events), "--repo", str(repo), "--tz", "-03:00")
    assert "maria@example.com" not in raw
    assert "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123" not in raw


def test_deterministic_markdown(repo, events):
    cmd = [sys.executable, os.path.join(SCRIPTS, "timeline.py"), "--events", str(events), "--repo", str(repo), "--tz", "-03:00"]
    first = subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=True).stdout
    second = subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=True).stdout
    assert first == second
    assert "| 2026-10-19 14:25 | eventos | mitigado |" in first
    assert "até mitigar: 35 min" in first


def test_explicit_window_filters_git(repo):
    result, _ = run_json("--repo", str(repo), "--since", "2026-10-19T14:00", "--tz", "-03:00")
    assert [item["type"] for item in result["itens"]] == ["commit"]
    assert any("sem arquivo de eventos" in w for w in result["warnings"])


@pytest.mark.parametrize("args", [
    ["--repo", "x", "--since", "2026-10-19", "--ref=--all"],
    ["--repo=-C/tmp", "--since", "2026-10-19"],
    ["--repo", "x"],
    ["--events", "x.md", "--tz", "Brasil"],
    ["--repo", "x", "--since", "ontem"],
])
def test_rejects_bad_input(args, tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "x").mkdir()
    (tmp_path / "x.md").write_text("- 2026-10-19 10:00 inicio: a\n", encoding="utf-8")
    assert timeline.main(args) == 2
    assert "erro:" in capsys.readouterr().err


def test_bad_repo_is_a_warning_not_a_crash(tmp_path, events):
    (tmp_path / "nao-git").mkdir()
    result, _ = run_json("--events", str(events), "--repo", str(tmp_path / "nao-git"))
    assert any("git log falhou" in w for w in result["warnings"])
    assert len(result["itens"]) == 6


def test_time_only_line_without_file_date(tmp_path):
    path = tmp_path / "notas.md"
    path.write_text("- 10:00 inicio: a\n- 2026-10-19T10:05Z detectado: b\n", encoding="utf-8")
    result, _ = run_json("--events", str(path))
    assert [item["type"] for item in result["itens"]] == ["detectado"]
    assert any("sem data" in w for w in result["warnings"])


def test_git_utc_z_suffix_parses():
    assert timeline.from_git_date("2026-10-19T10:00:00Z").utcoffset().total_seconds() == 0
