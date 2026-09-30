#!/usr/bin/env python3
"""Keyword search over the skill's data/*.csv (heuristics, anti-patterns, components, reference apps).

Usage: python search.py "bottom sheet android" [--domain components] [--limit 5]
Domains: heuristics, anti-patterns, components, reference-apps, market-sources (default: all).
Scores with BM25 over every column, stdlib only, so it runs anywhere the skill runs.
"""
import argparse
import csv
import math
import os
import re
import sys
import unicodedata

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
DOMAINS = ("heuristics", "anti-patterns", "components", "reference-apps", "market-sources")
K1, B = 1.5, 0.75


def normalize(text: str) -> list[str]:
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.findall(r"[a-z0-9]+", ascii_text.lower())


def load_rows(data_dir: str, domains: list[str]) -> list[tuple[str, dict]]:
    rows = []
    for domain in domains:
        path = os.path.join(data_dir, f"{domain}.csv")
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8", newline="") as handle:
            rows.extend((domain, row) for row in csv.DictReader(handle))
    return rows


def rank(query: str, rows: list[tuple[str, dict]], limit: int) -> list[tuple[float, str, dict]]:
    docs = [normalize(" ".join(v or "" for v in row.values())) for _, row in rows]
    if not docs:
        return []
    avg_len = sum(len(d) for d in docs) / len(docs)
    terms = normalize(query)
    doc_freq = {t: sum(1 for d in docs if t in d) for t in terms}
    scored = []
    for (domain, row), doc in zip(rows, docs):
        score = 0.0
        for term in terms:
            tf = doc.count(term)
            if not tf:
                continue
            idf = math.log(1 + (len(docs) - doc_freq[term] + 0.5) / (doc_freq[term] + 0.5))
            score += idf * tf * (K1 + 1) / (tf + K1 * (1 - B + B * len(doc) / avg_len))
        if score > 0:
            scored.append((score, domain, row))
    scored.sort(key=lambda item: item[0], reverse=True)
    return scored[:limit]


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--domain", choices=DOMAINS)
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--data-dir", default=DATA_DIR)
    args = parser.parse_args(argv)
    domains = [args.domain] if args.domain else list(DOMAINS)
    results = rank(args.query, load_rows(args.data_dir, domains), args.limit)
    for score, domain, row in results:
        print(f"[{domain}] {score:.2f}")
        for key, value in row.items():
            if value:
                print(f"  {key}: {value}")
    if not results:
        print("no match")
    return 0 if results else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
