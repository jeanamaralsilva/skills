# Integrações: quem faz o quê

A `ceo-analytics` decide **o quê** e **por quê**. As outras skills fazem o **como**. Não copie as regras delas para cá: chame a skill quando o momento chegar.

| Situação | Chamar | Por quê |
|---|---|---|
| Projeto com design system próprio | a skill em `design.ds_skill` da config | Componentes e tokens do time; gap vira pedido ao time de design |
| Cor, fonte ou logo da marca | a skill em `design.brand_skill` da config | Paleta e contraste já medidos |
| Implementar tela igual à referência | skill de fidelidade visual do time (ex.: `pixel-perfect`, se instalada) | A fidelidade vira número, não opinião |
| Subir a mudança | skill de PR em `fluxo.pr_skill` da config, ou `gh pr create` | Checks, vídeo antes/depois, texto sem marca de IA |
| Repo sem DS | `ui-ux-pro-max` | Base de estilos, paletas e pares de fonte |
| Auditoria WCAG profunda | `design:accessibility-review` | Checklist completo de acessibilidade |
| Texto de botão, erro ou empty state | `design:ux-copy` | Microcopy |
| Texto final do relatório ou do PR | skill de texto em `fluxo.texto_skill` da config, se houver | Tira as marcas de texto gerado |
| Nome de variável ou componente novo | `ceo-cortex` ou a skill de clean code do time | Nomes claros, sem abreviação |

Skills externas da comunidade (motion, Expo UI, HIG/M3, QA no device): `15-comunidade-e-ecossistema.md`.

## Ordem típica de uma tela nova

1. `ceo-analytics`: mapa, diagnóstico, benchmark e propostas. O CEO aprova uma.
2. O DS do projeto (`design.ds_skill`) ou o do repo: quais componentes usar.
3. Implementação contra a proposta aprovada, medida (skill de fidelidade, se houver).
4. PR com a evidência.

## Ordem típica de um ajuste

1. `ceo-analytics` com `09-estabilidade-de-tela.md`: baseline e região.
2. Edição mínima.
3. Diff visual.
4. PR.

## Projetos read-only

Quando o repo é read-only (na config ou porque não é do usuário), nada é escrito no repo e nenhum PR é aberto. O relatório fica no chat ou num arquivo fora do repo. As convenções do repo (`CLAUDE.md`) continuam valendo nas propostas.
