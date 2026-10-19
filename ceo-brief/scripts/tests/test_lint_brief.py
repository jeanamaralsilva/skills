import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import lint_brief  # noqa: E402


def rules(text, max_words=250):
    return [rule for _, rule, _ in lint_brief.lint(text, max_words)]


def test_clean_brief_passes():
    text = "**Resumo:** semana boa. O pagamento por Pix está no ar para os clientes (#10).\n\n**Decisão sua:** nenhuma."
    assert rules(text) == []


def test_flags_jargon_em_dash_and_leaks():
    found = rules("Fizemos deploy do PR — tudo certo. Avise fulano@empresa.com.")
    assert "jargon" in found and "em-dash" in found and "leak" in found


def test_ignores_code_and_urls_for_jargon():
    assert rules("Veja `deploy.yml` e https://example.com/pull/1") == []


def test_leak_is_caught_even_inside_code_block():
    assert rules("```\nghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123\n```") == ["leak"]


def test_long_sentence_and_word_budget():
    long_sentence = " ".join(["palavra"] * 30) + "."
    found = rules(long_sentence, max_words=20)
    assert "long-line" in found and "too-long" in found
