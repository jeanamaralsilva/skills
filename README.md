# skills

Skills do Jean para o Claude (Cowork e Claude Code).

## ceo-analytics

Designer de produto sênior em forma de agente. Recebe um app (código, app rodando ou design no Pencil/Figma) e entrega:

- **Mapa do app:** telas, abas e fluxos, com o objetivo de cada tela e o que cada botão faz.
- **Diagnóstico de UI/UX:** heurísticas de Nielsen e Laws of UX. Cada achado tem severidade de P0 a P3 e evidência com `arquivo:linha`.
- **Benchmark de mercado:** só fontes gratuitas, testadas uma a uma, e o que os usuários elogiam nas reviews.
- **Propostas de tela:** 2 ou 3 hipóteses, com todos os estados (loading, vazio, erro, offline, sucesso). iOS 26 com Liquid Glass só na navegação e Android com Material 3 Expressive.
- **Fluxo no Pencil:** pontos de toque numerados e setas até a tela de destino.

Antes de começar, ela lê a conversa e as decisões do repo. Responde curto, no formato de dono para CEO, e não mexe no que não foi pedido.

```
ceo-analytics/
├── SKILL.md       roteador: fases 0 a 5 e regras
├── references/    16 guias lidos sob demanda
├── data/          6 CSVs com fonte (heurísticas, anti-padrões, componentes, 39 apps, fontes de mercado, libs de UI)
├── scripts/       map_routes, search, contrast, lint_report + testes
├── agents/        briefings de subagentes
├── assets/        templates de relatório e proposta
└── evals/         casos de teste
```

## Instalar

Copie a pasta `ceo-analytics/` para `~/.claude/skills/` ou instale o pacote `.skill` pelo app do Claude.

## Testar

```bash
cd ceo-analytics && python3 -m pytest scripts/tests -q
```
