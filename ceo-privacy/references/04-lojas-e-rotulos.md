# Lojas: rótulos, manifest e ATT

Consultado em 2026-10-19. O rótulo é uma declaração do que o código faz. Monte a partir do mapa de dados e de `data/sdks.csv`, nunca de memória.

## Regras que mudam o que se marca

| Loja | Regra | Fonte |
|---|---|---|
| App Store | App Privacy declara o que o app e os SDKs de terceiros coletam | https://developer.apple.com/app-store/app-privacy-details/ |
| App Store | "Coletar" é enviar para fora do aparelho por mais tempo que o atendimento em tempo real; processado só no aparelho não conta | https://developer.apple.com/app-store/app-privacy-details/ |
| App Store | "Ligado ao usuário" salvo se desidentificado antes da coleta; dado pessoal pela lei é sempre ligado | https://developer.apple.com/app-store/app-privacy-details/ |
| App Store | "Rastreamento" é cruzar dado do app com dado de outras empresas para anúncio ou medição, ou repassar a data broker | https://developer.apple.com/app-store/app-privacy-details/ |
| App Store | Divulgação opcional só com todos os critérios (sem rastreamento, sem anúncio, coleta rara e opcional, fornecida pelo usuário a cada vez) | https://developer.apple.com/app-store/app-privacy-details/ |
| Google Play | Data safety obrigatório para todo app publicado, mesmo sem coleta; inclui SDKs; teste interno isento | https://support.google.com/googleplay/android-developer/answer/10787469 |
| Google Play | Não é "compartilhar": provedor de serviço, fins legais, ação do usuário, dado anonimizado | https://support.google.com/googleplay/android-developer/answer/10787469 |
| Google Play | Declarar criptografia em trânsito e o mecanismo de exclusão; o desenvolvedor responde pela exatidão | https://support.google.com/googleplay/android-developer/answer/10787469 |

## Do mapa para o formulário

Para cada linha do inventário, responda:

| Pergunta | App Store | Google Play |
|---|---|---|
| Sai do aparelho? | coletado ou não | coletado ou não |
| Vai para empresa que não é seu operador? | (entra em rastreamento se for para anúncio) | compartilhado |
| Ligado à conta ou ao aparelho? | ligado ao usuário | (não pergunta assim) |
| Usado para anúncio entre apps? | rastreamento: exige ATT | finalidade "publicidade" |
| Opcional para o usuário? | critério da divulgação opcional | opcional ou obrigatório |
| Finalidade | funcionalidade, analytics, personalização, anúncio, fraude... | idem |

SDKs comuns e o que coletam por padrão: `data/sdks.csv`. Pontos que costumam faltar:
- Firebase Analytics coleta app-instance ID, Advertising ID no Android, IP mascarado para localização aproximada e eventos de tela e sessão sem você chamar nada [fonte: https://support.google.com/analytics/answer/11582702].
- Crashlytics coleta stack trace, estado do app, dados do aparelho e um installation UUID; depende do Firebase installations, que também se declara [fonte: https://firebase.google.com/docs/android/play-data-disclosure].
- Sentry não manda PII por padrão (`sendDefaultPii: false`), mas o servidor infere o IP [fonte: https://docs.sentry.io/platforms/react-native/data-management/data-collected/].

## ATT (iOS)

- Rastrear ou ler o IDFA exige ATT; vale para SDK de terceiro mesmo que você não use o dado; não pode condicionar recurso nem dar incentivo [fonte: https://developer.apple.com/app-store/user-privacy-and-data-use/].
- Não é rastreamento: cruzamento só no aparelho, antifraude, IDFV para analytics do próprio desenvolvedor [fonte: https://developer.apple.com/app-store/user-privacy-and-data-use/].
- Expo: `expo-tracking-transparency` com `userTrackingPermission` no plugin (vira `NSUserTrackingUsageDescription`) [fonte: https://docs.expo.dev/versions/latest/sdk/tracking-transparency/].
- Android 13+ que lê o Advertising ID declara `com.google.android.gms.permission.AD_ID` [fonte: https://support.google.com/googleplay/android-developer/answer/6048248]. Se nenhum SDK precisa, bloqueie com `android.blockedPermissions` [fonte: https://docs.expo.dev/guides/permissions/].

## Privacy manifest (iOS)

- Required reason API sem motivo declarado: upload recusado desde 01/05/2024 [fonte: https://developer.apple.com/documentation/bundleresources/describing-use-of-required-reason-api].
- SDKs da lista da Apple (Firebase, GoogleSignIn, FBSDK, OneSignal, entre outros) precisam de manifest e assinatura [fonte: https://developer.apple.com/support/third-party-SDK-requirements/].
- Expo: `ios.privacyManifests` no app config; copie motivos de `node_modules/<lib>/ios/PrivacyInfo.xcprivacy` quando a Apple não ler o das libs [fonte: https://docs.expo.dev/guides/apple-privacy/].

## Permissões

Peça só o necessário e respeite o "não", oferecendo alternativa (ex.: digitar o endereço se negar a localização) (diretriz 5.1.1(iii) e (iv)) [fonte: https://developer.apple.com/app-store/review/guidelines/]. No Play, coleta não óbvia pede prominent disclosure dentro do app, antes da permissão, com aceite ativo [fonte: https://support.google.com/googleplay/android-developer/answer/10144311]. Texto de permissão e pré-voo do envio: `ceo-ship`, se instalada.

## O que a skill faz e não faz

Entrega a tabela do que marcar em cada loja e o porquê, com `arquivo:linha`. Não preenche App Store Connect nem Play Console: quem tem acesso preenche. Mudança de painel só com pedido e confirmação.
