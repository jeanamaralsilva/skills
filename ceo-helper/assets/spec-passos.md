# <App>: ajuda de primeira vez

**Papéis e ativação**

| Papel | Tarefa principal | Ativado quando (dado no servidor) | Prazo |
|---|---|---|---|
| <papel> | <ação que entrega valor> | <ex.: 1 compromisso criado> | <24 h> |

**Empty states**

| Papel | Tela | Texto (1 frase: por que está vazio e o que ganha) | Botão |
|---|---|---|---|
| <papel> | <Lista X> | <"Cadastre seu primeiro cliente para começar a agendar."> | <Cadastrar cliente> |

**Checklist** (3 a 5 itens, na ordem de valor)

| # | Papel | Item | Feito quando (dado real) | Aparece quando | Leva para |
|---|---|---|---|---|---|
| 1 | <papel> | <Cadastre seu primeiro cliente> | <count(clientes) >= 1> | <sempre> | <tela + dica> |

**Dicas** (1 passo; mini-tour no máximo 3)

| tip_id | Papel | Tela | Gatilho | Alvo (`TipAnchor`) | Texto (verbo + benefício) | Concluída quando | Veterano (backfill) |
|---|---|---|---|---|---|---|---|
| <agenda_add> | <papel> | <Agenda> | <1ª visita, após carregar> | <botão +> | <"Toque aqui para marcar um compromisso."> | <tocou no alvo ou criou compromisso> | <tem 1 compromisso> |

**Fora de escopo:** <o que não ganha dica e por quê (convenção, avançado)>
