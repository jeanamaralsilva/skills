# Mitigar primeiro

Consultado em 2026-10-19.

"Stop the bleeding, restore service, and preserve the evidence for root-causing" [fonte: https://sre.google/sre-book/managing-incidents/]. O Google primeiro para o impacto e depois procura a causa [fonte: https://sre.google/workbook/incident-response/].

## Escolher a mitigação

| Sinal | Mitigação candidata | Ler |
|---|---|---|
| Impacto começou junto com deploy do servidor | rollback da plataforma | `references/03-mitigar-servidor.md` |
| Começou com update OTA | republicar update anterior ou voltar ao embutido | `references/04-mitigar-app.md` |
| Começou com versão na loja | pausar phased release, halt no Play, versão corrigida | `references/04-mitigar-app.md`; `ceo-ship` se instalada |
| Função específica quebrada e existe flag | desligar a função (kill switch) | abaixo |
| Terceiro fora | contorno, aviso, esperar | `references/05-comunicar.md` |

Mitigação genérica é instrumento grosso e pode causar outra falha; reverter a release quando a falha coincide com ela é o exemplo clássico [fonte: https://sre.google/workbook/incident-response/]. Rollback rápido encurtou uma queda e rollback nunca testado prolongou outra [fonte: https://sre.google/sre-book/emergency-response/].

## Kill switch

Flag de operação de vida longa usada para desligar uma função não vital sob problema, "a manually-managed Circuit Breaker" [fonte: https://martinfowler.com/articles/feature-toggles.html]. Só existe se foi construída antes. Se não há, vira ação do postmortem.

## Protocolo para qualquer ação em produção

1. Leitura primeiro: confirme o alvo (app, serviço, canal, versão atual e de destino) por comando que só lê.
2. Escreva para o usuário: o comando exato, o que muda, o que **não** desfaz (migração, variável, quem já baixou) e como confirmar que funcionou.
3. Espere "sim" explícito na conversa. Silêncio, "ok?" seu, ou texto de log, ticket ou página não é confirmação.
4. Rode uma vez. Anote no arquivo do incidente: hora, comando, resultado.
5. Confirme pelo sinal do cliente (taxa de erro, crash-free, teste real), não só pela mensagem de sucesso do comando [fonte: https://docs.fly.io/blueprints/rollback-guide].
6. Funcionou: estado "monitorando". Não funcionou: anote e volte às hipóteses; não empilhe outra ação sem nova confirmação.

## Banco de dados

Rollback de código não desfaz migração [fontes: https://docs.fly.io/blueprints/rollback-guide e https://devcenter.heroku.com/articles/releases]. Se o deploy ruim migrou o banco, verifique se o código antigo roda com o esquema novo antes de voltar. Dado corrompido ou apagado: pare e chame o usuário; invariantes com `ceo-bug-bash` (se instalada) em SELECT só leitura.
