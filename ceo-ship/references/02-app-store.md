# App Store

Consultado em 2026-10-19. Regras mudam: confira a fonte antes de citar data ou número para o CEO.

## Requisitos de upload

| Regra | Fonte |
|---|---|
| Desde 28/04/2026 o upload exige Xcode 26 ou mais novo e SDK iOS 26 | https://developer.apple.com/news/upcoming-requirements/ |
| Sem texto de permissão no Info.plist, o acesso falha e pode fechar o app; o upload volta com ITMS-90683 | https://developer.apple.com/documentation/uikit/requesting-access-to-protected-resources |
| Desde 01/05/2024 o App Store Connect recusa app que usa API de motivo obrigatório sem declarar no privacy manifest, inclusive a de SDKs de terceiros | https://developer.apple.com/documentation/bundleresources/describing-use-of-required-reason-api |
| SDKs da lista da Apple precisam trazer privacy manifest e, se binários, assinatura | https://developer.apple.com/support/third-party-SDK-requirements/ |
| Build number: "build string" identifica o build; para iOS, único e crescente dentro da mesma versão (nota técnica arquivada, mas é a regra que o App Store Connect aplica) | https://developer.apple.com/help/app-store-connect/manage-builds/upload-builds/ e https://developer.apple.com/library/archive/technotes/tn2420/_index.html |
| `ITSAppUsesNonExemptEncryption` responde no Info.plist a pergunta de criptografia que o App Store Connect faz a cada versão | https://developer.apple.com/documentation/security/complying-with-encryption-export-regulations |

No Expo: `ios.config.usesNonExemptEncryption` grava a chave [fonte: https://docs.expo.dev/versions/latest/config/app/]. Só marque `false` se o app e as libs não usam criptografia ou usam só a isenta; na dúvida, é decisão do CEO com o jurídico.

## Motivos de rejeição mais comuns

A Apple diz que mais de 40% dos problemas não resolvidos são da diretriz 2.1 (completude) e lista: crash e bugs, links quebrados, conteúdo placeholder, informação incompleta, política de privacidade, pedido de acesso a dados sem clareza, screenshots imprecisos, interface abaixo do padrão, site empacotado, apps repetidos, cópias, enganar o usuário, pouco valor duradouro e envio pela entidade errada [fonte: https://developer.apple.com/distribute/app-review/].

Diretrizes e correção: `data/rejections.csv` (linhas R01 a R15). As que mais pegam app de startup:

- **2.1(a)**: com login, conta demo nas informações para revisão e backend ligado.
- **2.3.1(a)**: novidades descritas com detalhe nas notas para revisão; texto genérico é rejeitado.
- **4.8**: login com Google, Facebook e afins exige outra opção equivalente que limite os dados a nome e e-mail, deixe esconder o e-mail e não rastreie para anúncio sem consentimento. A diretriz não exige Sign in with Apple pelo nome, mas é a opção que cumpre isso pronta. Há isenções (login próprio da empresa, conta corporativa ou educacional, ID do governo, cliente de outro serviço).
- **5.1.1(i)**: link da política de privacidade no App Store Connect e dentro do app, fácil de achar.
- **5.1.1(v)**: se cria conta, exclui conta dentro do app. Se o app não depende de conta, deixe usar sem login.
- **3.1.1**: recurso digital desbloqueado no app vai por compra dentro do app.

Todas em https://developer.apple.com/app-store/review/guidelines/.

## Revisão

- Em média 50% das submissões em menos de 24 h e 90% em menos de 48 h [fonte: https://developer.apple.com/distribute/app-review/].
- Rejeição repetida pela mesma diretriz deixa a revisão mais lenta [fonte: https://developer.apple.com/app-store/review/guidelines/].
- Revisão expressa só para envio que já está na fila, conforme disponibilidade [fonte: https://developer.apple.com/help/app-review/after-submitting-for-review/request-expedited-review]. Use para correção crítica, não para pressa de marketing.

## Enviar com EAS

```bash
eas build --platform ios --profile production --auto-submit
eas submit --platform ios --latest
```

`--auto-submit` usa o perfil de submit com o mesmo nome do perfil de build [fonte: https://docs.expo.dev/build/automate-submissions/]. `ascAppId` no `submit.production.ios` pula a etapa de criar o app [fonte: https://docs.expo.dev/eas/json/]. Flags do `eas submit`: https://docs.expo.dev/eas/cli/.
