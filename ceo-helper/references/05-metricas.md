# Métricas

Métrica de sucesso é a ação de ativação acontecer mais cedo e mais vezes, não "viu a dica". Chameleon e Produktly medem conclusão de tour; isso é meio, não fim.

## Eventos

| Evento | Propriedades |
|---|---|
| `tip_shown` | `tip_id`, `role`, `trigger` (`auto`/`user`), `app_version` |
| `tip_dismissed` | `tip_id`, `role`, `how` (`button`/`outside`/`back`/`skip_all`) |
| `tip_target_tapped` | `tip_id`, `role` |
| `tips_reset` | `role` |
| `checklist_item_done` | `item_id`, `role`, `hours_since_signup` |
| `checklist_dismissed` | `role`, `items_done` |
| `checklist_completed` | `role`, `hours_since_signup` |
| `activation` | `role`, `hours_since_signup` (disparado pelo servidor quando o dado de ativação nasce, se a ferramenta aceita evento de servidor) |

Use o client de analytics que o app já tem. Sem analytics, as mesmas perguntas saem do banco (datas de criação dos dados vs data de cadastro).

## Perguntas para o painel

1. % de usuários novos ativados em 24 h e em 7 dias, antes e depois do lançamento, por papel.
2. Tempo mediano do cadastro até a ativação.
3. Por dica: `tip_target_tapped / tip_shown` (a dica levou à ação?) e `tip_dismissed how=skip_all` (irritou?).
4. Checklist: qual item trava (maior queda entre item N e N+1).
5. Retenção D1 e D7 de quem ativou vs quem não ativou (correlação, não causa).

## Comparação justa

- Antes/depois só vale com a mesma origem de usuários e sem outra mudança grande no período. Diga isso no relatório.
- Se der, feature flag com metade dos novos sem as dicas por 2 a 4 semanas [estimado]. Amostra pequena (poucas dezenas de cadastros por semana) não dá significância: reporte como tendência.
- Referência de mercado para D1/D7 é fonte secundária (https://www.plotline.so/blog/retention-rates-mobile-apps-by-industry). Use só como ordem de grandeza.
