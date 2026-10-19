# Postmortem sem culpa

Consultado em 2026-10-19. Modelo: `assets/postmortem-template.md`.

## Quando

- Gatilhos do Google: impacto visível acima de um limite, qualquer perda de dados, intervenção manual (rollback, desvio de tráfego), resolução demorada, falha de monitoramento [fonte: https://sre.google/sre-book/postmortem-culture/].
- PagerDuty: obrigatório em SEV1 e SEV2, reunião em até 3 dias corridos (SEV1) ou 5 dias úteis (SEV2) [fonte: https://response.pagerduty.com/after/post_mortem_process/]. Atlassian: SEV1 e SEV2, opcional nos demais [fonte: https://www.atlassian.com/incident-management/handbook/postmortems].

## Como

- Sem culpa: causas que contribuíram, sem acusar pessoa ou time [fonte: https://sre.google/sre-book/postmortem-culture/]. Fatos, sem julgamento pessoal; "o quê", não "quem" [fonte: https://sre.google/workbook/postmortem-culture/].
- Seções de referência da Atlassian: resumo, antecedentes, falha, impacto, detecção, resposta, recuperação, linha do tempo, cinco porquês, causa raiz, lições, ações corretivas [fonte: https://www.atlassian.com/incident-management/handbook/postmortems]. O modelo desta skill é a versão curta disso.
- Toda ação tem dono e um jeito de acompanhar; ações melhoram o sistema, não as pessoas [fonte: https://sre.google/workbook/postmortem-culture/]. A Atlassian dá 4 ou 8 semanas para ações prioritárias [fonte: https://www.atlassian.com/incident-management/handbook/postmortems].
- Publique enquanto está fresco: o bom exemplo do Workbook circulou em menos de 1 semana, o ruim 4 meses depois (exemplo, não regra) [fonte: https://sre.google/workbook/postmortem-culture/].

## Ações típicas de app + servidor

Só proponha as que se ligam às causas do incidente:
- Detectar antes: alerta na taxa crash-free ou de erro (`data/sinais.csv`).
- Mitigar mais rápido: rollback ensaiado, lançamento gradual (phased release, staged rollout, `--rollout-percentage` no EAS Update), kill switch.
- Prevenir: teste do fluxo que quebrou (`ceo-mobile-qa`), migração compatível com a versão anterior, atualização de dependência vulnerável (`ceo-deps`).

## Para o cliente

Se houve aviso, feche com 2 a 3 frases: o que aconteceu, desculpa sincera, o que muda [fonte: https://response.pagerduty.com/after/post_mortem_template/].
