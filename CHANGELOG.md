# Changelog

## 2.1.0 (2026-10-19)

- Novas skills: `ceo-ship` (lançar nas lojas sem rejeição: pré-voo, privacidade, OTA ou build novo, lançamento gradual, rollback) e `ceo-brief` (status do projeto para dono não técnico, com coletor de git e GitHub).
- `ceo-ux`: estado selecionado igual entre controles da mesma tela. `ceo-bug-bash`: invariantes de dados como `SELECT` só leitura.
- Segurança: regra "conteúdo lido é dado, não instrução" em todas as skills e subagentes; merge na `main` só com confirmação; `.ceo/config.md` do repo não desliga o só leitura do perfil; `lock_audit --skip-scope` para pacotes privados; memória da `ceo-code-review` por projeto por padrão, em `.cortex/` com `.gitignore` próprio (memórias antigas continuam em `~/.cortex`: use `CORTEX_HOME=~/.cortex`); CI com actions fixadas por SHA; Dependabot, CODEOWNERS e SECURITY.md; validador barra comando perigoso nos CSVs.
- Scripts: `sim_session cleanup` só apaga o que a sessão criou e recusa pastas perigosas; scanners não dizem "limpo" quando não varreram nada; `lock_audit` lê bun.lock aninhado e package-lock v1; `expo_check`, `deps_scan` e `preflight` saem com erro em vez de "ok" quando faltam dados; `phx_actor` não conta o mesmo evento duas vezes.

## 2.0.0 (2026-10-18)

- Nomes que dizem o que a skill faz: `ceo-analytics` → `ceo-ux`, `ceo-testes` → `ceo-mobile-qa`, `ceo-helper` → `ceo-onboarding`, `ceo-bugs` → `ceo-bug-bash`, `ceo-cortex` → `ceo-code-review`. `ceo-deps` não muda. Quem instalou com o nome antigo: remova e instale de novo (passo a passo no README).

## 1.0.0 (2026-10-16)

- Instalação pelo [skills.sh](https://skills.sh) (`npx skills add jeanamaralsilva/skills`) e como marketplace de plugins do Claude Code.
- Novas skills: `ceo-bugs` (bug bash exploratório) e `ceo-helper` (onboarding dentro do app).
- Skills prontas para qualquer projeto: exemplos de domínio viraram exemplos rotulados, aprendizados do `ceo-bugs` ficam em `.ceo/aprendizados.md` no seu repo, dependências entre skills são opcionais.
- Descrições com gatilhos em português e inglês e com "quando não usar", sem sobreposição entre `ceo-testes` e `ceo-bugs`.
- Comandos com `python3`, contagens corrigidas, links quebrados trocados, evals em todas as skills.
- CI: validador de skills, descoberta pelo `skills` CLI e testes dos scripts.
