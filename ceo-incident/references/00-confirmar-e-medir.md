# Confirmar, medir e classificar

Consultado em 2026-10-19.

## Declare cedo

- Declare incidente se precisa de mais alguém, se o cliente vê, ou se seguiu sem solução após 1 h de análise. Melhor declarar cedo e fechar rápido do que tarde [fonte: https://sre.google/sre-book/managing-incidents/].
- "Declare incidents early and often" [fonte: https://sre.google/workbook/incident-response/].
- Na prática desta skill: abrir `.ceo/incidents/AAAA-MM-DD.md` (`assets/linha-do-tempo-template.md`) é declarar. Custa um minuto.

## Confirmar (5 minutos, só leitura)

1. **O que o cliente não consegue fazer?** Em palavras dele. "Abro o app e fecha" vale mais que "erro 500".
2. **É real e é agora?** Um relato isolado pode ser aparelho, rede ou conta. Procure um segundo sinal: crash reporting, log do servidor, outro cliente, seu próprio teste.
3. **Desde quando?** O primeiro erro no log ou no crash, não a hora da reclamação. Anote os dois: `inicio` e `detectado`.
4. **Quem e quantos?** Plataforma (iOS, Android, web), versão do app, update OTA, região, tipo de conta. Número com origem: "Sentry: crash-free users caiu de X para Y", "log: N erros 500 em 10 min". Sem número, diga "não verificado".
5. **O que mudou perto do início?** Deploy do servidor, update OTA, versão na loja, migração, variável, terceiro fora. A coincidência com uma mudança é a primeira candidata a reverter [fonte: https://www.atlassian.com/incident-management/handbook/incident-response].

## Severidade

`data/severidade.csv`. Resumo:

| Nível | Quando | Exemplo |
|---|---|---|
| SEV1 | muitos clientes, perda severa, dado exposto | app fecha ao abrir para a maioria |
| SEV2 | uso muito prejudicado para muitos | login fora no Android |
| SEV3 | minoria afetada ou risco de escalar | uma tela quebrada |
| SEV4 | exige ação, não impede uso | lentidão, job falhando |

Critérios da PagerDuty [fonte: https://response.pagerduty.com/before/severity_levels/]. Na dúvida, o nível mais alto; a severidade é revista no postmortem, não discutida durante (mesma fonte).

## Papéis quando é uma pessoa só

O SRE Book separa comando, operação, comunicação e planejamento [fonte: https://sre.google/sre-book/managing-incidents/]. A PagerDuty tem comandante, escriba e ligação com cliente e com a empresa [fonte: https://response.pagerduty.com/before/different_roles/]. Quem acumula tudo (dono técnico com IA):

- **Comando:** o usuário decide. A skill propõe e pede confirmação.
- **Registro:** a skill anota cada fato na hora no arquivo do incidente.
- **Comunicação:** a skill escreve o texto; o usuário envia.
- **Operação:** só quem foi autorizado mexe em produção. "Só a equipe de operação mexe no sistema durante o incidente" [fonte: https://sre.google/sre-book/managing-incidents/].
