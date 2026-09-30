import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, SCRIPTS)

import contrast  # noqa: E402
import lint_report  # noqa: E402
import map_routes  # noqa: E402
import search  # noqa: E402

FIXTURES = os.path.join(HERE, "fixtures")


def test_contrast_black_on_white_is_21():
    assert round(contrast.contrast_ratio("#000000", "#FFFFFF"), 2) == 21.0


def test_contrast_short_hex_and_aa_threshold():
    ratio = contrast.contrast_ratio("#777", "#fff")
    assert 4.4 < ratio < 4.5
    assert contrast.verdict(ratio, large_text=False)["AA"] is False
    assert contrast.verdict(ratio, large_text=True)["AA"] is True


def test_lint_flags_em_dash_jargon_vague_and_unsourced_number():
    text = "Tela robusta — ok\nPrecisa melhorar a acessibilidade\nConversao caiu 30%\n"
    rules = {rule for _, rule, _ in lint_report.lint(text, max_words=600)}
    assert {"em-dash", "jargon", "vague-fix", "unsourced-number"} <= rules


def test_lint_accepts_tagged_number_and_finding_with_evidence():
    text = (
        "Contraste do botao 3.1:1 [medido]\n"
        "- **P1** Botao sem estado de loading `app/(tabs)/index.tsx:42`\n"
    )
    assert lint_report.lint(text, max_words=600) == []


def test_lint_flags_finding_without_evidence_and_ignores_code_blocks():
    text = "- **P0** Fluxo confuso\n```\nrobust — 30%\n```\n"
    rules = [rule for _, rule, _ in lint_report.lint(text, max_words=600)]
    assert rules == ["no-evidence"]


def test_lint_word_budget():
    rules = [rule for _, rule, _ in lint_report.lint("palavra " * 50, max_words=10)]
    assert rules == ["too-long"]


def test_map_routes_expo_router():
    screen_map = map_routes.build_map(os.path.join(FIXTURES, "expo-app"))
    screens = {r["route"] for r in screen_map["expo-router"] if r["kind"] == "screen"}
    assert screens == {"/", "/lesson/[id]", "/profile"}
    assert "expo-router" in screen_map["detected"]
    profile = next(r for r in screen_map["expo-router"] if r["route"] == "/profile")
    assert profile["target"] == os.path.join("src", "screens", "lesson-screen.tsx")


def test_map_routes_react_navigation():
    screen_map = map_routes.build_map(os.path.join(FIXTURES, "rn-nav"))
    names = {(s["name"], s["component"]) for s in screen_map["react-navigation"]}
    assert names == {("Home", "HomeScreen"), ("Profile", "ProfileScreen"), ("Moderation", "ModerationScreen")}
    assert {n["type"] for n in screen_map["navigators"]} == {"NativeStack", "BottomTab"}
    assert len(screen_map["navigators"]) == 4


def test_map_routes_cli_exit_code_when_nothing_found(tmp_path):
    result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "map_routes.py"), str(tmp_path)])
    assert result.returncode == 2


def test_search_ranks_matching_row_first(tmp_path):
    (tmp_path / "components.csv").write_text(
        "pattern,when\nBottom sheet,interacao curta com botao fechar\nTab bar,navegacao principal visivel\n",
        encoding="utf-8",
    )
    rows = search.load_rows(str(tmp_path), ["components"])
    results = search.rank("sheet fechar", rows, limit=5)
    assert results[0][2]["pattern"] == "Bottom sheet"
    assert len(results) == 1


def test_search_normalizes_accents(tmp_path):
    (tmp_path / "heuristics.csv").write_text("name\nNavegação visível\n", encoding="utf-8")
    results = search.rank("navegacao", search.load_rows(str(tmp_path), ["heuristics"]), limit=5)
    assert len(results) == 1


def test_data_csvs_are_well_formed_and_sourced():
    data_dir = os.path.join(SCRIPTS, "..", "data")
    for domain in search.DOMAINS:
        rows = search.load_rows(data_dir, [domain])
        assert rows, f"{domain}.csv missing or empty"
        ids = [row["id"] for _, row in rows]
        assert len(ids) == len(set(ids)), f"duplicate id in {domain}.csv"
        for _, row in rows:
            assert None not in row and all(v != "" for v in row.values()), f"bad row in {domain}: {row}"
            if "source" in row:
                assert row["source"].startswith("https://"), f"unsourced row {row['id']}"


def test_every_file_cited_in_skill_md_exists():
    import re as _re
    skill_root = os.path.join(SCRIPTS, "..")
    skill_md = open(os.path.join(skill_root, "SKILL.md"), encoding="utf-8").read()
    cited = set(_re.findall(r"`((?:references|agents|assets|scripts|data)/[\w./-]+)`", skill_md))
    assert cited, "SKILL.md cites no bundled file"
    missing = [path for path in cited if not os.path.exists(os.path.join(skill_root, path))]
    assert missing == []


def test_short_reference_names_in_skill_md_resolve():
    import re as _re
    skill_root = os.path.join(SCRIPTS, "..")
    skill_md = open(os.path.join(skill_root, "SKILL.md"), encoding="utf-8").read()
    names = {f for f in os.listdir(os.path.join(skill_root, "references"))}
    for short in set(_re.findall(r"`(\d\d-[\w-]+\.md)`", skill_md)):
        assert short in names, short
    for number in set(_re.findall(r"`(\d\d)`", skill_md)):
        assert any(n.startswith(number + "-") for n in names), number


def test_report_template_example_passes_lint():
    example = (
        "# WAYUP: análise UI/UX\n"
        "**Veredito:** fluxo de treino funciona. Maior alavanca: registrar carga.\n"
        "- **P0** Carga não persiste → salvar por série `src/features/workout/useSets.ts:41`\n"
        "- **P1** Botão Salvar com 3.1:1 [medido] → usar token de texto primário [tela: Treino]\n"
    )
    assert lint_report.lint(example, max_words=600) == []
