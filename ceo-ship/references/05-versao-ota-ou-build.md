# Versão, build e a decisão OTA ou build novo

Consultado em 2026-10-19.

## Números

| Campo do Expo | Vira | Regra | Fonte |
|---|---|---|---|
| `version` | CFBundleShortVersionString e versionName | o número que o usuário vê | https://docs.expo.dev/versions/latest/config/app/ |
| `ios.buildNumber` | CFBundleVersion | único e crescente dentro da versão | https://developer.apple.com/library/archive/technotes/tn2420/_index.html |
| `android.versionCode` | versionCode | inteiro, sempre maior, máximo 2100000000 | https://developer.android.com/studio/publish/versioning |

Com EAS, `cli.appVersionSource: "remote"` é o recomendado desde o EAS CLI 12: o EAS guarda os números e os valores de build do app config são ignorados. Com `autoIncrement` no perfil de produção, cada build sobe sozinho. Comandos: `eas build:version:set` e `eas build:version:sync` [fonte: https://docs.expo.dev/build-reference/app-versions/].

Suba `version` quando a mudança é visível para o usuário.

## OTA ou build novo

| Mudou | Caminho | Fonte |
|---|---|---|
| Só JS, estilo, imagens | OTA (EAS Update) pode | https://docs.expo.dev/eas-update/faq/ |
| Código nativo ou lib nativa (instalada ou atualizada) | build novo | https://docs.expo.dev/eas-update/faq/ |
| Permissão (câmera, localização...) | build novo | https://docs.expo.dev/eas-update/faq/ |
| Texto de permissão (Info.plist) | build novo | https://docs.expo.dev/guides/permissions/ |
| SDK do Expo | build novo | https://docs.expo.dev/eas-update/faq/ |
| Propósito principal do app | build e revisão; código interpretado baixado não pode mudar o propósito do app | https://docs.expo.dev/faq/ |

Mudança de config plugin ou de campo do app config que vai para o Info.plist ou AndroidManifest também muda o nativo. Na dúvida, não adivinhe: compare o fingerprint.

```bash
eas fingerprint:generate --platform ios --build-profile production
eas fingerprint:compare --build-id <id-do-build-na-loja>
```

Os dois comandos e flags estão em https://docs.expo.dev/eas/cli/. Fingerprint diferente do build na loja: build novo.

## runtimeVersion

O runtimeVersion garante que um update só chega a builds com o mesmo nativo [fonte: https://docs.expo.dev/eas-update/runtime-versions/].

| Política | Muda quando | Risco |
|---|---|---|
| `fingerprint` | qualquer coisa que afete o nativo | mais builds; menos chance de update incompatível |
| `appVersion` | `version` sobe | esquecer de subir a versão ao mudar nativo quebra quem já usa |
| `nativeVersion` | version + buildNumber/versionCode | idem |
| `sdkVersion` | o SDK do Expo muda | mudança nativa dentro do mesmo SDK passa despercebida |
| texto fixo ("1.0.0") | você muda à mão | idem |

Valores aceitos: https://docs.expo.dev/versions/latest/config/app/. A doc mostra o caso real: update que depende de lib nativa nova chega a um build sem ela e o expo-updates tenta voltar para o último update que funcionava. Recomende `fingerprint` (achado `OTA02`) e, se o time preferir outra política, que a regra "mudou nativo, sobe o runtime" esteja escrita.

## Publicar OTA

```bash
eas update --channel production --message "Corrige total do carrinho" --environment production
```

`--environment` é obrigatório no SDK 55 ou mais novo [fonte: https://docs.expo.dev/eas-update/getting-started/]. O perfil de build precisa de `channel` para o build saber de onde baixar (`OTA03`) [fonte: https://docs.expo.dev/eas/json/]. Mudança de comportamento que o revisor precisaria ver vai por build e revisão, não por OTA [fonte: https://docs.expo.dev/eas-update/introduction/].

Lançar OTA aos poucos e voltar atrás: `references/07-lancamento-gradual-e-rollback.md`.
