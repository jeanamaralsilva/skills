# Base legal e consentimento

Consultado em 2026-10-19. A skill sugere a base provável por finalidade; a escolha final é do controlador com o advogado.

## As bases (LGPD art. 7º)

Consentimento; obrigação legal; administração pública; pesquisa; execução de contrato a pedido do titular; exercício de direitos em processo; proteção da vida; tutela da saúde; legítimo interesse; proteção do crédito [fonte: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709compilado.htm].

Dado sensível (saúde, biometria, religião, origem racial, vida sexual, opinião política, genético, sindicato) tem lista própria: consentimento específico e destacado, ou hipótese do art. 11 II quando indispensável (art. 11) [fonte: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709compilado.htm].

## Base provável por finalidade (para levar ao advogado)

| Finalidade no app | Base provável | Por quê |
|---|---|---|
| Criar conta, login, entregar o que o usuário pediu | execução de contrato (art. 7º V) | sem o dado o serviço não funciona |
| Nota fiscal, guarda exigida por lei | obrigação legal (art. 7º II) | a lei manda guardar |
| Antifraude, segurança da conta | legítimo interesse (art. 7º IX) ou art. 11 II g para sensível | só o estritamente necessário e com transparência (art. 10) |
| Analytics de produto, crash | legítimo interesse ou consentimento | depende do SDK e do que vai junto; marketing e anúncio pesam para consentimento |
| Anúncio personalizado, rastreamento entre apps | consentimento | e ATT no iOS (`04-lojas-e-rotulos.md`) |
| Dado de saúde, biometria | consentimento específico e destacado (art. 11 I) | ou hipótese do art. 11 II com advogado |
| Dado de criança | melhor interesse; consentimento de um dos pais é a regra do art. 14 §1º, mas a ANPD admite outras bases do art. 7º ou 11 se o melhor interesse prevalecer | Enunciado CD/ANPD nº 1/2023 [fonte: https://www.in.gov.br/en/web/dou/-/enunciado-cd/anpd-n-1-de-22-de-maio-de-2023-485306934] |

## Se a base é consentimento, o código precisa provar

- Livre, informado, inequívoco e para finalidade determinada (art. 5º XII); autorização genérica é nula (art. 8º §4º) [fonte: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709compilado.htm].
- O ônus da prova é do controlador (art. 8º §2º): guarde quem, quando, qual versão do texto, para qual finalidade. Uma tabela de consentimentos com `user_id`, `finalidade`, `versao_texto`, `aceito_em`, `revogado_em` resolve.
- Revogação a qualquer momento, grátis e fácil (art. 8º §5º): o botão de desligar fica tão fácil quanto o de ligar.
- Mudou finalidade, compartilhamento ou duração: avisar com destaque (art. 8º §6º e art. 9º §2º).
- SDK que coleta com base em consentimento só liga depois do "sim": Firebase Analytics com `analytics_auto_collection_enabled: false` no `firebase.json` e `setAnalyticsCollectionEnabled(true)` depois [fonte: https://rnfirebase.io/analytics/usage]; Crashlytics com `crashlytics_auto_collection_enabled: false` [fonte: https://rnfirebase.io/crashlytics/usage].

## Transparência mínima ao titular (art. 9º)

Finalidade; forma e duração; identidade e contato do controlador; com quem compartilha e para quê; responsabilidades; direitos do art. 18. Se o dado é condição para usar o app, diga com destaque (art. 9º §3º) [fonte: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709compilado.htm]. Isso vai na política (`10-politica-e-termos.md`) e, para coleta não óbvia, numa tela antes da permissão.

## GDPR, quando há usuários na UE

- Vale para quem oferece bens ou serviços a pessoas na UE, mesmo de fora (art. 3(2)) [fonte: https://publications.europa.eu/resource/celex/32016R0679].
- 6 bases (art. 6(1)); consentimento provado e retirável (art. 7); categorias especiais (art. 9) [fonte: https://publications.europa.eu/resource/celex/32016R0679].
- Criança consente sozinha a partir de 16 anos, ou menos se o país baixar, nunca abaixo de 13 (art. 8(1)) [fonte: https://publications.europa.eu/resource/celex/32016R0679].
- Representante na UE (art. 27) e contrato com operador (art. 28): leve ao advogado.
