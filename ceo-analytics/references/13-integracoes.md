# Integrações: quem faz o quê

A `ceo-analytics` decide **o quê** e **por quê**. As outras skills fazem o **como**. Não copie as regras delas para cá: chame a skill quando o momento chegar.

| Situação | Chamar | Por quê |
|---|---|---|
| Repo INFLEET (remote `infleet/`) | `infleet-herads` | Componentes e tokens do HeraDS; gap vira pedido ao time de design |
| Cor, fonte ou logo INFLEET | `infleet-brandbook` | Paleta e contraste já medidos |
| Implementar tela igual à referência | `pixel-perfect` | A fidelidade vira número, não opinião |
| Subir a mudança | `send-pr` | Checks, vídeo antes/depois, texto sem marca de IA |
| Repo fora da INFLEET sem DS | `ui-ux-pro-max` | Base de estilos, paletas e pares de fonte |
| Auditoria WCAG profunda | `design:accessibility-review` | Checklist completo de acessibilidade |
| Texto de botão, erro ou empty state | `design:ux-copy` | Microcopy |
| Texto final do relatório ou do PR | `infleet:no-ai-slop` | Tira as marcas de texto gerado |
| Nome de variável ou componente novo | `infleet:clean-code` | Nomes em inglês, sem abreviação |

## Ordem típica de uma tela nova

1. `ceo-analytics`: mapa, diagnóstico, benchmark e propostas. O Jean aprova uma.
2. `infleet-herads` ou o DS do repo: quais componentes usar.
3. `pixel-perfect`: implementa contra a proposta aprovada e mede.
4. `send-pr`: sobe com a evidência.

## Ordem típica de um ajuste

1. `ceo-analytics` com `09-estabilidade-de-tela.md`: baseline e região.
2. Edição mínima.
3. Diff visual.
4. `send-pr`.

## Projetos read-only

Quando o Jean analisa um repo que não é dele (ex.: WAYUP), nada é escrito no repo e nenhum PR é aberto. O relatório fica no chat ou num arquivo fora do repo. As convenções do repo (`CLAUDE.md`) continuam valendo nas propostas.
