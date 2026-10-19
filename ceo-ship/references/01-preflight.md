# Pré-voo automático

```bash
python3 scripts/preflight.py <app-dir>                    # app.json
python3 scripts/preflight.py <app-dir> --config cfg.json  # app.config.ts/js resolvido
python3 scripts/preflight.py <app-dir> --json             # para processar
```

Só lê. Cada achado traz o id de `data/checks.csv`, onde estão severidade e fonte. Exit 1 quando há P0 ou P1.

## app.config.ts ou .js

É código: o script não executa e devolve `CFG01` com a lista do que não avaliou. Peça para rodar na raiz do app e passar o arquivo:

```bash
npx expo config --json --type public > /tmp/app-config.json
python3 scripts/preflight.py . --config /tmp/app-config.json
```

`npx expo config` aceita `--json`, `--full` e `--type` (public, prebuild, introspect) [fonte: https://docs.expo.dev/more/expo-cli/]. Se a pessoa não puder rodar, aceite o JSON colado. Sem isso, os itens do app config ficam "não avaliado", nunca "ok".

## Pastas ios/ e android/

| Situação | Fonte da verdade | O script |
|---|---|---|
| Sem ios/ e android/ (CNG) | app config | lê o app config |
| ios/ ou android/ no .gitignore (gerada) | app config | ignora a pasta quando o app config foi lido; sem ele, usa a pasta como pista e avisa que pode estar velha |
| ios/ ou android/ no git (nativo) | os arquivos nativos | lê Info.plist, PrivacyInfo.xcprivacy, AndroidManifest.xml e build.gradle |

## O que ele cobre e o que não

Cobre: versão e build (VER), perfis EAS (EAS), runtimeVersion e OTA (OTA), identificadores, criptografia, textos de permissão, privacy manifest no nativo, login social, iPad, localização em segundo plano (IOS), target API, SDK do Expo e permissões sensíveis do Android (AND), sinal de exclusão de conta (ACC01) e de política de privacidade (PRV01).

Não cobre (checagem manual, `auto=manual` no CSV): conta demo, App Privacy, Data safety, screenshots, notas, contas e trilhas, prazos das lojas. Liste as que se aplicam ao pedido, não as 38.

## Textos de permissão padrão

Várias libs do Expo escrevem um texto genérico em inglês ("Allow $(PRODUCT_NAME) to access your camera") quando a opção do config plugin não é passada, e o Expo aplica algumas dessas libs mesmo fora de `plugins`. Por isso o achado `IOS03` aparece com a lib instalada e sem texto próprio. A Apple pede um texto por recurso que diga para que o app usa o dado; texto que só repete o nome do recurso não serve [fonte: https://developer.apple.com/help/app-review/guideline-reference/5-1-1-purpose-strings].

Correção: passe a opção no plugin com texto no idioma do app, ou `false` quando o app não usa aquele recurso (ex.: `microphonePermission: false` no seletor de imagem, que também tira o RECORD_AUDIO do Android, `AND11`) [fonte: https://docs.expo.dev/versions/latest/sdk/imagepicker/]. Texto de permissão não muda por OTA [fonte: https://docs.expo.dev/guides/permissions/].

## Achado heurístico

`ACC01` e `PRV01` procuram texto no código (ex.: "excluir conta", "privacy"). Sem achado não prova que existe a tela; com achado, abra o arquivo e confirme antes de reportar. `IOS06` olha só as libs instaladas.
