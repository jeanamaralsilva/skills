# Persistência e servidor

Por que servidor: quem reinstala ou troca de aparelho volta a ver a mesma dica, e repetir para quem já viu é o antipadrão que a Apple manda evitar (https://developer.apple.com/design/human-interface-guidelines/onboarding). Cache local só para decidir sem esperar a rede.

## Dois tipos de estado

| Estado | Onde nasce | Grava? |
|---|---|---|
| Item do checklist feito | Derivado de dados que já existem (tem cliente? tem compromisso?) | Não. Calcule no servidor a cada leitura. |
| Dica vista, dispensada ou concluída; checklist fechado | Ação do usuário no app | Sim, por usuário e papel. |

Derivar em vez de gravar resolve veteranos de graça no checklist e evita estado que diverge dos dados.

## Schema sugerido

Um campo mapa no usuário (ou tabela própria se o app tem muitos papéis):

```
onboarding (jsonb, default {}):
{
  "<papel>": {
    "tips": { "<tip_id>": { "status": "seen|dismissed|done", "at": "<iso8601>" } },
    "checklist_dismissed_at": "<iso8601>|null",
    "tips_paused": false
  }
}
```

Postgres/Ecto: coluna `:map` com `default: %{}`, `null: false`. Migração precisa funcionar com as linhas que já existem (o default resolve).

## Endpoint

- Leitura: junto do perfil ou da home, para não custar um request a mais. Devolve `onboarding` do papel atual e `checklist: [{id, done, visible}]` já calculado.
- Escrita: `POST /me/onboarding/tips/:tip_id` com `{status}` e `POST /me/onboarding/checklist/dismiss`. `PUT` em "rever dicas" zera `tips` e `tips_paused` do papel.
- **Idempotente:** gravar o mesmo status de novo não muda nada. Status só avança (`seen` < `dismissed`/`done`), nunca volta, salvo o reset explícito. Atualize com merge atômico no banco (ex.: `jsonb_set` ou update dentro de transação com lock da linha), não leia-modifique-grave no app.
- **Autorização:** só o próprio usuário, só o papel que ele tem. `tip_id` validado contra uma lista conhecida (nada de chave livre crescendo o JSON).
- **Offline:** o app grava no cache local na hora e manda depois; repetir o envio é seguro por ser idempotente.

## Cache local

- MMKV (ou o storage que o app já usa) com chave por usuário e papel: `onboarding:<user_id>:<papel>`.
- Decisão de mostrar usa o cache; o servidor atualiza o cache quando o perfil chega. Em conflito, vale o status mais avançado.
- Logout limpa o cache daquele usuário. Troca de papel troca a chave.
- Primeiro acesso sem cache e sem resposta do servidor: não mostre dica. Esperar é melhor que repetir.

## Veteranos (backfill)

Antes de ligar as dicas em produção:

1. Para cada dica, defina a condição que prova que o usuário já sabe fazer aquilo (ex.: dica do "+" da agenda: tem 1 compromisso criado).
2. Rode o backfill (migração de dados ou job) marcando `done` nessas dicas para quem cumpre a condição. Idempotente, em lotes, sem travar a tabela.
3. Alternativa sem backfill: o servidor calcula na leitura e devolve a dica como `done` se a condição já vale. Mais simples, custa uma contagem por leitura (cacheie se pesar).
4. Teste com uma conta veterana real (cópia de staging) antes de lançar: ela não pode ver nada de "primeiro X".
