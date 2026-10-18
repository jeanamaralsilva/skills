#!/usr/bin/env python3
"""Audits the navigation structure of one screen: nested tabs, repeated labels, filters disguised
as tabs, empty tabs, constant columns.

Usage: python nav_audit.py outline.json
       python nav_audit.py - <<'EOF'            (plain text outline on stdin)
       title: Financeiro - Auditoria
       L1: Faturamento do mês | Vínculos | Resumão
       L2: Faturamento do mês | Liberados 0 | Inadimplentes 137
       filters: Todos 751 | Sem diferença 289 | Com diferença 462
       heading: Setembro de 2026
       col Motivo: Posse sem cobrança | Posse sem cobrança | Posse sem cobrança
       EOF

The outline is what you see on the screen, top to bottom: the page title, each row of tabs
(L1, L2, ...), filter chips if they are visually filters, the section heading, and any column
whose values you can read. The script does not look at pixels; you transcribe, it judges.
Rules follow NN/g "Tabs, Used Right" (one row of tabs, short labels, tabs are not filters)
and the density rules in references/19-navegacao-e-densidade.md. Exit 1 when there are findings.
"""
import argparse
import json
import re
import sys
import unicodedata

COUNT = re.compile(r"^(.*?)\s+(\d[\d.]*)$")
STOPWORDS = {"de", "do", "da", "dos", "das", "e", "o", "a", "os", "as", "em", "no", "na", "nos", "nas", "por", "para", "com", "of", "the", "and", "in", "by"}


def normalize(label: str) -> str:
    base = COUNT.match(label.strip())
    text = base.group(1) if base else label
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", ascii_text.strip().lower())


def count_of(label: str):
    match = COUNT.match(label.strip())
    return int(match.group(2).replace(".", "")) if match else None


def is_partition(labels: list[str]) -> bool:
    """True when one label's count equals the sum of the others: same table, filtered."""
    counts = [count_of(l) for l in labels]
    if len(counts) < 3 or any(c is None for c in counts):
        return False
    total = max(counts)
    return sum(counts) - total == total


def parse_text(text: str) -> dict:
    outline: dict = {"levels": [], "columns": {}}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        items = [v.strip() for v in value.split("|") if v.strip()]
        if re.fullmatch(r"L\d+", key, re.I):
            outline["levels"].append(items)
        elif key.lower() == "filters":
            outline["filters"] = items
        elif key.lower().startswith("col "):
            outline["columns"][key[4:].strip()] = items
        else:
            outline[key.lower()] = value.strip()
    return outline


def audit(outline: dict) -> list[dict]:
    findings: list[dict] = []
    levels: list[list[str]] = [list(level) for level in outline.get("levels", [])]
    title = outline.get("title", "")
    heading = outline.get("heading", "")

    # A tab row that only partitions the table is a filter wearing a tab costume.
    tab_rows = []
    for index, level in enumerate(levels, start=1):
        if is_partition(level):
            findings.append({"rule": "filtro-como-aba", "severity": "P2",
                             "detail": f"nível {index} ({' | '.join(level)}): as contagens somam o total, é a mesma tabela filtrada",
                             "fix": "segmented control ou chips junto da tabela; aba só para conteúdo diferente (AN03)"})
        else:
            tab_rows.append((index, level))

    if len(tab_rows) >= 2:
        findings.append({"rule": "abas-dentro-de-abas", "severity": "P1",
                         "detail": f"{len(tab_rows)} linhas de abas empilhadas (níveis {', '.join(str(i) for i, _ in tab_rows)})",
                         "fix": "uma linha de abas; o outro nível vira sidebar, segmented control com outro nome, ou página própria (H21, AN01)"})

    seen: dict[str, str] = {}
    if title:
        seen[normalize(title)] = "título"
    for index, level in enumerate(levels, start=1):
        for label in level:
            key = normalize(label)
            if key in seen:
                findings.append({"rule": "rotulo-repetido", "severity": "P2",
                                 "detail": f"'{label}' aparece em {seen[key]} e no nível {index}",
                                 "fix": "cada rótulo uma vez por tela; o nível de baixo diz o que acrescenta (H22, AN02)"})
            else:
                seen[key] = f"nível {index}"
    if heading and normalize(heading) in seen:
        findings.append({"rule": "rotulo-repetido", "severity": "P2",
                         "detail": f"h2 '{heading}' repete {seen[normalize(heading)]}", "fix": "o h2 traz só o que muda (período, cliente)"})

    flagged_long: set[str] = set()
    for index, level in enumerate(levels, start=1):
        for label in level:
            words = len([w for w in normalize(label).split() if w not in STOPWORDS])
            if words > 2 and normalize(label) not in flagged_long:
                flagged_long.add(normalize(label))
                findings.append({"rule": "rotulo-longo", "severity": "P3", "detail": f"'{label}' tem {words} palavras",
                                 "fix": "1 ou 2 palavras na linguagem do usuário (H24)"})
            if count_of(label) == 0:
                findings.append({"rule": "aba-vazia", "severity": "P3", "detail": f"'{label}' no nível {index} mostra 0",
                                 "fix": "esconder quando vazia ou explicar por que existe (H25)"})

    for name, values in outline.get("columns", {}).items():
        distinct = {normalize(v) for v in values if v}
        if len(values) >= 3 and len(distinct) == 1:
            findings.append({"rule": "coluna-constante", "severity": "P2",
                             "detail": f"coluna '{name}' tem o mesmo valor em {len(values)} linhas ('{values[0]}')",
                             "fix": "mover para o filtro ativo ou para o cabeçalho; mostrar na linha só quando difere (H26, AN04)"})

    header_blocks = sum(1 for part in (title, heading) if part) + len(levels) + (1 if outline.get("filters") else 0)
    if header_blocks >= 5:
        findings.append({"rule": "cabecalho-em-cascata", "severity": "P2",
                         "detail": f"{header_blocks} blocos acima da primeira linha de dado",
                         "fix": "comprimir: título + período + métrica numa faixa; filtros e busca na linha da tabela (AN05)"})
    return findings


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("outline", help="outline.json or - for text on stdin")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    raw = sys.stdin.read() if args.outline == "-" else open(args.outline, encoding="utf-8").read()
    outline = json.loads(raw) if raw.lstrip().startswith("{") else parse_text(raw)
    findings = audit(outline)
    if args.json:
        print(json.dumps(findings, ensure_ascii=False, indent=2))
    elif not findings:
        print("navegação limpa")
    else:
        for f in findings:
            print(f"{f['severity']} {f['rule']}: {f['detail']} → {f['fix']}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
