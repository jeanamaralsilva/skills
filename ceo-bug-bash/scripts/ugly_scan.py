#!/usr/bin/env python3
"""Varredura estática de defeitos que o cliente vê num app RN/Expo em pt-BR.

Uso: python ugly_scan.py <repo-mobile> [--json]

Cada regra nasceu de um bug real (ver references/06-aprendizados-exemplo.md). Saída é
pista, não veredito: confirme lendo o código e, se possível, no print.
"""
import json
import re
import sys
from pathlib import Path

SKIP_DIRS = {"node_modules", ".git", "ios", "android", "dist", "build", ".expo", "__tests__", "coverage"}
EXTS = {".ts", ".tsx", ".js", ".jsx"}

# Palavras terminadas em "s" que não são plural de substantivo ("${data} às 10h").
PLURAL_STOPWORDS = ("às", "as", "os", "das", "dos", "nas", "nos", "pelas", "pelos", "mais", "menos",
                    "após", "depois", "apenas", "antes", "atrás", "através", "vs", "is", "was", "has")

# (id, severidade, descrição, regex)
RULES = [
    ("money-tofixed", "alta", "Dinheiro com toFixed: sai 'R$ 1800.00' ou sem milhar",
     re.compile(r"R\$\s*\$?\{?[^\n]*toFixed\(|toFixed\(2\)\.replace\(")),
    ("http-code-in-text", "alta", "Código HTTP no texto mostrado ao usuário",
     re.compile(r"[`\"'][^`\"'\n]*\(\$\{[^}]*status[^}]*\}\)[^`\"'\n]*[`\"']")),
    ("raw-error-message", "media", "Mensagem crua de erro na tela (confira se é traduzida antes)",
     re.compile(r"(setError|toast\.error|Alert\.alert)\([^)\n]*\b(e|err|error)\??\.message")),
    ("english-ui", "alta", "Texto em inglês visível",
     re.compile(r">\s*(Loading|Error|Cancel|Submit|Save|Delete|Retry|Something went wrong|No data)\.{0,3}\s*<|"
                r"(title|label|placeholder|message|text)\s*[:=]\s*[\"'](Loading|Error|Cancel|Submit|Save|Delete|Retry)[\"']")),
    ("plural-fixed", "baixa", "Plural fixo com número em template ('1 itens', '1 dias')",
     re.compile(r"`[^`\n]*\$\{[^}]+\}\s+(?!(?:" + "|".join(PLURAL_STOPWORDS) + r")\b)[a-zà-ú]{2,}s\b")),
    ("missing-accent", "baixa", "Palavra sem acento em texto visível",
     re.compile(r"[\"'`>][^\"'`<\n]*\b(Nao|nao|possivel|Voce|voce|sessao|Sessao|Endereco|endereco|ate|tambem|numero|Numero|codigo|Codigo|horario|Horario|proxima|Proxima|historico|Historico|configuracoes|Configuracoes|informacoes)\b[^\"'`<\n]*[\"'`<]")),
    ("raw-null-ui", "alta", "undefined/null/NaN/Invalid date podem vazar em template",
     re.compile(r"[\"'`](undefined|null|NaN|Invalid date)[\"'`]|\?\?\s*[\"']undefined")),
    ("ampm-or-us-date", "media", "Formato de data americano ou AM/PM",
     re.compile(r"format\([\"'][^\"']*(MM/DD|hh:mm\s*A|h:mm\s*a)[^\"']*[\"']\)")),
    ("decimal-point-unit", "baixa", "Número com ponto antes de unidade ('1.2km')",
     re.compile(r"toFixed\(1\)\}\s*(km|kg|m)\b")),
    ("case-sensitive-error-map", "media", "Mapa de erro do servidor com chave em inglês: compare sem maiúsculas",
     re.compile(r"[\"'](Not found|Internal server error|Unauthorized|Bad request)[\"']\s*:")),
]


# Regras que olham o arquivo inteiro: o defeito nasce da combinação de props.
FILE_RULES = [
    ("sheet-auto-scrollable", "media",
     "TrueSheet com detents auto e scrollable: no iOS abre na altura máxima com vazio embaixo",
     lambda text: re.search(r"detents=\{\[\s*[\"']auto[\"']\s*\]\}", text) and re.search(r"^\s*scrollable\b", text, re.M)),
    ("sheet-footer-transparent", "media",
     "TrueSheet com footer: confira com teclado aberto se o rodapé tem fundo e não cobre campos",
     lambda text: "<TrueSheet" in text and re.search(r"\bfooter=\{", text) and "TextInput" in text or ("<TrueSheet" in text and re.search(r"\bfooter=\{", text) and "<Input" in text)),
]


def source_files(root: Path):
    for path in root.rglob("*"):
        # só o caminho relativo: um repo dentro de ~/build/ não pode sumir inteiro
        if path.suffix not in EXTS or any(p in SKIP_DIRS for p in path.relative_to(root).parts):
            continue
        if ".test." in path.name:
            continue
        yield path


def scan(root: Path):
    hits = []
    for path in source_files(root):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        text = "\n".join(lines)
        for rid, sev, desc, check in FILE_RULES:
            if check(text):
                hits.append({"rule": rid, "sev": sev, "desc": desc,
                             "file": str(path.relative_to(root)), "line": 1, "code": "(arquivo)"})
        for n, line in enumerate(lines, 1):
            s = line.strip()
            if s.startswith(("//", "*", "/*")):
                continue
            for rid, sev, desc, rx in RULES:
                if rid == "plural-fixed" and re.search(r"(===|==|>|<)\s*1\b|plural", line):
                    continue
                if rx.search(line):
                    hits.append({"rule": rid, "sev": sev, "desc": desc,
                                 "file": str(path.relative_to(root)), "line": n, "code": s[:140]})
    return hits


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    root = Path(sys.argv[1]).resolve()
    if not root.is_dir():
        print(f"erro: diretório não encontrado: {root}", file=sys.stderr)
        sys.exit(2)
    if next(source_files(root), None) is None:
        print(f"erro: nenhum arquivo {'/'.join(sorted(EXTS))} varrido em {root}; nada foi analisado", file=sys.stderr)
        sys.exit(2)
    hits = scan(root)
    if "--json" in sys.argv:
        print(json.dumps(hits, ensure_ascii=False, indent=1))
        return
    order = {"alta": 0, "media": 1, "baixa": 2}
    by_rule = {}
    for h in hits:
        by_rule.setdefault(h["rule"], []).append(h)
    for rid, hs in sorted(by_rule.items(), key=lambda kv: order[kv[1][0]["sev"]]):
        print(f"\n[{hs[0]['sev']}] {rid}: {hs[0]['desc']} ({len(hs)})")
        for h in hs[:15]:
            print(f"  {h['file']}:{h['line']}  {h['code']}")
        if len(hs) > 15:
            print(f"  ... +{len(hs) - 15}")
    print(f"\n{len(hits)} pistas. Confirme cada uma antes de chamar de bug.")


if __name__ == "__main__":
    main()
