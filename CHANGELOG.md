# Changelog

## 2.0.0 (2026-10-18)

- Nomes que dizem o que a skill faz: `ceo-analytics` → `ceo-ux`, `ceo-testes` → `ceo-mobile-qa`, `ceo-helper` → `ceo-onboarding`, `ceo-bugs` → `ceo-bug-bash`, `ceo-cortex` → `ceo-code-review`. `ceo-deps` não muda. Quem instalou com o nome antigo: remova e instale de novo (passo a passo no README).

## 1.0.0 (2026-10-16)

- Instalação pelo [skills.sh](https://skills.sh) (`npx skills add jeanamaralsilva/skills`) e como marketplace de plugins do Claude Code.
- Novas skills: `ceo-bugs` (bug bash exploratório) e `ceo-helper` (onboarding dentro do app).
- Skills prontas para qualquer projeto: exemplos de domínio viraram exemplos rotulados, aprendizados do `ceo-bugs` ficam em `.ceo/aprendizados.md` no seu repo, dependências entre skills são opcionais.
- Descrições com gatilhos em português e inglês e com "quando não usar", sem sobreposição entre `ceo-testes` e `ceo-bugs`.
- Comandos com `python3`, contagens corrigidas, links quebrados trocados, evals em todas as skills.
- CI: validador de skills, descoberta pelo `skills` CLI e testes dos scripts.
