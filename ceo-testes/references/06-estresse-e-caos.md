# Estresse e caos

Estresse não é rodar a suíte 10 vezes. É tirar do app o que ele assume que tem: tempo, rede, memória, permissão, ordem.

## Rede

`simctl` não controla a rede. Três ferramentas, do mais cirúrgico ao mais bruto:

### Toxiproxy (por conexão, scriptável)

```bash
brew install toxiproxy && toxiproxy-server &
toxiproxy-cli create -l localhost:4001 -u localhost:4000 phx     # o app aponta para :4001
toxiproxy-cli toxic add -t latency   -a latency=3000 -a jitter=500 phx    # lento
toxiproxy-cli toxic add -t latency   -a latency=11000 phx                 # acima do timeout de push (B40)
toxiproxy-cli toxic add -t timeout   -a timeout=0 phx                     # segura tudo sem responder (queda silenciosa)
toxiproxy-cli toxic add -t reset_peer -a timeout=2000 phx                 # fecha a conexão (rejoin, B42)
toxiproxy-cli toxic add -t limit_data -a bytes=20000 phx                  # resposta cortada no meio (upload, B39)
toxiproxy-cli toxic add -t bandwidth -a rate=20 phx                       # 20 KB/s
toxiproxy-cli toxic add -t slicer -a average_size=64 -a size_variation=32 -a delay=10 phx   # frames picados
toxiproxy-cli toxic remove -n latency_downstream phx ; toxiproxy-cli toggle phx ; toxiproxy-cli delete phx
```

`--toxicity 0.3` aplica em 30% das conexões: bugs intermitentes de verdade. No simulador, a URL do app vem de env (`SIMCTL_CHILD_API_URL=http://localhost:4001`) ou do `.env` do dev build. Para staging, o proxy fica entre o app e a internet: `-u staging.example.com:443` com TLS de ponta a ponta não funciona para HTTPS (só para WebSocket sem TLS ou com o app aceitando o host); prefira servidor local.

### Network Link Conditioner (Mac inteiro, perfis prontos)

"Additional Tools for Xcode" (developer.apple.com/download/all) > Hardware > Network Link Conditioner.prefPane. Perfis 3G, Edge, Very Bad Network, 100% Loss. Afeta tudo no Mac, inclusive o Metro: use com o bundle já carregado.

### Modo avião

Não há no simulador iOS. Opções: `toxic add -t timeout -a timeout=0` (equivalente funcional), desligar o Wi-Fi do Mac (afeta tudo), ou iPhone físico. No Android, `setAirplaneMode` do Maestro.

## Tempo e ordem

| Provocar | Como | Observa |
|---|---|---|
| Duplo toque | Maestro `tapOn repeat: 5 delay: 40`; agent-device `press --count 12 --interval-ms 45` | 1 registro, botão desabilitado durante a mutation (B01) |
| Rajada do outro ator | `phx_actor` `{"repeat": 20, "push": ..., "interval": 10}` | ordem por sequência do servidor, nada perdido (B44) |
| Timeout e reenvio | latency 11000 + usuário toca de novo | servidor processou 1x? idempotência (B40, B02) |
| Relógio do cliente errado | Simulator > Features > Toggle time? não existe: use `SIMCTL_CHILD_TZ` para fuso e, para skew, mock de `Date.now` no dev build | expiração e contagem regressiva pelo relógio do servidor (B45) |
| Fuso e DST | `SIMCTL_CHILD_TZ=America/Manaus`, `Europe/Lisbon`; servidor em UTC | hora certa para cada papel; `{:gap}`/`{:ambiguous}` no servidor (B30, B31) |
| Locale | `-AppleLanguages "(pt-BR)" -AppleLocale pt_BR` vs `en_US` | vírgula decimal, data (B32) |

## Ciclo de vida

| Provocar | Como | Observa |
|---|---|---|
| Background longo | Home; esperar 10 min (tour After-hours); voltar | socket e queries retomam; `AppState` `inactive` não é tratado como background no iOS (B15) |
| Morte do processo | `xcrun simctl terminate <UDID> <bundle>`; reabrir | rascunho restaurado ou descartado de propósito; sem crash por estado nulo (B17) |
| Sair da tela durante request | Toxiproxy latency 5000; navegar antes da resposta | sem warning de setState após unmount; resposta velha não sobrescreve a tela nova (B18) |
| Reinstalar | `xcrun simctl uninstall` + `install` | token antigo no Keychain não entra em sessão inválida; `keychain reset` para o caso limpo (B22) |
| Push com app fechado | `terminate`; `simctl push` com payload da notificação; tocar | abre a tela certa; `getLastNotificationResponse` no boot (B23) |
| Permissão negada 2x | `simctl privacy revoke`; fluxo que pede | sem loop; alternativa oferecida (B27) |

## Dados e memória

| Provocar | Como | Observa |
|---|---|---|
| Lista grande | seed de 1000+ itens no servidor (`mix run priv/repo/seeds_stress.exs` ou script) | sem áreas em branco, jank, celula reciclada com foto errada (B37, B38) |
| Texto enorme e emoji | `inputText` com 500 caracteres, RTL, emoji composto | sem overflow, sem crash de parse (TR04) |
| Memória | rolar galeria por 5 min; `agent-device perf memory sample` a cada 30 s, ou Instruments Allocations | uso estável; sem jetsam (`EXC_RESOURCE`) (B36) |
| Upload interrompido | `limit_data` ou `terminate` durante upload | progresso consistente; servidor sem arquivo parcial (B39) |
| Fonte máxima + escuro | `simctl ui content_size accessibility-extra-extra-extra-large` + `appearance dark`; `fonte-grande-e-escuro.yaml` | nada cortado; botões alcançáveis (B33, B34) |

## Carga no servidor (k6)

```bash
brew install k6
k6 run --vus 50 --duration 60s -e WS_URL=ws://localhost:4000/socket -e TOPIC=room:1 -e TOKEN=$TEST_TOKEN_B assets/k6-phoenix-ws.js
```

`assets/k6-phoenix-ws.js` abre N clientes por sala com join, heartbeat e um push por segundo, e mede p95 do `phx_reply`. Observa: latência de broadcast, timeouts de join, mailbox crescendo (`:observer` ou LiveDashboard), file descriptors. Rode contra servidor local ou staging, nunca produção.

## Caos no servidor

- `Process.exit(pid, :kill)` no processo do canal (via `iex -S mix` ou teste): cliente faz rejoin, `join/3` roda de novo (B42).
- Derrubar um nó de dois: presenças do nó morto somem após o timeout do Tracker (B49).
- `Oban.drain_queue` com job duplicado: efeito único (B07, B08).

## Fontes

- Toxiproxy README e CLI: https://raw.githubusercontent.com/Shopify/toxiproxy/main/README.md ; https://raw.githubusercontent.com/Shopify/toxiproxy/main/cmd/cli/cli.go ; Homebrew: https://formulae.brew.sh/formula/toxiproxy
- Network Link Conditioner: https://www.avanderlee.com/debugging/network-link-conditioner-utility/
- k6 websockets (atual; `k6/experimental/websockets` está deprecado): https://grafana.com/docs/k6/latest/javascript-api/k6-websockets/
- AppState iOS: https://reactnative.dev/docs/appstate ; Memória iOS: https://developer.apple.com/documentation/xcode/reducing-your-app-s-memory-use
