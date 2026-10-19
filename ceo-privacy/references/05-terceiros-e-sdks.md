# Terceiros e SDKs

Consultado em 2026-10-19.

Todo SDK que sai do aparelho é alguém recebendo dado pessoal. Para cada um: o que coleta por padrão, se dá para reduzir, se entra no rótulo da loja, onde fica o servidor.

## Inventário

`scripts/pii_scan.py` lista os pacotes de `package.json` e `mix.exs` que estão em `data/sdks.csv`, com coleta padrão, como reduzir e fonte. Pacote de coleta que não está no CSV: abra a doc oficial dele antes de afirmar qualquer coisa; sem doc, marque "não verificado".

## Regras de bolso

- **Mande id, não pessoa.** `Sentry.setUser({ id })`, `crashlytics().setUserId(id)`, `analytics().setUserId(id)`. Crashlytics pede id, token ou hash, nunca e-mail [fonte: https://firebase.google.com/docs/crashlytics/android/customize-crash-reports]. O Google Analytics proíbe enviar e-mail, telefone, nome ou URL com PII em evento [fonte: https://support.google.com/analytics/answer/6366371].
- **Sentry:** `sendDefaultPii` fica `false`; com `true` vão user id, username e e-mail [fonte: https://docs.sentry.io/platforms/react-native/configuration/options/]. Use `beforeSend` para limpar breadcrumbs, query strings e contexto [fonte: https://docs.sentry.io/platforms/react-native/data-management/sensitive-data/]. Mantenha o scrubbing do servidor ligado [fonte: https://docs.sentry.io/security-legal-pii/scrubbing/server-side-scrubbing/]. Session Replay mascara texto, imagem e input por padrão; não desligue [fonte: https://docs.sentry.io/platforms/react-native/session-replay/privacy/].
- **Firebase Analytics e Crashlytics:** se a base for consentimento, comece desligado no `firebase.json` e ligue depois do "sim" [fonte: https://rnfirebase.io/analytics/usage] [fonte: https://rnfirebase.io/crashlytics/usage]. Sem anúncio, desligue a coleta de Advertising ID [fonte: https://firebase.google.com/docs/analytics/android/configure-data-collection].
- **Meta e AdMob:** coletam identificadores para anúncio; Meta registra eventos sozinho até você desligar `AutoLogAppEventsEnabled` e `AdvertiserIDCollectionEnabled` [fonte: https://developers.facebook.com/docs/app-events/getting-started-app-events-android]. Exigem ATT no iOS se rastreiam (`04-lojas-e-rotulos.md`).
- **Amplitude:** coleta IP, adid, modelo e operadora por padrão; desligue em `trackingOptions` [fonte: https://amplitude.com/docs/sdks/analytics/react-native/react-native-sdk].
- **Push:** o push token identifica o aparelho; guarde ligado à conta só enquanto ela existir e apague na exclusão.

## Operador, contrato e país

- Fornecedor que trata dado em seu nome é operador: precisa de contrato (DPA). No GDPR, o contrato é obrigatório (art. 28) [fonte: https://publications.europa.eu/resource/celex/32016R0679].
- Servidor ou SDK fora do Brasil é transferência internacional: só vale nas hipóteses do art. 33 da LGPD (país adequado, cláusulas padrão, consentimento específico, entre outras) [fonte: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709compilado.htm]. Liste país de cada fornecedor e leve ao advogado; a skill não decide qual hipótese usar.
- Repassar a outro controlador dado obtido por consentimento exige novo consentimento específico (art. 7º §5º) [fonte: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709compilado.htm].

## SDK novo

Antes de instalar: o que coleta, se tem privacy manifest (lista da Apple: https://developer.apple.com/support/third-party-SDK-requirements/), o que muda no App Privacy e no Data safety, licença e versão (`ceo-deps`, se instalada).
