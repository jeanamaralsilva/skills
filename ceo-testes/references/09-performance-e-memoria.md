# Performance e memória no iOS

Jank, tela que demora e app que morre por memória são bugs que o cliente descreve como "lento" ou "fechou sozinho". Medem-se; não se estimam.

## Orçamentos

| Métrica | Alvo | Fonte |
|---|---|---|
| Frame | 16,7 ms a 60 Hz; 8,3 ms a 120 Hz (ProMotion) | Apple, Animation Hitches |
| Hitch | < 5 ms por segundo "bom"; > 10 ms/s "ruim" (hitch time ratio) | Apple, Instruments |
| Resposta a toque | < 100 ms percebido como instantâneo; < 1 s mantém o fluxo; > 10 s precisa de progresso | NN/g |
| Cold start | < 2 s até a primeira tela útil (TTI); Apple mata o app em ~20 s sem UI | Apple, Reducing launch time |
| Memória | sem crescimento contínuo em 5 min de uso; jetsam (`EXC_RESOURCE`, "terminated due to memory") é P0 | Apple |
| Componentes animados por tela | poucos; animar só `transform` e `opacity` (thread de UI, Reanimated) | Reanimated |

## Medir

### Sem Instruments

```bash
agent-device perf frames --json                   # fps, frames perdidos durante um fluxo
agent-device perf memory sample --json            # RSS do app
xcrun simctl spawn <UDID> log stream --predicate 'process == "App" AND (eventMessage CONTAINS "hitch" OR eventMessage CONTAINS "memory")'
```

Tempo de resposta pelo vídeo: `recordVideo` e os timestamps do `video_frames.py` entre o toque e a tela nova. Rotule `[medido]`.

### Com Instruments (xctrace, sem abrir a GUI)

```bash
xcrun xctrace list templates
xcrun xctrace record --template 'Animation Hitches' --device <UDID> --time-limit 30s --output runs/hitches.trace --attach <pid|AppName>
xcrun xctrace record --template 'Time Profiler' --device <UDID> --output runs/cpu.trace --launch -- /path/App.app   # --launch por último
xcrun xctrace record --template 'Allocations' --device <UDID> --time-limit 120s --output runs/mem.trace --attach AppName
xcrun xctrace export --input runs/hitches.trace --toc
xcrun xctrace export --input runs/hitches.trace --xpath '/trace-toc/run[@number="1"]/data/table[@schema="hitches"]' --output runs/hitches.xml
```

`open runs/hitches.trace` abre no Instruments para ler. No simulador o Time Profiler mede a CPU do Mac, não do iPhone: serve para achar o que é lento, não para dizer quanto. Hitches e Allocations são úteis no simulador; números finais de FPS só no aparelho.

### No React Native

- Dev build com `__DEV__` é 2 a 5x mais lento: meça em build de release (`eas build --profile preview`), nunca no Metro.
- Hermes: `Performance` API (`performance.mark/measure`) aparece no React Native DevTools > Performance. Marque `app_start`, `screen_ready`.
- Re-render: React DevTools Profiler (DevTools > Profiler) com "Record why each component rendered". Lista com 1000 itens e item sem `memo` aparece na hora.
- Reanimated: `useFrameCallback` para contar frames; `runOnJS` no meio da animação é suspeito.
- FlashList: `onBlankArea` dá os pixels em branco durante o scroll (B37); `recyclingKey` nas imagens (B38).

## Cenários obrigatórios antes de release

| Cenário | Como | Oráculo |
|---|---|---|
| Cold start | `terminate`, `launch` com vídeo | primeira tela útil < 2 s [medido] |
| Scroll da lista principal com 1000 itens | seed + `swipe` 10x | sem hitch > 10 ms/s; sem área em branco |
| Transição de aba com animação | `varredura-de-abas.yaml` + Animation Hitches | hitch ratio "bom" |
| Sheet abrindo e fechando 20x | Maestro `repeat` | memória volta ao patamar |
| 5 min de uso real com socket | `phx_actor` mandando 1 evento/s | RSS estável; sem reconexão em loop |
| Fonte grande + escuro | `fonte-grande-e-escuro.yaml` | layout íntegro (não é perf, mas é a mesma rodada) |

## Android (quando houver)

Ainda não é alvo desta skill em máquinas só com iOS, mas o roteiro já existe: `adb shell dumpsys gfxinfo <pkg> reset` → fluxo → `dumpsys gfxinfo <pkg>` (janky frames, P90/P95/P99); Flashlight (`flashlight test --bundleId <pkg> --testCommand "maestro test f.yaml"`) dá score 0-100 com FPS, CPU e RAM; Perfetto para trace de sistema; `adb shell monkey -p <pkg> -s 42 --throttle 50 5000` para fuzz. Emulador com `-memory 1536 -netdelay gsm -netspeed edge` simula aparelho fraco. Receitas T23 a T27 e T33 a T35 em `data/recipes.csv`.

## Fontes

- xctrace: `xcrun xctrace help record` (Xcode 26.6); https://keith.github.io/xcode-man-pages/xctrace.1.html
- Animation Hitches (Apple): https://developer.apple.com/documentation/xcode/analyzing-responsiveness-issues-in-your-shipping-app ; Memória: https://developer.apple.com/documentation/xcode/reducing-your-app-s-memory-use
- NN/g tempos de resposta: https://www.nngroup.com/articles/response-times-3-important-limits/
- React Native DevTools: https://reactnative.dev/docs/react-native-devtools ; FlatList/FlashList: https://reactnative.dev/docs/optimizing-flatlist-configuration
- agent-device perf: https://oss.callstack.com/agent-device/docs/commands
- Flashlight: https://docs.flashlight.dev/test ; Perfetto: https://perfetto.dev/docs/getting-started/system-tracing
