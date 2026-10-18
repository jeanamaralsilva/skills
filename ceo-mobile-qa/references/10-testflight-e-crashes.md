# TestFlight, iPhone físico e crashes

O simulador não tem push de verdade, câmera, rede móvel, Keychain pós-reinstall nem a memória de um iPhone. O que o cliente vê, ele vê num aparelho. Três caminhos: TestFlight (o que o cliente usa), iPhone físico ligado ao Mac, e os crash logs que a Apple já coletou.

## TestFlight: o que o cliente já mandou

Testador com TestFlight 2.3+ tira um print dentro do app e envia feedback ali; quando o app crasha, o TestFlight oferece enviar o crash com comentário. Isso fica em App Store Connect > Apps > (app) > TestFlight > Feedback > **Screenshots** e **Crashes**. Dá para baixar `.zip`; crashes ficam 120 dias. App travado (não respondendo) não gera crash report.

### Pela API (App Store Connect API 4.0)

Endpoints (roles ADMIN, APP MANAGER ou DEVELOPER; Team ou Individual key):

```
GET /v1/apps/{id}/betaFeedbackScreenshotSubmissions
GET /v1/betaFeedbackScreenshotSubmissions/{id}
GET /v1/apps/{id}/betaFeedbackCrashSubmissions
GET /v1/betaFeedbackCrashSubmissions/{id}
GET /v1/betaFeedbackCrashSubmissions/{id}/crashLog      → texto do crash
GET /v1/betaCrashLogs/{id}
```

Auth: JWT ES256 em `Authorization: Bearer`. Header `alg: ES256`, `kid: <Key ID>`, `typ: JWT`. Payload (Team key): `iss` (Issuer ID), `iat`, `exp` (no máximo 20 min à frente), `aud: "appstoreconnect-v1"`. Individual key: sem `iss`, com `sub: "user"`.

```bash
# token com a chave .p8 (precisa de python-jwt ou jose; nunca commite a .p8)
python3 - <<'EOF'
import jwt, time, os
token = jwt.encode({"iss": os.environ["ASC_ISSUER_ID"], "iat": int(time.time()), "exp": int(time.time()) + 1200, "aud": "appstoreconnect-v1"},
                   open(os.environ["ASC_KEY_PATH"]).read(), algorithm="ES256", headers={"kid": os.environ["ASC_KEY_ID"], "typ": "JWT"})
print(token)
EOF
curl -s -H "Authorization: Bearer $TOKEN" "https://api.appstoreconnect.apple.com/v1/apps/$APP_ID/betaFeedbackCrashSubmissions?limit=20" | jq '.data[] | {id, created: .attributes.createdDate, device: .attributes.deviceModel, os: .attributes.osVersion, comment: .attributes.comment}'
curl -s -H "Authorization: Bearer $TOKEN" "https://api.appstoreconnect.apple.com/v1/betaFeedbackCrashSubmissions/$SUB_ID/crashLog" > runs/crash.txt
```

Webhooks de "TestFlight feedback events" existem na mesma versão da API para receber em tempo real. Cada crash vira um item de caça-bug: aparelho, iOS, comentário do testador, stack.

## Ler um crash log

1. **Exception Type / Reason:** `EXC_BAD_ACCESS` (ponteiro), `EXC_CRASH (SIGABRT)` com `NSInternalInconsistencyException` (assert do UIKit, ex.: layout fora da main thread), `EXC_RESOURCE` (memória ou CPU: jetsam), `0x8badf00d` (watchdog: travou o main thread > 20 s no launch), `SIGKILL` com `Code 0xdead10cc` (segurou um arquivo no background).
2. **Thread crashed:** a primeira linha com o nome do app ou de uma lib (`hermes`, `RNGestureHandler`, `ExpoModulesCore`) é o suspeito. Em RN, crash de JS vira `RCTFatal` ou `facebook::jsi::JSError` com a mensagem no `Last Exception Backtrace` ou no `Application Specific Information`.
3. **Symbolicated?** Linhas com `0x1a2b3c + 1234` sem nome de função não estão symbolicadas. O Organizer faz isso sozinho quando o build subiu com dSYM (EAS sobe por padrão). Manual: `xcrun atos -arch arm64 -o App.app.dSYM/Contents/Resources/DWARF/App -l <load address> <address>`.
4. **Erro de JS em release:** o stack de Hermes aponta para `index.android.bundle`/`main.jsbundle` com linha gigante. Sem source map, use `npx expo export --source-maps` do mesmo commit e `npx metro-symbolicate` com o sourcemap; com Sentry/Bugsnag configurado, eles fazem isso.

## Xcode Organizer

Window > Organizer > Crashes: todos os crashes de TestFlight e App Store, agregados por assinatura, independentemente do ajuste de diagnóstico do aparelho (TestFlight compartilha sempre). Control-clique no crash > Show in Finder dá o `.xccrashpoint`; dentro, os `.crash`. Watchdog, jetsam e crashes de code-signature não aparecem no Organizer: esses vêm do aparelho (Ajustes > Privacidade > Análise > Dados de Análise) ou do TestFlight.

## iPhone físico no Mac

Requisitos: cabo ou Wi-Fi pareado (`xcrun devicectl list devices`), Developer Mode ativo (Ajustes > Privacidade e Segurança), conta Apple Developer para assinar. Com isso:

- **Instalar e abrir:** `xcrun devicectl device install app --device <id> App.ipa`; `xcrun devicectl device process launch --device <id> <bundle>`.
- **Logs:** Console.app filtrando pelo processo; ou `idevicesyslog` (libimobiledevice).
- **Automação:** agent-device com as variáveis de assinatura (`04-maestro-e-agentes.md`). Maestro **não** roda em iPhone físico (PR de suporte fechado sem merge; workaround não oficial `devicelab-dev/maestro-ios-device`). Appium XCUITest roda, com WebDriverAgent assinado.
- **Rede:** Ajustes > Desenvolvedor > Network Link Conditioner (aparece com Developer Mode) para 3G, Edge, 100% loss no próprio aparelho: é o único jeito de testar modo avião e rede móvel de verdade.
- **Push real:** só aqui ou no TestFlight. `expo-notifications` com token APNs do dev build.

## O que só o aparelho ou o TestFlight provam

| Caso | Por quê |
|---|---|
| Push abrindo a tela certa com app fechado (B23) | `simctl push` não passa pelo APNs nem pelo cold start real |
| Keychain após reinstall (B22) | o simulador apaga tudo no `uninstall` |
| Modo avião e troca Wi-Fi/4G (B14, B16) | não existe no simulador |
| Memória e jank finais (B36, B37) | o simulador usa a CPU e a RAM do Mac |
| Câmera, microfone, Face ID | sem hardware; `simctl` só simula permissão |
| Low Power Mode, bateria baixa | muda rede e animação; só no aparelho |

## Fontes

- Feedback no App Store Connect: https://developer.apple.com/help/app-store-connect/test-a-beta-version/view-tester-feedback
- API: https://developer.apple.com/documentation/appstoreconnectapi/beta-feedback-crash-submissions ; https://developer.apple.com/documentation/appstoreconnectapi/beta-feedback-screenshot-submissions ; release notes 4.0: https://developer.apple.com/documentation/appstoreconnectapi/app-store-connect-api-4-0-release-notes
- Tokens: https://developer.apple.com/documentation/appstoreconnectapi/generating-tokens-for-api-requests
- Crash reports e Organizer: https://developer.apple.com/documentation/xcode/acquiring-crash-reports-and-diagnostic-logs ; interpretar: https://developer.apple.com/documentation/xcode/examining-the-fields-in-a-crash-report
- Maestro em device físico (PR fechado): https://github.com/mobile-dev-inc/Maestro/pull/2856 ; agent-device: https://incubator.callstack.com/agent-device/docs/installation ; Appium: https://appium.github.io/appium-xcuitest-driver/latest/getting-started/device-setup/
