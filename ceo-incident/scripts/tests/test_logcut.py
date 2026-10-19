import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, SCRIPTS)

import logcut  # noqa: E402
from _common import mask  # noqa: E402

ELIXIR_LOG = """\
12:00:01.120 request_id=F1aBcDeFgHiJkLmN [info] GET /api/health
12:00:02.300 request_id=F2aBcDeFgHiJkLmN [error] ** (Ecto.NoResultsError) expected at least one result for user 4812
    (ecto 3.12.0) lib/ecto/repo/queryable.ex:164: Ecto.Repo.Queryable.one!/3
    (app 0.1.0) lib/app/accounts.ex:40: App.Accounts.get!/1
12:03:10.010 request_id=F3aBcDeFgHiJkLmN [error] ** (Ecto.NoResultsError) expected at least one result for user 977
12:01:00.000 request_id=F4aBcDeFgHiJkLmN [warning] login falhou para maria.silva@example.com tel (11) 98765-4321
12:05:00.000 request_id=F5aBcDeFgHiJkLmN [error] payment webhook timeout after 30000ms token=sk_live_ABCDEFGHIJKLMNOP cpf 123.456.789-09
"""

RAILS_LOG = """\
I, [2026-10-19T12:00:00.000000 #101]  INFO -- : Started GET "/orders/55"
E, [2026-10-19T12:00:05.000000 #101] ERROR -- : ActiveRecord::RecordNotFound (Couldn't find Order with 'id'=55)
E, [2026-10-19T12:07:05.000000 #102] ERROR -- : ActiveRecord::RecordNotFound (Couldn't find Order with 'id'=91)
"""

JSON_LOG = "\n".join([
    json.dumps({"level": 50, "time": 1792411200000, "msg": "db connection refused 10.0.0.12:5432"}),
    json.dumps({"level": 50, "time": 1792411260000, "msg": "db connection refused 10.0.0.13:5432"}),
    json.dumps({"level": 30, "time": 1792411270000, "msg": "request completed"}),
    json.dumps({"severity": "ERROR", "timestamp": "2026-10-19T15:00:00-03:00", "message": "Bearer abcdefghijklmnop1234 rejected"}),
]) + "\n"


def run(text, *args):
    stats, groups = logcut.analyze(text.splitlines(True), *args)
    return stats, groups


def test_elixir_groups_by_signature_with_stack_and_window():
    stats, groups = run(ELIXIR_LOG, "warn")
    top = groups[0]
    assert top["total"] == 2
    assert "Ecto.NoResultsError" in top["assinatura"]
    assert "4812" not in top["assinatura"]
    assert top["primeiro"] == "12:00:02" and top["ultimo"] == "12:03:10"
    assert top["com_stack"] == 1
    assert stats["linhas"] == 7 and stats["entradas"] == 5
    assert all(g["nivel"] != "info" for g in groups)


def test_masks_personal_data_and_secrets_everywhere():
    _, groups = run(ELIXIR_LOG, "warn")
    dump = json.dumps(groups, ensure_ascii=False)
    for leaked in ("maria.silva@example.com", "98765-4321", "sk_live_ABCDEFGHIJKLMNOP", "123.456.789-09"):
        assert leaked not in dump
    assert "[oculto]" in dump


def test_rails_format_and_min_level():
    _, groups = run(RAILS_LOG, "error")
    assert len(groups) == 1
    group = groups[0]
    assert group["total"] == 2 and group["nivel"] == "error"
    assert group["assinatura"].startswith("ActiveRecord::RecordNotFound")
    assert group["primeiro"] == "2026-10-19T12:00:05" and group["ultimo"] == "2026-10-19T12:07:05"


def test_json_lines_numeric_level_epoch_and_zone():
    _, groups = run(JSON_LOG, "warn")
    by_sig = {g["assinatura"]: g for g in groups}
    refused = next(g for s, g in by_sig.items() if "connection refused" in s)
    assert refused["total"] == 2
    assert "10.0.0.12" not in refused["exemplo"]
    bearer = next(g for s, g in by_sig.items() if "rejected" in s)
    assert bearer["primeiro"] == "2026-10-19T18:00:00Z"
    assert "abcdefghijklmnop1234" not in json.dumps(groups)
    assert not any("request completed" in s for s in by_sig)


def test_unleveled_error_lines_count_and_grep_filters():
    text = "boot ok\nTraceback (most recent call last):\nconnection failed to redis\n"
    _, groups = run(text, "warn")
    assert len(groups) == 2
    _, only = run(text, "warn", "redis")
    assert len(only) == 1 and "redis" in only[0]["assinatura"]


def test_output_is_deterministic(tmp_path):
    path = tmp_path / "app.log"
    path.write_text(ELIXIR_LOG + RAILS_LOG + JSON_LOG, encoding="utf-8")
    cmd = [sys.executable, os.path.join(SCRIPTS, "logcut.py"), str(path), "--json"]
    first = subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=True).stdout
    second = subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=True).stdout
    assert first == second
    assert json.loads(first)["total_grupos"] >= 5


def test_text_output_and_missing_file(tmp_path, capsys):
    path = tmp_path / "x.log"
    path.write_text(ELIXIR_LOG, encoding="utf-8")
    assert logcut.main([str(path), "--top", "1"]) == 0
    out = capsys.readouterr().out
    assert "2x" in out and "grupos a mais" in out
    assert logcut.main([str(tmp_path / "nao-existe.log")]) == 2


def test_mask_examples():
    assert mask("postgres://user:segredo@db:5432/app") == "postgres://[oculto]@db:5432/app"
    assert "abc123" not in mask("password=abc123 ok")
    assert mask("CNPJ 12.345.678/0001-90") == "CNPJ [oculto]"
    assert mask("pedido 2026-10-19 às 12:00:00") == "pedido 2026-10-19 às 12:00:00"


def test_mask_prefixed_secret_keys_and_plain_cpf():
    assert "abcDEF123xyz" not in mask('"access_token": "abcDEF123xyz"')
    assert "s3cr3tvalue" not in mask("client_secret=s3cr3tvalue")
    assert "12345678901" not in mask("cpf=12345678901")


def test_bad_json_timestamps_do_not_crash():
    text = '{"ts": NaN, "level": "error", "message": "x"}\n{"ts": 1e300, "level": "error", "message": "x"}\n'
    stats, groups = run(text, "warn")
    assert groups[0]["total"] == 2 and stats["sem_hora"] == 2
