# Os maiores ralos

Consultado em 2026-10-19. Ids entre colchetes estão em `data/levers.csv`, com fonte.

Ordem para olhar: o que cresce com o número de usuários primeiro, o que é fixo depois.

## Build na nuvem e CI
- **Build em todo push ou PR.** No EAS cada build de plano pago custa de US$1 (Android médio) a US$4 (iOS grande) depois do crédito do plano [EAS-GATILHO]. O inventário aponta `eas build` em `package.json` ou no CI. Corte: build só em tag ou na main, build de PR só com label, cancelar run repetida [CI-CONCURRENCY].
- **Mudança só de JavaScript virando build.** Use update pelo ar [EAS-UPDATE]; o MAU de update entra na conta do EAS acima da franquia.
- **Cache de build desligado** [EAS-CACHE].
- **Build local** para teste [EAS-LOCAL]: corta custo, custa tempo de máquina e não leva os segredos do EAS.
- **CI em macOS.** No GitHub o minuto de macOS custa cerca de 10 vezes o de Linux (0.062 contra 0.006 USD em 2026-10-19) [CI-LINUX]. Lint, teste de JavaScript e build Android não precisam de macOS.

## Servidor e banco
- **Máquina ligada sem tráfego.** Auto stop no Fly [FLY-AUTOSTOP], serviço que dorme na Railway [RW-SLEEP], plano que dorme no Render e no Heroku. Risco: primeira requisição lenta. Não use em quem recebe webhook de pagamento ou push agendado sem testar.
- **Máquina ou banco grande demais.** Compare uso de CPU e memória dos últimos 30 dias no painel com o tamanho contratado. Desça um degrau por vez, com janela de volta.
- **Volume e disco provisionados.** Cobram mesmo parados [FLY-AUTOSTOP]. Volume órfão de app apagado é ralo comum; apagar é irreversível.
- **Região.** Egress e máquina mudam por região; América do Sul costuma custar mais [FLY-REGIAO]. Mudar região mexe em latência e em dado pessoal (veja ceo-privacy se instalada).

## Tráfego e arquivos
- **Imagem e anexo servidos direto do bucket.** Egress de S3 para a internet sai mais caro que por CDN acima da franquia; CDN com plano fixo pode zerar o excedente [CDN].
- **Imagem sem redimensionar.** Mandar foto original para lista de miniaturas multiplica o egress. Corte no código (ceo-deps ou o time).
- **Arquivo velho no storage.** Lifecycle para classe mais barata [S3-LIFECYCLE].

## Logs e monitoramento
- **Log demais.** Log por GB ingerido (Datadog a partir de 0.10 USD por GB em 2026-10-19). Debug ligado em produção é o caso clássico.
- **Erro em loop enchendo o Sentry.** Teto de gasto [SENTRY-CAP]. Um bug pode consumir a cota do mês em horas.

## IA
Prompt longo repetido sem cache, modelo grande para tarefa simples, sem teto de gasto. Veja `05-ia.md`.

## Sem teto
Serviço com cobrança por uso e sem teto ou alerta é o risco de conta-surpresa: Vercel [VERCEL-BUDGET], Railway [RW-LIMIT], Supabase [SUPA-CAP], Firebase [FB-BUDGET], APIs de IA [IA-LIMITE]. Teto que derruba o serviço ao bater precisa de decisão do dono.
