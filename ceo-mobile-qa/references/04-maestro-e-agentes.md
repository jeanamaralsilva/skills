# Maestro, agent-device e argent

Três jeitos de tocar no app. Escolha pelo que o caso pede, não pelo hábito.

| Ferramenta | Para | Não serve para |
|---|---|---|
| **Maestro** (YAML) | fluxo repetível: login, duplo toque, deep link, regressão visual, CI (EAS Workflows) | iPhone físico (só simulador), exploração sem roteiro |
| **agent-device** (Callstack) | exploração dirigida por agente, iPhone físico, perf (frames, memória, xctrace), `press --count` para rajadas | suíte estável de regressão |
| **argent** (Software Mansion, Expo) | dev build com MCP: inspecionar tela, logs, rede e profiling pelo agente | app sem dev client |
| **Claude in Chrome / agent-browser** | a parte web do produto | mobile |

## Maestro

Instalação: `curl -fsSL "https://get.maestro.mobile.dev" | bash` (precisa de Java 17+). Verifique com `maestro --version`.

```bash
maestro --device <UDID> test .maestro/login.yaml                 # um device
maestro test -e APP_ID=com.x.app -e USERNAME=$TEST_USER_ADMIN flow.yaml
maestro test --format junit --output runs/report.xml --test-output-dir runs/maestro .maestro/
maestro test --shard-split 2 .maestro/                           # divide a suíte entre devices conectados
maestro --device <UDID> hierarchy                                # ids e textos da tela atual (não está na doc, existe)
maestro record --local flow.yaml                                 # grava vídeo do flow
maestro studio                                                   # inspeção visual
claude mcp add maestro -- maestro mcp                            # expõe ao agente: inspecionar, rodar YAML inline
```

Comandos que mais importam para caçar bug (confirmados na doc em out/2026):

| Comando | Uso | Nota |
|---|---|---|
| `tapOn: {text: X, repeat: 5, delay: 40}` | duplo toque / rajada (B01) | `delay` em ms entre toques |
| `launchApp: {clearState: true, clearKeychain: true, permissions: {all: deny}}` | instalação limpa e permissões negadas | `permissions` aceita `camera: allow` etc. |
| `stopApp` + `launchApp: {stopApp: false}` | morte do processo e volta (B17) | iOS não tem `back` (só Android e web) |
| `openLink: "app://x"` | deep link | em dev build, não no Expo Go |
| `extendedWaitUntil: {visible: X, timeout: 10000}` | esperar mais que o retry padrão | `assertVisible` não aceita `timeout` |
| `waitForAnimationToEnd: {timeout: 5000}` | antes de print | |
| `takeScreenshot: runs/x` e `assertScreenshot: {path: runs/x.png, thresholdPercentage: 98}` | regressão visual | gere a baseline uma vez; limiar alto demais dá falso positivo com relógio na barra (use `status_bar override`) |
| `runFlow: {file: login.yaml, env: {ROLE: admin}}` | compor flows | |
| `repeat: {times: 3, commands: [...]}` ou `while: {notVisible: X}` | loops | |
| `copyTextFrom: {id: X}` → `${maestro.copiedText}` | ler valor da tela | |
| `evalScript: ${output.n = 1}` | lógica | |
| `scrollUntilVisible: {element: X, direction: DOWN}` | listas | |
| `hideKeyboard` | iOS faz swipes; se falhar, `tapOn` em área neutra | |
| `setAirplaneMode: enabled` | **só Android** | iOS: Toxiproxy ou Network Link Conditioner |

Templates prontos em `assets/maestro/`: `login-por-papel`, `duplo-toque`, `background-e-volta`, `deep-link-frio-e-quente`, `permissao-negada`, `fonte-grande-e-escuro`, `varredura-de-abas`. Todos com `appId: ${APP_ID}` e credencial por `-e` a partir de variável de ambiente.

**Na nuvem:** EAS Workflows tem job `maestro` (`build_id`, `flow_path`, `shards`, `retries`, `record_screen`). Serve para rodar a suíte sem ocupar o Mac.

## agent-device

```bash
npm install -g agent-device@latest                 # Node 22.12+
agent-device open <bundle-ou-.app> --platform ios [--device "ceo-admin"]
agent-device snapshot -i                           # árvore com refs @e1, @e2 (também --diff)
agent-device press @e12 --settle                   # ou press x y
agent-device press 300 500 --count 12 --interval-ms 45    # rajada de toques (B01)
agent-device type "texto" ; agent-device fill @e7 "texto"
agent-device swipe x1 y1 x2 y2 ; agent-device scroll down 0.5
agent-device record start runs/a.mov ; agent-device record stop
agent-device perf frames --json ; agent-device perf memory sample --json
agent-device perf trace start --kind xctrace --template "Animation Hitches" --out runs/hitches.trace ; ... stop
agent-device screenshot runs/x.png ; agent-device close
```

iPhone físico: pareado (`xcrun devicectl list devices`), Developer Mode ativo, assinatura pelo Xcode ou `AGENT_DEVICE_IOS_TEAM_ID`, `AGENT_DEVICE_IOS_SIGNING_IDENTITY`, `AGENT_DEVICE_IOS_PROVISIONING_PROFILE`. No físico, settings, push e clipboard não funcionam pela ferramenta. A skill `dogfood` da mesma equipe (`npx skills add https://github.com/callstackincubator/agent-device --skill dogfood`) é um roteiro de QA exploratório por agente; combine com os tours de `data/tours.csv`.

## argent

`npx @swmansion/argent init` no projeto Expo cria o dev build com o servidor MCP. Dá ao agente: hierarquia, toque, logs do Metro, requisições de rede e profiling. Exige dev build (`expo-dev-client`), não Expo Go.

## React Native DevTools

Pressione `j` no terminal do `npx expo start --dev-client`. A aba Network existe desde RN 0.83 (sem WebSocket, sem throttling). Flipper está descontinuado (última versão com RN: 0.239.0). Para ver os frames do canal Phoenix, use `--verbose` no `phx_actor.mjs` ou `socket.logger` no app.

## Fontes

- Maestro: https://docs.maestro.dev/reference/commands-available/tapon.md (e launchapp, extendedwaituntil, assertscreenshot, openlink, back, setairplanemode, repeat); CLI: https://docs.maestro.dev/maestro-cli/maestro-cli-commands-and-options.md; MCP: https://docs.maestro.dev/get-started/maestro-mcp
- EAS Workflows job maestro: https://docs.expo.dev/eas/workflows/pre-packaged-jobs.md
- agent-device: https://oss.callstack.com/agent-device/docs/commands ; https://raw.githubusercontent.com/callstackincubator/agent-device/main/README.md
- argent: https://docs.expo.dev/agents/argent.md
- React Native DevTools: https://reactnative.dev/docs/react-native-devtools ; Flipper: https://raw.githubusercontent.com/facebook/flipper/main/README.md
