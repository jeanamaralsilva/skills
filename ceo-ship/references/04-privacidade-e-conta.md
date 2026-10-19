# Privacidade, permissões e conta

Consultado em 2026-10-19.

## Privacy manifest (iOS)

- Categorias de API de motivo obrigatório: `NSPrivacyAccessedAPICategoryFileTimestamp`, `SystemBootTime`, `DiskSpace`, `ActiveKeyboards` e `UserDefaults` [fonte: https://developer.apple.com/documentation/bundleresources/app-privacy-configuration/nsprivacyaccessedapitypes/nsprivacyaccessedapitype].
- Sem o motivo declarado, o upload é recusado desde 01/05/2024, contando o código de SDKs [fonte: https://developer.apple.com/documentation/bundleresources/describing-use-of-required-reason-api].
- Expo: declare em `ios.privacyManifests.NSPrivacyAccessedAPITypes`. A doc avisa que a Apple não lê direito todos os PrivacyInfo de dependências CocoaPods estáticas (como os pacotes do Expo), então pode ser preciso repetir no app os motivos que as libs usam. Para achar: veja `node_modules/<lib>/ios/PrivacyInfo.xcprivacy` e copie os tipos e motivos [fonte: https://docs.expo.dev/guides/apple-privacy/].
- Nativo: `PrivacyInfo.xcprivacy` no alvo do app (o script acusa a falta com `IOS05`).

## Rótulos de privacidade

| Loja | O que | Fonte |
|---|---|---|
| App Store | App Privacy obrigatório para app novo e update, incluindo o que SDKs de terceiros coletam; URL da política obrigatória; muda sem nova versão | https://developer.apple.com/app-store/app-privacy-details/ |
| Google Play | Data safety para todo app publicado, mesmo sem coleta, incluindo SDKs | https://support.google.com/googleplay/android-developer/answer/10787469 |

Monte a lista a partir do código, não de memória: SDKs no `package.json` (analytics, crash, anúncio, login, pagamento, push), permissões do app config e o que o backend guarda. Para escrever a política e preencher os rótulos, use a skill de termos e privacidade do time, se instalada.

## Textos de permissão

Regras da Apple [fonte: https://developer.apple.com/help/app-review/guideline-reference/5-1-1-purpose-strings]:
- Um texto por recurso pedido.
- Diga para que o app usa e o benefício. "Para usar a localização" não serve; "Usamos sua localização para sugerir a rota até o destino" serve.
- Peça no momento em que a pessoa vai usar o recurso, e respeite o "não" (diretriz 5.1.1(iv), https://developer.apple.com/app-store/review/guidelines/).

Escreva no idioma da página da loja. Texto padrão em inglês num app em português é o achado `IOS03`.

## Exclusão de conta

| Loja | Regra | Fonte |
|---|---|---|
| App Store | Se cria conta, inicia a exclusão dentro do app (desde 30/06/2022). Fácil de achar. Desativar não basta. Pode levar a uma página web que conclui. Não exigir ligação nem e-mail fora de setor regulado. Com Sign in with Apple, revogar o token pela REST API | https://developer.apple.com/support/offering-account-deletion-in-your-app/ |
| Google Play | Caminho dentro do app e link web para pedir exclusão, ambos; o link vai no Console | https://support.google.com/googleplay/android-developer/answer/13327111 |

Na prática: um item "Excluir conta" em Conta ou Perfil, confirmação, chamada ao backend que apaga ou agenda a exclusão, e uma página web pública com o mesmo fluxo. O backend precisa apagar de verdade os dados ligados à conta; teste com uma conta descartável.

## Política de privacidade

Link no App Store Connect e no app (5.1.1(i), https://developer.apple.com/app-store/review/guidelines/); link no Play Console e no app (https://support.google.com/googleplay/android-developer/answer/9888076).
