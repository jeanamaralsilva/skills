import datetime as dt
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import estimate  # noqa: E402

TODAY = dt.date(2026, 10, 19)


def row(id, service, plan, metric, included, low, high, unit="month", currency="USD", checked_on="2026-10-19"):
    return {"id": id, "service": service, "plan": plan, "metric": metric, "included": str(included), "price_low": str(low),
            "price_high": str(high), "currency": currency, "unit": unit, "checked_on": checked_on,
            "source": "https://example.invalid/pricing"}


PRICING = [
    row("B-BASE", "Build", "Starter", "base", "", 19, 19),
    row("B-MAU", "Build", "Starter", "mau", 3000, 0.005, 0.005, unit="mau"),
    row("B-BUILD", "Build", "Starter", "builds", 0, 1, 4, unit="build"),
    row("B-CREDIT", "Build", "Starter", "credit", "", 15, 15, unit="builds"),
    row("DEV", "Store", "Dev", "base", "", 99, 99, unit="year"),
    row("REG", "Store", "Reg", "base", "", 25, 25, unit="once"),
    row("OLD", "Old", "X", "base", "", 10, 10, checked_on="2026-08-01"),
]
FEES = [{"id": "F-CARD", "provider": "Pay", "product": "card", "condition": "", "fee_pct": "4", "fee_fixed": "0.40",
         "currency": "BRL", "checked_on": "2026-10-19", "source": "https://example.invalid/fees"}]


def run(plans=(), picks=(), fees=(), uses=None):
    return estimate.estimate(PRICING, FEES, list(plans), list(picks), list(fees), uses or {}, TODAY)


def test_base_plus_overage_with_usage_range():
    result = run(plans=["Build=Starter"], uses=estimate.parse_uses(["mau=2000-8000", "builds=10"]))
    low, high = result["totais"]["USD"]
    # builds 10..40 minus a 15 credit (never below zero): low 19 + 0 + 0 ; high 19 + 5000 x 0.005 + (40 - 15)
    assert low == pytest.approx(19.0)
    assert high == pytest.approx(19 + 25 + 25)
    per_low, per_high = result["por_usuario_ativo"]["USD"]
    assert per_low == pytest.approx(19.0 / 8000)
    assert per_high == pytest.approx(69.0 / 2000)


def test_yearly_fee_is_monthly_and_one_time_fee_is_left_out():
    result = run(picks=["DEV", "REG"])
    assert result["totais"]["USD"][0] == pytest.approx(99 / 12)
    assert any("taxa única" in w for w in result["avisos"])


def test_stale_price_warns_and_missing_usage_warns():
    result = run(picks=["OLD", "B-MAU"])
    assert any("OLD" in w and "30 dias" in w for w in result["avisos"])
    assert any("'mau'" in w for w in result["avisos"])


def test_fee_uses_revenue_and_transactions_and_keeps_currency_apart():
    result = run(picks=["B-BASE"], fees=["F-CARD"], uses=estimate.parse_uses(["receita=1000", "transacoes=10"]))
    assert result["totais"]["BRL"][0] == pytest.approx(40 + 4)
    assert result["totais"]["USD"][0] == pytest.approx(19)


def test_unknown_plan_pick_or_bad_number_raise():
    with pytest.raises(estimate.InputError):
        run(plans=["Build=Nope"])
    with pytest.raises(estimate.InputError):
        run(picks=["NOPE"])
    with pytest.raises(estimate.InputError):
        estimate.parse_uses(["mau=abc"])
    with pytest.raises(estimate.InputError):
        estimate.parse_uses(["mau=9-1"])


def test_cli_with_real_csv(capsys, tmp_path):
    usage = tmp_path / "uso.json"
    usage.write_text(json.dumps({"plan": ["Expo EAS=Starter"], "use": {"mau": "5000", "builds": "10"}}), encoding="utf-8")
    assert estimate.main(["--usage", str(usage), "--today", "2026-10-19"]) == 0
    out = capsys.readouterr().out
    assert "EAS-STARTER" in out and "2026-10-19" in out and "https://" in out
    assert estimate.main(["--plan", "Expo EAS=Starter", "--today", "2027-01-01"]) == 0
    assert "mais de 30 dias" in capsys.readouterr().out


def test_cli_bad_input_exit_2(capsys):
    assert estimate.main([]) == 2
    assert estimate.main(["--usage=-x.json"]) == 2
    assert estimate.main(["--plan", "Nada=Nada"]) == 2
    assert "error" in capsys.readouterr().err


def test_real_csvs_have_source_date_and_numbers():
    pricing = estimate.load_csv("pricing.csv")
    fees = estimate.load_csv("fees.csv")
    levers = estimate.load_csv("levers.csv")
    ids = [r["id"] for r in pricing] + [r["id"] for r in fees] + [r["id"] for r in levers]
    assert len(ids) == len(set(ids))
    for r in pricing + fees + levers:
        assert r["source"].startswith("https://"), r["id"]
        dt.date.fromisoformat(r["checked_on"])
    for r in pricing:
        float(r["price_low"])
        float(r["price_high"])
        assert float(r["price_low"]) <= float(r["price_high"]), r["id"]


def test_empty_fee_is_unverified_not_zero_and_total_is_partial(capsys):
    fees = FEES + [{"id": "F-EMPTY", "provider": "Store", "product": "app", "condition": "", "fee_pct": "", "fee_fixed": "",
                    "currency": "USD", "checked_on": "2026-10-19", "source": "https://example.invalid/fees"}]
    result = estimate.estimate(PRICING, fees, [], ["B-BASE"], ["F-EMPTY"], estimate.parse_uses(["receita=1000"]), TODAY)
    line = next(l for l in result["linhas"] if l["id"] == "F-EMPTY")
    assert line["custo"] is None and line["nao_verificado"]
    assert result["total_parcial"] is True
    assert result["totais"]["USD"][0] == pytest.approx(19)
    assert any("F-EMPTY" in w and "não verificado" in w for w in result["avisos"])
    text = estimate.render(result)
    assert "NÃO VERIFICADO" in text and "PARCIAL" in text


def test_empty_price_is_unverified_not_zero():
    pricing = PRICING + [row("NOPRICE", "X", "Y", "base", "", "", "")]
    result = estimate.estimate(pricing, FEES, [], ["NOPRICE"], [], {}, TODAY)
    assert result["linhas"][0]["custo"] is None
    assert result["total_parcial"] is True and result["totais"] == {}
    assert "nenhum valor verificado" in estimate.render(result)


def test_real_empty_fee_apple_std_is_not_zero(capsys):
    assert estimate.main(["--fee", "APPLE-STD", "--use", "receita=1000", "--today", "2026-10-19"]) == 0
    out = capsys.readouterr().out
    assert "NÃO VERIFICADO" in out and "PARCIAL" in out and "0.00 USD" not in out


@pytest.mark.parametrize("payload", [{"use": ["mau"]}, {"plan": "Expo EAS=Free"}, {"pick": [1]},
                                     {"plan": ["Expo EAS=Starter"], "use": {"mau": {"x": 1}}}])
def test_usage_json_wrong_shape_exit_2(capsys, tmp_path, payload):
    usage = tmp_path / "uso.json"
    usage.write_text(json.dumps(payload), encoding="utf-8")
    assert estimate.main(["--usage", str(usage), "--today", "2026-10-19"]) == 2
    captured = capsys.readouterr()
    assert "error" in captured.err and "JSON de uso" in captured.err and captured.out == ""


def test_list_shows_empty_fee_as_unverified_not_zero():
    text = estimate.list_rows([], estimate.load_csv("fees.csv"), "Apple App Store")
    apple_std = next(l for l in text.splitlines() if l.startswith("APPLE-STD"))
    assert "não verificado" in apple_std and "0%" not in apple_std
