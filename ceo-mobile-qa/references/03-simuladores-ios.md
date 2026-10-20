# Simuladores iOS: sessão, memória e limpeza

## Orçamento de memória

Um simulador iOS 26 ocioso usa cerca de 4 GB de RAM (258 processos, medição do projeto simslim num M1 Pro de 16 GB; a Apple não publica número). Xcode aberto, Metro e um servidor Phoenix somam mais 4 a 6 GB. Num Mac de 16 GB:

| Cenário | Cabe? | Faça assim |
|---|---|---|
| 1 simulador + servidor local + Metro | sim | padrão |
| 1 simulador + `phx_actor.mjs` como segundo papel | sim | padrão para multiusuário |
| 2 simuladores | no limite: o Mac começa a paginar | feche Xcode e navegador; só quando o teste precisa de duas telas de verdade (ex.: comparar o que cada papel vê ao mesmo tempo) |
| 3 ou mais | não | nunca |

Com 32 GB ou mais, dois simuladores são rotina e três cabem. A config (`maquina.ram_gb`, `simuladores_max`) decide; sem config, assuma 16 GB.

```bash
python3 scripts/sim_session.py plan --roles admin,user --ram-gb 16
```

## Ciclo de vida

Tudo que a sessão cria leva o prefixo `ceo-`, e só isso é apagado no fim. Os simuladores do desenvolvedor ficam.

```bash
xcrun simctl list devicetypes                       # ids de device type
xcrun simctl list runtimes                          # ids de runtime
python3 scripts/sim_session.py create admin          # cria ceo-admin (iPhone 17, iOS 26) e dá boot
xcrun simctl boot <UDID>; open -a Simulator         # ou abrir o Simulator.app depois do boot
xcrun simctl install <UDID> build/App.app           # .app do EAS (perfil simulator) ou do Xcode
xcrun simctl launch --console-pty <UDID> <bundle>   # com stdout do app no terminal
xcrun simctl launch --terminate-running-process <UDID> <bundle>
xcrun simctl terminate <UDID> <bundle>              # mata o processo (B17)
xcrun simctl shutdown <UDID>
python3 scripts/sim_session.py cleanup               # shutdown + delete dos ceo-*, apaga runs/
```

Sem `.app`: `eas build -p ios --profile preview` com `"ios": {"simulator": true}` no `eas.json` e `eas build:run -p ios --latest` instala no simulador bootado (não compila no Mac). `npx expo run:ios` compila com Xcode localmente e precisa de memória; numa máquina de 16 GB com `build_nativo_local: false`, não.

## Estado do app e do aparelho

| Objetivo | Comando |
|---|---|
| Deep link | `xcrun simctl openurl <UDID> "app://class/123"` |
| Push (sem servidor) | `xcrun simctl push <UDID> <bundle> payload.json` (payload com chave `aps`, até 4 KB) |
| Negar ou dar permissão | `xcrun simctl privacy <UDID> revoke camera <bundle>`; `grant`; `reset all <bundle>` |
| Localização em movimento | `xcrun simctl location <UDID> start --speed=15 --interval=1 37.3349,-122.0090 37.3317,-122.0307` |
| Modo escuro | `xcrun simctl ui <UDID> appearance dark` |
| Fonte grande | `xcrun simctl ui <UDID> content_size accessibility-extra-extra-extra-large` (valores: `extra-small` a `extra-extra-extra-large`, `accessibility-medium` a `accessibility-extra-extra-extra-large`, `increment`, `decrement`) |
| Contraste | `xcrun simctl ui <UDID> increase_contrast enabled` |
| Idioma e região | `xcrun simctl launch <UDID> <bundle> -AppleLanguages "(pt-BR)" -AppleLocale pt_BR` |
| Fuso horário | `SIMCTL_CHILD_TZ=America/Manaus xcrun simctl launch <UDID> <bundle>` (o valor gruda; reinicie o simulador para trocar) |
| Variável de ambiente no app | prefixo `SIMCTL_CHILD_`: `SIMCTL_CHILD_API_URL=... xcrun simctl launch ...` |
| Limpar Keychain (sessão velha pós-reinstall, B22) | `xcrun simctl keychain <UDID> reset` |
| Zerar o aparelho | `xcrun simctl erase <UDID>` (precisa estar desligado) |
| Barra de status limpa | `xcrun simctl status_bar <UDID> override --time 9:41 --batteryLevel 100 --wifiBars 3` |
| Sem Wi-Fi na barra (só visual) | `xcrun simctl status_bar <UDID> override --wifiMode failed --dataNetwork wifi` |
| Teclado de hardware | Simulator > I/O > Keyboard > desmarque Connect Hardware Keyboard (senão o teclado virtual não aparece e o KeyboardAvoidingView não é testado) |

Modo avião e rede ruim não existem no `simctl`. Veja `06-estresse-e-caos.md`.

## Evidência

```bash
xcrun simctl io <UDID> screenshot runs/tela.png
xcrun simctl io <UDID> recordVideo --codec=h264 --force runs/fluxo.mov   # Ctrl-C para parar; "Recording started" sai no stderr
xcrun simctl spawn <UDID> log stream --level debug --predicate 'process == "<AppName>"' > runs/app.log &
xcrun simctl diagnose --no-archive --output runs/diag                  # logs do sistema e crash reports
```

Crash reports do simulador: `~/Library/Logs/DiagnosticReports/*.ips`. Abra com Console.app ou `plutil -p`.

## PWA e painel web no Safari do simulador

Web app instalável usado no iPhone se testa no WebKit iOS. Chrome headless não reproduz layout, zoom nem input de data do iPhone.

- Abrir: com argent, `boot-device`, `open-url http://localhost:<porta>`, `screenshot` e `describe` (T68). Sem argent, `xcrun simctl openurl <UDID> http://localhost:<porta>`. Console e Web Inspector: Safari > Develop > simulador (T69).
- Servidor local e dados de teste, como no resto da skill (`references/01-estrategia-e-risco.md`). Nunca produção com dado real, nem "só para ver no iPhone".
- Input date ou time num grid de 2 colunas (B51): sem largura fixa, o tema iOS do WebKit põe `min-width` igual à maior data estimada e `box-sizing: content-box`. O campo passa da borda e o Safari reduz a página. Correção: `-webkit-appearance: none` e `min-width: 0` no input e nos filhos do grid; colunas `minmax(0, 1fr)`, porque `1fr` sozinho tem mínimo `auto` (B52).
- Zoom ao focar campo (B53): o WebKit iOS calcula o zoom como 16 dividido pela fonte do campo. Fonte do campo >= 16px resolve. `maximum-scale=1` no viewport também limita esse zoom; o pinch do usuário continua, porque desde o iOS 10 o Safari permite pinch em toda página.
- Service worker com `clients.claim()` (B54): sem claim, a página só passa pelo SW depois de recarregar. Com claim, o SW assume a página aberta no meio do caminho (`controllerchange`), e o que já estava em andamento corre contra essa troca. Relato de campo: na primeira visita no Safari iOS, os PUT da fila offline não chegaram ao servidor até recarregar. Em app com fila offline, não use claim, ou só comece a fila com `navigator.serviceWorker.controller` definido.
- Fila offline com IndexedDB e outbox (B55): `fetch` não tem opção de timeout, então use `AbortSignal.timeout(15000)`. Retry com intervalo. Salve local sem esperar a rede. Mostre "N pendentes" tocável, com o motivo. Nunca `confirm()` nem logout dentro do processamento da fila. 401 só pede login de novo e mantém a fila. Para provocar: Network Link Conditioner ou Toxiproxy (`references/06-estresse-e-caos.md`).

## Limpeza (sempre, mesmo com falha)

```bash
python3 scripts/sim_session.py cleanup          # ceo-* e runs/
xcrun simctl shutdown all
xcrun simctl delete unavailable                # simuladores de runtimes que não existem mais
xcrun simctl runtime list -v
xcrun simctl runtime delete --dry-run --notUsedSinceDays 60   # veja antes; depois sem --dry-run
du -sh ~/Library/Developer/CoreSimulator/Devices ~/Library/Developer/Xcode/DerivedData
```

O `cleanup` preserva `runs/patches/` e `runs/keep/` (clipes de até 15 s citados no relatório, testes implementados ficam nas pastas do repo). Vídeos inteiros, prints, traces, logs e builds baixados vão embora. `DerivedData` pode ser apagado quando o Xcode está fechado. `~/Library/Developer/CoreSimulator/Caches` não tem recomendação oficial da Apple; apague só `dyld` dentro dela se o disco estiver cheio e o Xcode fechado, e diga no relatório. Antes do `cleanup`, corte o trecho citado (`ffmpeg -ss -to`) para `runs/keep/`; o resto da gravação some.

## Fontes

- `xcrun simctl help <comando>` (Xcode 26.6) para cada flag acima
- simslim, medição de RAM: https://pkg.go.dev/github.com/mobai-app/simslim
- Dynamic Type e contraste via `simctl ui`: https://raw.githubusercontent.com/appium/node-simctl/master/lib/subcommands/ui.ts
- TZ no simulador (Apple DTS): https://developer.apple.com/forums/thread/86951
- Runtimes: https://developer.apple.com/forums/thread/773153
- EAS simulator build: https://docs.expo.dev/build-reference/simulators/
- argent, ferramentas: https://github.com/software-mansion/argent/blob/main/packages/docs/docs/reference/tools.mdx
- Web Inspector no simulador: https://developer.apple.com/documentation/safari-developer-tools/inspecting-ios
- Input de data no iOS (min-width estimado): https://github.com/WebKit/WebKit/blob/main/Source/WebCore/rendering/ios/RenderThemeIOS.mm ; https://bugs.webkit.org/show_bug.cgi?id=301648
- `1fr` = `minmax(auto, 1fr)`: https://www.w3.org/TR/css-grid-1/#track-sizes
- Zoom ao focar (16 / fonte, limitado por maximum-scale): https://github.com/WebKit/WebKit/blob/main/Source/WebKit/UIProcess/API/ios/WKWebViewIOS.mm ; pinch no iOS 10: https://webkit.org/blog/7367/new-interaction-behaviors-in-ios-10/
- `clients.claim()`: https://developer.mozilla.org/en-US/docs/Web/API/Clients/claim ; https://web.dev/articles/service-worker-lifecycle
- `AbortSignal.timeout()`: https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal/timeout_static ; `confirm()` é modal: https://developer.mozilla.org/en-US/docs/Web/API/Window/confirm
