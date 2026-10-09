# Rubrica por tipo de tela

Toda tela é de um ou dois tipos. Cada tipo tem os erros que sempre aparecem. Antes de opinar, classifique a tela e passe pela lista do tipo: é isso que faz a análise sair completa na primeira vez, sem o CEO ter que apontar o que faltou. A base consultável é `data/screen-checks.csv` (SC01 a SC34, cada linha com fonte): `python scripts/search.py "<tema>" --domain screen-checks`.

## Classifique primeiro

| Tipo | Como reconhecer | Checks | Referência complementar |
|---|---|---|---|
| **Formulário** | campos para preencher e um botão de envio | SC01 a SC07 | erros: SC05; toggles: SC07 |
| **Tabela / painel de dados** | linhas e colunas, filtros, totais | SC08 a SC12, mais `19-navegacao-e-densidade.md` e `nav_audit.py` | dashboard: SC13 a SC15 |
| **Dashboard / métricas** | números grandes, gráficos, período | SC13 a SC15 | `dataviz` quando for construir o gráfico |
| **Lista / feed / cards** | itens repetidos, scroll | SC20, SC21, SC16, SC17 | mobile: `06-componentes-premium.md` (loading, empty) |
| **Detalhe / ficha** | um item, suas propriedades, ações | SC18, SC19 (ações destrutivas), SC30, SC31 | |
| **Busca e filtros** | campo de busca, chips, facetas | SC22, SC23, H23 | |
| **Navegação** | tab bar, menu, breadcrumb, header | SC24 a SC28, H21 a H25 | `19` para abas e camadas |
| **Modal / diálogo** | sobreposição que bloqueia | SC18, SC19 | |
| **Estado vazio / carregando / erro** | sem dado, spinner, falha | SC16, SC17, SC29, SC05 | `06` |
| **Onboarding / primeiro uso** | tutorial, permissões | SC32, SC33 | |
| **Configurações** | lista de opções e toggles | SC34, SC07 | |

Uma tela de auditoria financeira, por exemplo, é **tabela + navegação + busca e filtros**: três listas, não uma.

## Como usar na análise

1. Classifique (um ou dois tipos) e escreva isso no brief, não no relatório.
2. Rode cada check do tipo contra o que está na tela ou no código. Cada violação vira achado com `arquivo:linha` ou `[tela: X]` e o id do check (`SC08`), que já carrega a fonte.
3. O que passou não entra no relatório. "Formulário em uma coluna, ok" é ruído.
4. Severidade: perde dado ou bloqueia a tarefa (SC04, SC17, SC19 com destrutivo como padrão) é P1; custa cliques ou leitura (SC02, SC08, SC13) é P2; polimento (SC12, SC28) é P3.

## O que o check não cobre

- Se a tela faz sentido no produto (a tarefa certa está ali). Isso vem do mapa (`01`, `02`) e da conversa (`00`).
- Se o visual é bom. Isso é `07-anti-slop-visual.md` e `05-plataformas.md`.
- Se funciona. Isso é `ceo-testes`.

## Fontes

Todas verificadas em 09/10/2026, uma por linha do CSV. As principais: NN/g Website Forms Usability (2016), Placeholders Are Harmful (2014, rev. 2018), Data Tables: Four Major User Tasks (2022), Dashboards: Making Charts Easier (2017), Empty States in Complex Applications (2021), Modal & Nonmodal Dialogs (2017), Confirmation Dialogs (2018, rev. 2026), Mobile Subnavigation (2017), Cards (2016), Toggle-Switch Guidelines (2018), Breadcrumbs (2018, rev. 2026), Search: Visible and Simple (2001), Progress Indicators (2014), Error-Message Guidelines (2023), Tooltip Guidelines (2019), Icon Usability (2014), Infinite Scrolling (2022), Date-Input Fields (2017), Filter Categories and Values (2018), Sticky Headers (2021), Visual Hierarchy (2021), Onboarding Tutorials vs. Contextual Help (2023), Push Notifications (2018); Apple HIG Tab Bars (2026); Android Developers Navigation bar (2026); NN/g Customization Features report (sem data).
