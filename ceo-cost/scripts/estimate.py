#!/usr/bin/env python3
"""Estimates a monthly cost range from usage and the prices in data/pricing.csv and data/fees.csv.

Usage:
  python3 estimate.py --plan "Expo EAS=Starter" --use mau=2000-8000 --use builds=20 [--pick ID ...]
                      [--fee ID --use receita=5000 --use transacoes=120] [--usage uso.json] [--json]
  python3 estimate.py --list [service]

- --plan "Service=Plan" picks every row of that plan; --pick ID picks one row by its id.
- --use metric=value or metric=low-high. Metrics are the "metric" column of pricing.csv
  (mau, builds, egress_gb, storage_gb, ci_minutes, input_mtok, output_mtok, cache_read_mtok,
  cache_write_mtok, compute_month, db_month, seats, ...). "base" rows count once per month;
  yearly fees are divided by 12; "once" fees stay out of the monthly total. A "credit" row
  (unit = the metric it offsets) lowers that metric's cost in the same plan, never below zero. Overage = max(0, usage - included) x unit price.
- --fee ID applies a row of fees.csv: receita x fee_pct + transacoes x fee_fixed.
- --usage FILE: JSON {"plan": [...], "pick": [...], "fee": [...], "use": {"mau": "2000-8000"}}.
- An empty price (pricing.csv price_low) or an empty fee (fees.csv fee_pct and fee_fixed) means
  "not verified": the line is shown as not verified, left out of the total, and the total is partial.

Every line prints the price date (checked_on) and source. Prices checked more than 30 days
before --today (default: today) get a warning: reopen the source before quoting the number.
Totals are kept per currency (USD and BRL are never added together).

Exit code: 0 ok, 2 bad input.
"""
import argparse
import csv
import datetime as dt
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data")
STALE_DAYS = 30
RANGE_RE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*(?:-\s*(\d+(?:\.\d+)?))?\s*$")


class InputError(ValueError):
    pass


def load_csv(name, data_dir=DATA):
    with open(os.path.join(data_dir, name), encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def number(value, default=0.0):
    value = (value or "").strip()
    return float(value) if value else default


def parse_range(raw, what):
    match = RANGE_RE.match(str(raw))
    if not match:
        raise InputError(f"{what}: use número ou faixa baixo-alto (ex.: 2000-8000), recebi {raw!r}")
    low = float(match.group(1))
    high = float(match.group(2)) if match.group(2) else low
    if high < low:
        raise InputError(f"{what}: o alto ({high}) é menor que o baixo ({low})")
    return low, high


def parse_uses(items):
    uses = {}
    for item in items:
        key, sep, value = str(item).partition("=")
        key = key.strip()
        if not sep or not key:
            raise InputError(f"--use precisa de metrica=valor, recebi {item!r}")
        uses[key] = parse_range(value, key)
    return uses


def stale(checked_on, today):
    try:
        day = dt.date.fromisoformat(checked_on)
    except ValueError:
        return True
    return (today - day).days > STALE_DAYS


def select_rows(pricing, plans, picks):
    chosen, seen = [], set()
    by_id = {row["id"]: row for row in pricing}
    for plan in plans:
        service, sep, name = plan.partition("=")
        rows = [r for r in pricing if r["service"] == service.strip() and r["plan"] == name.strip()]
        if not sep or not rows:
            raise InputError(f"plano não achado: {plan!r} (use --list para ver serviço e plano)")
        chosen.extend(r for r in rows if r["id"] not in seen and not seen.add(r["id"]))
    for pick in picks:
        if pick not in by_id:
            raise InputError(f"id não achado em pricing.csv: {pick!r}")
        if pick not in seen:
            seen.add(pick)
            chosen.append(by_id[pick])
    return chosen


def unverified_line(row, service, plan, metric):
    return {"id": row["id"], "servico": service, "plano": plan, "metrica": metric, "uso": (0.0, 0.0), "incluido": 0.0,
            "cobrado": (0.0, 0.0), "custo": None, "nao_verificado": True, "moeda": row["currency"], "unidade": "",
            "checked_on": row["checked_on"], "source": row["source"]}


def estimate(pricing, fees, plans, picks, fee_ids, uses, today):
    rows = select_rows(pricing, plans, picks)
    fee_by_id = {row["id"]: row for row in fees}
    lines, totals, warnings, missing, unverified = [], {}, [], set(), []
    credits = [r for r in rows if r["metric"] == "credit"]
    for row in (r for r in rows if r["metric"] != "credit"):
        metric = row["metric"]
        if not (row["price_low"] or "").strip():
            lines.append(unverified_line(row, row["service"], row["plan"], metric))
            unverified.append(row)
            continue
        low_price, high_price = number(row["price_low"]), number(row["price_high"], number(row["price_low"]))
        if metric == "base" and row["unit"] == "once":
            qty, billed = (1.0, 1.0), (0.0, 0.0)
            warnings.append(f"{row['id']}: taxa única de {row['price_low']} {row['currency']}, fora do total mensal")
        elif metric == "base":
            qty = (1.0, 1.0)
            divisor = 12.0 if row["unit"] == "year" else 1.0
            billed = (1.0 / divisor, 1.0 / divisor)
        else:
            if metric not in uses:
                missing.add(metric)
            qty = uses.get(metric, (0.0, 0.0))
            included = number(row["included"])
            billed = (max(0.0, qty[0] - included), max(0.0, qty[1] - included))
        cost = (billed[0] * low_price, billed[1] * high_price)
        lines.append({"id": row["id"], "servico": row["service"], "plano": row["plan"], "metrica": metric,
                      "uso": qty, "incluido": number(row["included"]), "cobrado": billed, "custo": cost,
                      "moeda": row["currency"], "unidade": row["unit"], "checked_on": row["checked_on"], "source": row["source"]})
        total = totals.setdefault(row["currency"], [0.0, 0.0])
        total[0] += cost[0]
        total[1] += cost[1]
        if stale(row["checked_on"], today):
            warnings.append(f"{row['id']}: preço de {row['checked_on']}, mais de {STALE_DAYS} dias; reabra {row['source']} antes de afirmar")
    for row in credits:
        if not (row["price_low"] or "").strip():
            lines.append(unverified_line(row, row["service"], row["plan"], "credit"))
            unverified.append(row)
            continue
        # A plan credit (e.g. build credit) lowers only the cost of its target metric in the same plan, never below zero.
        target = [l for l in lines if l["metrica"] == row["unit"] and l["servico"] == row["service"]
                  and l["plano"] == row["plan"] and l["custo"] is not None]
        spent = (sum(l["custo"][0] for l in target), sum(l["custo"][1] for l in target))
        value = number(row["price_low"])
        cost = (-min(value, spent[0]), -min(value, spent[1]))
        lines.append({"id": row["id"], "servico": row["service"], "plano": row["plan"], "metrica": "credit",
                      "uso": (value, value), "incluido": 0.0, "cobrado": (1.0, 1.0), "custo": cost, "moeda": row["currency"],
                      "unidade": f"crédito sobre {row['unit']}", "checked_on": row["checked_on"], "source": row["source"]})
        total = totals.setdefault(row["currency"], [0.0, 0.0])
        total[0] += cost[0]
        total[1] += cost[1]
        if stale(row["checked_on"], today):
            warnings.append(f"{row['id']}: crédito de {row['checked_on']}, mais de {STALE_DAYS} dias; reabra {row['source']} antes de afirmar")
    for fee_id in fee_ids:
        row = fee_by_id.get(fee_id)
        if row is None:
            raise InputError(f"id não achado em fees.csv: {fee_id!r}")
        if not ((row["fee_pct"] or "").strip() or (row["fee_fixed"] or "").strip()):
            lines.append(unverified_line(row, row["provider"], row["product"], "taxa"))
            unverified.append(row)
            continue
        revenue = uses.get("receita", (0.0, 0.0))
        count = uses.get("transacoes", (0.0, 0.0))
        if "receita" not in uses:
            missing.add("receita")
        if number(row["fee_fixed"]) and "transacoes" not in uses:
            missing.add("transacoes")
        pct, fixed = number(row["fee_pct"]) / 100.0, number(row["fee_fixed"])
        cost = (revenue[0] * pct + count[0] * fixed, revenue[1] * pct + count[1] * fixed)
        lines.append({"id": row["id"], "servico": row["provider"], "plano": row["product"], "metrica": "taxa",
                      "uso": revenue, "incluido": 0.0, "cobrado": revenue, "custo": cost, "moeda": row["currency"],
                      "unidade": f"{row['fee_pct'] or 0}% + {row['fee_fixed'] or 0} fixo", "checked_on": row["checked_on"],
                      "source": row["source"]})
        total = totals.setdefault(row["currency"], [0.0, 0.0])
        total[0] += cost[0]
        total[1] += cost[1]
        if stale(row["checked_on"], today):
            warnings.append(f"{row['id']}: taxa de {row['checked_on']}, mais de {STALE_DAYS} dias; reabra {row['source']} antes de afirmar")
    per_user = {}
    if "mau" in uses and uses["mau"][1] > 0:
        mau_low, mau_high = uses["mau"]
        for currency, (low, high) in totals.items():
            # Cheapest per user: low cost spread over many users; dearest: high cost over few.
            per_user[currency] = (low / mau_high if mau_high else 0.0, high / mau_low if mau_low else 0.0)
    for metric in sorted(missing):
        warnings.append(f"sem uso informado para '{metric}': contei 0 (use --use {metric}=...)")
    for row in unverified:
        warnings.append(f"{row['id']}: preço/taxa vazio no CSV (não verificado); fora do total, que fica PARCIAL."
                        f" Confira {row['source']} antes de citar")
    return {"linhas": lines, "totais": {k: tuple(v) for k, v in totals.items()}, "por_usuario_ativo": per_user,
            "total_parcial": bool(unverified), "avisos": warnings, "hoje": today.isoformat()}


def money(pair, currency):
    low, high = pair
    big = max(abs(low), abs(high))
    fmt = (lambda v: f"{v:,.2f}") if big >= 0.01 or big == 0 else (lambda v: f"{v:.4f}")
    return f"{fmt(low)} {currency}" if abs(high - low) < 1e-9 else f"{fmt(low)} a {fmt(high)} {currency}"


def qty(pair):
    low, high = pair
    show = lambda v: f"{v:g}"
    return show(low) if low == high else f"{show(low)}-{show(high)}"


def render(result):
    out = [f"Estimativa mensal (preços do CSV, conferidos na data de cada linha; hoje {result['hoje']})."]
    for line in result["linhas"]:
        if line.get("nao_verificado"):
            out.append(f"- [{line['id']}] {line['servico']} {line['plano']} {line['metrica']}: NÃO VERIFICADO"
                       f" (valor vazio no CSV, fora do total) | {line['checked_on']} | {line['source']}")
            continue
        out.append(f"- [{line['id']}] {line['servico']} {line['plano']} {line['metrica']}: uso {qty(line['uso'])},"
                   f" incluído {line['incluido']:g}, cobrado {qty(line['cobrado'])} x {line['unidade']}"
                   f" = {money(line['custo'], line['moeda'])} | preço de {line['checked_on']} | {line['source']}")
    if result.get("total_parcial"):
        out.append("\nTotal por mês (PARCIAL: há linha não verificada fora da soma):")
    else:
        out.append("\nTotal por mês:")
    for currency, pair in result["totais"].items():
        out.append(f"- {money(pair, currency)}")
    if not result["totais"]:
        out.append("- nenhum valor verificado")
    if result["por_usuario_ativo"]:
        out.append("Por usuário ativo no mês:")
        for currency, pair in result["por_usuario_ativo"].items():
            out.append(f"- {money(pair, currency)}")
    if result["avisos"]:
        out.append("\nAvisos:")
        out.extend(f"- {w}" for w in result["avisos"])
    out.append("\nÉ estimativa: imposto, câmbio, crédito promocional e preço negociado ficam de fora. A fatura real manda.")
    return "\n".join(out)


def list_rows(pricing, fees, service):
    out = []
    for row in pricing:
        if not service or row["service"].lower() == service.lower():
            out.append(f"{row['id']}: {row['service']}={row['plan']} {row['metric']} incl. {row['included'] or 0}"
                       f" {row['price_low']}-{row['price_high']} {row['currency']}/{row['unit']} ({row['checked_on']})")
    for row in fees:
        if not service or row["provider"].lower() == service.lower():
            value = (f"{row['fee_pct'] or 0}% + {row['fee_fixed'] or 0} {row['currency']}"
                     if (row["fee_pct"] or row["fee_fixed"]) else "valor não verificado")
            out.append(f"{row['id']}: taxa {row['provider']} {row['product']} ({row['condition']}) {value} ({row['checked_on']})")
    return "\n".join(out) or "nada achado"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--plan", action="append", default=[], help='"Serviço=Plano" como em pricing.csv')
    parser.add_argument("--pick", action="append", default=[], help="id de uma linha de pricing.csv")
    parser.add_argument("--fee", action="append", default=[], help="id de uma linha de fees.csv")
    parser.add_argument("--use", action="append", default=[], help="metrica=valor ou metrica=baixo-alto")
    parser.add_argument("--usage", help="arquivo JSON com plan, pick, fee e use")
    parser.add_argument("--today", help="data de hoje AAAA-MM-DD (padrão: hoje)")
    parser.add_argument("--list", nargs="?", const="", metavar="SERVICO", help="lista ids, planos e preços")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        pricing, fees = load_csv("pricing.csv"), load_csv("fees.csv")
        if args.list is not None:
            print(list_rows(pricing, fees, args.list))
            return 0
        today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
        plans, picks, fee_ids, use_items = list(args.plan), list(args.pick), list(args.fee), list(args.use)
        if args.usage:
            if args.usage.startswith("-") or any(ord(ch) < 32 for ch in args.usage):
                raise InputError(f"caminho inválido: {args.usage!r}")
            with open(args.usage, encoding="utf-8") as handle:
                data = json.load(handle)
            if not isinstance(data, dict):
                raise InputError("o JSON de uso precisa ser um objeto")
            for key in ("plan", "pick", "fee"):
                value = data.get(key, [])
                if not isinstance(value, list) or not all(isinstance(p, str) for p in value):
                    raise InputError(f"no JSON de uso, '{key}' precisa ser lista de textos, recebi {value!r}")
            use = data.get("use") or {}
            if not isinstance(use, dict) or not all(isinstance(v, (str, int, float)) and not isinstance(v, bool)
                                                    for v in use.values()):
                raise InputError(f'no JSON de uso, \'use\' precisa ser objeto {{"metrica": "valor"}}, recebi {use!r}')
            plans += data.get("plan", [])
            picks += data.get("pick", [])
            fee_ids += data.get("fee", [])
            use_items += [f"{k}={v}" for k, v in use.items()]
        if not (plans or picks or fee_ids):
            raise InputError("diga o que estimar: --plan, --pick ou --fee (veja --list)")
        result = estimate(pricing, fees, plans, picks, fee_ids, parse_uses(use_items), today)
    except (InputError, ValueError, OSError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else render(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
