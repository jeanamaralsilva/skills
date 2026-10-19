# Comunicar

Consultado em 2026-10-19. A skill escreve; o usuário envia. Nada vai para status page, Slack, e-mail, loja ou rede social sem pedido explícito com o destino.

## Estados

Investigando (sintoma visto, causa desconhecida), identificado (causa achada, correção em andamento), monitorando (correção aplicada, observando), resolvido [fonte: https://support.atlassian.com/statuspage/docs/create-an-incident/].

## Para o dono (`assets/update-dono-template.md`)

- Estado e impacto em 1 a 2 frases, depois situação atual e próximos passos, e a hora do próximo update [fonte: https://www.atlassian.com/incident-management/handbook/incident-response].
- Em SEV1 e SEV2, cerca de 30 minutos entre updates internos [fonte: https://response.pagerduty.com/during/during_an_incident/]. Sem novidade, mande assim mesmo: atualizar sem novidade é melhor que silêncio [fonte: https://www.atlassian.com/incident-management/incident-communication].
- Diga o que não se sabe: "a causa ainda não é conhecida" [fonte: https://www.atlassian.com/incident-management/handbook/incident-response].
- Feche com "Decisão sua", mesmo que seja "nenhuma". Para traduzir para leigo com mais cuidado, `ceo-brief` (se instalada).

## Para o cliente (`assets/aviso-cliente-template.md`)

- Primeira mensagem cedo; a PagerDuty mira 5 minutos depois de abrir o incidente e updates pelo menos a cada 20 minutos nas 2 primeiras horas, toda mensagem com a hora da próxima [fonte: https://response.pagerduty.com/during/external_communication_guidelines/].
- Nunca mais de 1 hora sem update enquanto o cliente está afetado [fonte: https://www.atlassian.com/incident-management/incident-communication].
- 1 a 2 frases, sem detalhe técnico; prazo de volta só se existir um [fonte: https://www.atlassian.com/incident-management/handbook/incident-response].
- Evite "fora do ar" ou "queda" se não foi queda total [fonte: https://response.pagerduty.com/after/post_mortem_process/].
- Na resolução, diga se houve perda de dados [fonte: https://response.pagerduty.com/during/external_communication_guidelines/].
- Evite update vazio: diga o que mudou ou o que está sendo feito (mesma fonte).

Cadências acima são de times grandes. Para uma pessoa só, combine com o dono (`incidente.comunicacao.cadencia_min` no config) e cumpra o que prometeu.

## Antes de entregar qualquer texto

- Nenhum e-mail, telefone, CPF, nome de cliente, id interno, URL interna, stack trace, token ou segredo.
- Nenhum nome de pessoa para culpa. Nenhum fornecedor culpado sem confirmação pela página de status dele.
- Nenhum prazo que ninguém confirmou.
- Número com origem.
