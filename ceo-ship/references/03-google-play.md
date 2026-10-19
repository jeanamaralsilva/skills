# Google Play

Consultado em 2026-10-19. Regras mudam: confira a fonte antes de citar data ou número para o CEO.

## Requisitos que bloqueiam

| Regra | Fonte |
|---|---|
| Desde 31/08/2026 app novo e update miram Android 16 (API 36) ou mais; dá para pedir extensão até 01/11/2026. Wear OS e Automotive: API 35; TV e XR: API 34 | https://support.google.com/googleplay/android-developer/answer/11926878 |
| Expo SDK 54 foi o primeiro a mirar Android 16 (API 36); SDKs 56, 57 e 58 também miram 36 | https://expo.dev/changelog/sdk-54 e https://docs.expo.dev/versions/latest/ |
| Conta pessoal criada depois de 13/11/2023: teste fechado com pelo menos 12 testers inscritos por 14 dias seguidos antes da produção | https://support.google.com/googleplay/android-developer/answer/14151465 |
| Verificação de desenvolvedor: todo pacote no Play registrado até 30/09/2026, senão o app é removido | https://support.google.com/googleplay/android-developer/answer/16984799 |
| App novo publica em Android App Bundle (AAB) desde agosto de 2021 | https://developer.android.com/guide/app-bundle |
| Apps que miram API 35 ou mais precisam suportar páginas de 16 KB; update sem suporte fica bloqueado a partir de 01/02/2027 | https://developer.android.com/guide/practices/page-sizes |
| versionCode: inteiro positivo, sempre maior que o anterior, máximo 2100000000; o Android bloqueia downgrade | https://developer.android.com/studio/publish/versioning |

Conta pessoal nova e teste fechado é o atraso que mais pega: são no mínimo 14 dias antes de poder pedir produção. Diga isso ao CEO no primeiro contato, com data.

## Formulários do Console

- **Data safety**: todo app publicado preenche, mesmo sem coletar dados, incluindo o que SDKs de terceiros coletam. Só a trilha interna fica isenta [fonte: https://support.google.com/googleplay/android-developer/answer/10787469].
- **Exclusão de conta**: caminho dentro do app (pode ser link para a página web) e link web onde a pessoa pede a exclusão, sempre [fonte: https://support.google.com/googleplay/android-developer/answer/13327111].
- **Política de privacidade**: link no Console e dentro do app [fonte: https://support.google.com/googleplay/android-developer/answer/9888076].
- **Acesso ao app**: se precisa de login, dados em "Sign-in details" para o revisor [fonte: https://support.google.com/googleplay/android-developer/answer/9859455].

## Permissões que pedem declaração

| Permissão | Regra | Fonte |
|---|---|---|
| ACCESS_BACKGROUND_LOCATION | declaração no Console, aviso destacado no app antes do pedido, vídeo | https://support.google.com/googleplay/android-developer/answer/9799150 |
| SMS e registro de chamadas | só o app padrão de SMS, telefone ou assistente, com declaração | https://support.google.com/googleplay/android-developer/answer/10208820 |
| QUERY_ALL_PACKAGES | só quando a função principal exige ver os apps instalados | https://support.google.com/googleplay/android-developer/answer/10158779 |
| READ_MEDIA_IMAGES e READ_MEDIA_VIDEO | só se o seletor do sistema não atende, com declaração | https://support.google.com/googleplay/android-developer/answer/14115180 |
| FOREGROUND_SERVICE_* | declarar os tipos usados | https://support.google.com/googleplay/android-developer/answer/13392821 |
| USE_EXACT_ALARM | restrita à função principal; fora disso SCHEDULE_EXACT_ALARM | https://support.google.com/googleplay/android-developer/answer/13161072 |
| MANAGE_EXTERNAL_STORAGE | formulário de declaração | https://support.google.com/googleplay/android-developer/answer/10467955 |

A doc do `expo-media-library` avisa que acesso amplo à galeria no Android só é permitido para apps que precisam dele [fonte: https://docs.expo.dev/versions/latest/sdk/media-library/]. Permissão que entra sem uso (ex.: RECORD_AUDIO do seletor de imagem) sai com `android.blockedPermissions` [fonte: https://docs.expo.dev/guides/permissions/].

## Revisão

Pode levar até 7 dias ou mais em casos excepcionais [fonte: https://support.google.com/googleplay/android-developer/answer/9859751].

## Enviar com EAS

```bash
eas build --platform android --profile production --auto-submit
eas submit --platform android --latest
```

Na primeira submissão, `eas submit` cria a release na trilha de teste interno; o app precisa existir no Play Console e a chave da conta de serviço do Google precisa estar configurada [fonte: https://docs.expo.dev/submit/android/]. Em `submit.production.android`: `track` (production, beta, alpha, internal), `releaseStatus` (completed, draft, halted, inProgress), `rollout` de 0 a 1, que só vale com `inProgress`, e `serviceAccountKeyPath` [fonte: https://docs.expo.dev/eas/json/].
