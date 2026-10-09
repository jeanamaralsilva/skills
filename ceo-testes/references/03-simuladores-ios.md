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
python scripts/sim_session.py plan --roles admin,user --ram-gb 16
```

## Ciclo de vida

Tudo que a sessão cria leva o prefixo `ceo-`, e só isso é apagado no fim. Os simuladores do desenvolvedor ficam.

```bash
xcrun simctl list devicetypes                       # ids de device type
xcrun simctl list runtimes                          # ids de runtime
python scripts/sim_session.py create admin          # cria ceo-admin (iPhone 17, iOS 26) e dá boot
xcrun simctl boot <UDID>; open -a Simulator         # ou abrir o Simulator.app depois do boot
xcrun simctl install <UDID> build/App.app           # .app do EAS (perfil simulator) ou do Xcode
xcrun simctl launch --console-pty <UDID> <bundle>   # com stdout do app no terminal
xcrun simctl launch --terminate-running-process <UDID> <bundle>
xcrun simctl terminate <UDID> <bundle>              # mata o processo (B17)
xcrun simctl shutdown <UDID>
python scripts/sim_session.py cleanup               # shutdown + delete dos ceo-*, apaga runs/
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

## Limpeza (sempre, mesmo com falha)

```bash
python scripts/sim_session.py cleanup          # ceo-* e runs/
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
