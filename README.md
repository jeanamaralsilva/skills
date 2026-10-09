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

## ceo-deps

Dono técnico das dependências de um app inteiro, em um ou vários repos (ex.: mobile Expo + server Phoenix):

- **Inventário multi-repo:** gerenciadores, lockfiles (inclusive os ignorados pelo git), toolchain, deps por git, overrides, bots, CI e risco de OTA (`runtimeVersion`).
- **Segurança e supply chain:** audit de cada ecossistema, versões exatas do lock contra o OSV e defesas contra pacote malicioso (cooldown, `--ignore-scripts`, Actions fixadas por SHA).
- **Versões e compatibilidade:** Expo SDK (`bundledNativeModules.json`), duplicata de módulo nativo, regressão de Hermes e matriz Elixir/OTP.
- **Duplicadas e sem uso, licenças (SaaS e lojas), acoplamento, serviços externos e ciclo de vida.**
- **Manter:** aplica o que é seguro em branch e verifica em degraus, com o build nativo na nuvem (EAS) e no CI, sem buildar no Mac.

Scripts: `detect_stack.py`, `expo_check.py`, `lock_audit.py`, `deps_scan.py`. Dados: 105 checks com fonte (JS/Expo, Elixir e mais 10 linguagens), 31 licenças, 23 grupos de libs duplicadas e incidentes reais.

## ceo-cortex

Revisão e escrita de código no nível de engenheiro sênior, com memória entre sessões (`cortex`), detector de duplicação e mapa de símbolos. Tem guias de armadilhas por linguagem (Elixir com as 26 Iron Laws do phxagents, React Native, React, TypeScript/Node, Python, Go, Kotlin/Android, Swift/iOS, Java, SQL e desktop). Antes se chamava code-cortex.

## Instalar

Copie a pasta da skill para `~/.claude/skills/` (ou crie um link: `ln -s ~/orca/skills/<skill> ~/.claude/skills/<skill>`) ou instale o pacote `.skill` pelo app do Claude.

## Testar

```bash
for s in ceo-analytics ceo-deps ceo-cortex; do (cd $s && python3 -m pytest scripts/tests -q); done
```
