# CEO skills

[![CI](https://github.com/jeanamaralsilva/skills/actions/workflows/ci.yml/badge.svg)](https://github.com/jeanamaralsilva/skills/actions/workflows/ci.yml)
[![skills.sh](https://img.shields.io/badge/skills.sh-jeanamaralsilva%2Fskills-black)](https://skills.sh/jeanamaralsilva/skills)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

```bash
npx skills add jeanamaralsilva/skills
```

> **English:** six agent skills (Claude Code, Cursor, Codex, Gemini CLI, Copilot and any agent that reads `SKILL.md`) that look after a mobile app and its server the way a technical owner would: UX review, dependency audit, senior code review, mobile QA, bug bash and in-app onboarding. Every data row cites its source. The skills are written in Brazilian Portuguese; agents follow them fine in any language and reply in yours.

Seis skills para o Claude (Cowork, Claude Code e qualquer agente que leia `SKILL.md`) que cuidam de um app mobile com servidor como um dono técnico cuidaria: UX, dependências, código, testes e ajuda de primeira vez. Cada uma reporta curto, no tom de quem responde ao CEO: o que está bom, o que quebrou, o que já foi resolvido e o que só o dono decide. Sem narrar processo, sem inventar resultado, sem esconder erro ou risco de segurança.

Nenhuma skill depende de um projeto específico. O que varia por projeto (repos, read-only, limites da máquina, design system, papéis de teste, credenciais por variável de ambiente) vai em `.ceo/config.md` na raiz do repo. Modelo em qualquer `*/assets/ceo-config.example.md`.

| Skill | Pergunta que responde | Tamanho |
|---|---|---|
| [ceo-analytics](ceo-analytics/) | O app está bom de usar? O que propor? Como fica a animação no iOS e no Android? | 21 guias, 8 CSVs (heurísticas, anti-padrões, componentes, 43 apps de referência, fontes de mercado, libs de UI, 45 padrões de motion, 34 checks por tipo de tela), 5 scripts |
| [ceo-deps](ceo-deps/) | As dependências estão seguras, compatíveis e mantidas? | 14 guias, 105 checks com fonte em 12 ecossistemas, 31 licenças, incidentes reais, 6 scripts |
| [ceo-cortex](ceo-cortex/) | O código está certo, limpo e sem repetição? | guias por linguagem (Elixir com as Iron Laws do phxagents, RN, TS/Node, Python, Go, Kotlin, Swift, Java, SQL), memória entre sessões, detector de duplicação |
| [ceo-testes](ceo-testes/) | O app funciona de verdade, com dois usuários, sem rede, depois do background? Onde está o bug do vídeo que o cliente mandou? | 13 guias, 50 bugs reproduzíveis, 66 receitas de comando, 26 tours, 5 scripts, 7 flows Maestro |
| [ceo-bugs](ceo-bugs/) | Onde o app quebra ou fica feio antes do cliente ver? | 6 guias + pesquisa com fonte, 16 charters, scanner de "feio" (moeda, plural, inglês, erro técnico), aprendizados por rodada em `.ceo/aprendizados.md` do seu repo |
| [ceo-helper](ceo-helper/) | O usuário novo sabe o que fazer sem incomodar quem já usa? Como implementar empty state, checklist e dica com destaque? | 8 guias, 28 padrões e antipadrões com fonte, 7 libs RN avaliadas, 2 templates |

## ceo-analytics

Designer de produto sênior em forma de agente. Recebe um app (código, app rodando ou design no Pencil/Figma) e entrega:

- **Mapa do app:** telas, abas e fluxos, com o objetivo de cada tela e o que cada botão faz.
- **Diagnóstico de UI/UX:** heurísticas de Nielsen e Laws of UX. Cada achado tem severidade de P0 a P3 e evidência com `arquivo:linha`.
- **Benchmark de mercado:** só fontes gratuitas, testadas uma a uma, e o que os usuários elogiam nas reviews.
- **Propostas de tela:** 2 ou 3 hipóteses, com todos os estados (loading, vazio, erro, offline, sucesso). iOS 26 com Liquid Glass só na navegação e Android com Material 3 Expressive.
- **Motion e micro-interações:** ícone de aba que pulsa, gradiente lento atrás do ícone, sheet que acompanha o dedo, transições; com API por plataforma, duração, Reduce Motion e custo no Android.
- **Fluxo no Pencil:** pontos de toque numerados e setas até a tela de destino.

## ceo-deps

Dono técnico das dependências de um app inteiro, em um ou vários repos (ex.: mobile Expo + server Phoenix):

- **Inventário multi-repo:** gerenciadores, lockfiles (inclusive os ignorados pelo git), toolchain, deps por git, overrides, bots, CI e risco de OTA (`runtimeVersion`).
- **Segurança e supply chain:** audit de cada ecossistema, versões exatas do lock contra o OSV e defesas contra pacote malicioso (cooldown, `--ignore-scripts`, Actions fixadas por SHA).
- **Versões e compatibilidade:** Expo SDK (`bundledNativeModules.json`), duplicata de módulo nativo, regressão de Hermes e matriz Elixir/OTP.
- **Duplicadas e sem uso, licenças (SaaS e lojas), acoplamento, serviços externos e ciclo de vida.**
- **Manter:** aplica o que é seguro em branch e verifica em degraus, com o build nativo na nuvem (EAS) e no CI quando a máquina não aguenta.

## ceo-cortex

Revisão e escrita de código no nível de engenheiro sênior, com memória entre sessões (`cortex`), detector de duplicação e mapa de símbolos. Guias de armadilhas por linguagem. Antes se chamava code-cortex.

## ceo-testes

QA de app mobile (iOS primeiro) que acha e prova bug:

- **Mapa e matriz:** `map_flows.py` lista telas, botões e estados e expande cada ação em feliz, triste, duplo toque, sem rede, background no meio, deep link frio. `map_realtime.py` pareia os eventos do servidor Phoenix com os listeners do app e aponta os gaps.
- **Dois usuários de verdade:** um simulador mais `phx_actor.mjs` (cliente Phoenix Channels sem dependências) como segundo papel. Dois simuladores só quando precisa.
- **Estresse:** Toxiproxy (latência, timeout, reset), ciclo de vida, permissões, fonte grande, memória, carga com k6.
- **Evidência:** `video_frames.py` corta o vídeo do cliente nas mudanças de cena; TestFlight feedback e crash logs pela API do App Store Connect; xctrace para hitches.
- **Limpeza:** tudo que a sessão cria tem prefixo `ceo-` e é apagado no fim (`sim_session.py cleanup`).
- **Servidor:** testes ExUnit de canal com dois clientes, corridas, jobs e propriedades antes de abrir simulador.

## ceo-helper

Ajuda de primeira vez (onboarding dentro do app) para app mobile Expo/React Native:

- **Brief e ativação:** papéis, tarefa principal de cada um e o dado no servidor que prova que o usuário foi ativado.
- **Três camadas, nesta ordem:** empty state que ensina, checklist de primeiros passos marcado por dados reais, dica de 1 passo com destaque na hora certa. Nada de carrossel de boas-vindas.
- **Regras com fonte:** 1 dica automática por sessão, nunca ao abrir o app, alvo sempre tocável, sempre dá para pular e rever, tour de no máximo 3 passos.
- **Implementação:** componente próprio com máscara SVG, `measureInWindow` e Reanimated, sem módulo nativo novo (sai por OTA); comparação com as libs e plano B.
- **Servidor e veteranos:** estado por usuário e papel, endpoint idempotente, cache local e backfill para quem já usa não ver "primeiro X".
- **Medir e testar:** eventos, ativação em 24 h e 7 dias, matriz de simulador com VoiceOver, Reduzir Movimento, fonte grande e Android edge-to-edge.

## Instalar

**Qualquer agente (Claude Code, Cursor, Codex, Gemini CLI, Copilot, OpenCode e outros)** pelo [skills.sh](https://skills.sh):

```bash
npx skills add jeanamaralsilva/skills                         # escolhe skills e agentes no menu
npx skills add jeanamaralsilva/skills --skill ceo-analytics   # só uma
npx skills add jeanamaralsilva/skills --all -g                # todas, em todos os agentes, para o usuário
npx skills add jeanamaralsilva/skills --list                  # só listar
npx skills update                                             # atualizar depois
```

**Claude Code como plugin** (um passo, Claude Code 2.1.275+; atualiza junto com o marketplace):

```
/plugin install ceo-analytics --marketplace jeanamaralsilva/skills
/plugin install ceo-deps --marketplace jeanamaralsilva/skills
/plugin install ceo-cortex --marketplace jeanamaralsilva/skills
/plugin install ceo-testes --marketplace jeanamaralsilva/skills
/plugin install ceo-bugs --marketplace jeanamaralsilva/skills
/plugin install ceo-helper --marketplace jeanamaralsilva/skills
```

Em versões anteriores: `/plugin marketplace add jeanamaralsilva/skills` e depois `/plugin install ceo-analytics@ceo-skills`.

**Manual:** copie a pasta da skill para `~/.claude/skills/` (ou `ln -s <este repo>/<skill> ~/.claude/skills/<skill>`).

`ceo-bugs` usa a receita de simulador da `ceo-testes`; instale as duas juntas.

### Configurar no seu projeto

Copie `ceo-testes/assets/ceo-config.example.md` para `.ceo/config.md` na raiz do seu repo e preencha o que souber (repos, o que é só leitura, limites da máquina, papéis de teste). Credenciais vão por variável de ambiente, nunca no arquivo.

### Requisitos

Python 3 para os scripts (só biblioteca padrão). Cada skill diz no `SKILL.md` o que mais usa (Maestro, simulador iOS, `gh`, Node) e funciona em modo reduzido quando falta algo.

## Testar

```bash
python3 scripts/validate_skills.py   # frontmatter, limites, links internos e marketplace
pip install pytest pyyaml
for t in */scripts/tests; do (cd "$(dirname "$t")" && python3 -m pytest tests -q); done
```

O CI roda os dois em todo push e PR.

## Contribuir

Cada linha de dado (`data/*.csv`) tem uma coluna `source` com a URL. Achado sem fonte não entra. Scripts têm teste. Skill nova: pasta com `SKILL.md` (nome igual ao da pasta) e entrada em `.claude-plugin/marketplace.json`; o `validate_skills.py` cobra os dois. Nome de projeto, pessoa ou empresa não entra nas skills: o que é seu vai em `.ceo/config.md`.
