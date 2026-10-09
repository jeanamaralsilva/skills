# Mapa de telas e matriz de casos

Testar "tudo" começa por saber o que existe. O mapa vem do código, não da memória.

## 1. Telas e ações

```bash
python scripts/map_flows.py <mobile> [--screen class] [--json]
```

Para cada tela (expo-router em `app/` ou `src/app/`; fallback `*Screen.tsx`): rota, ações tocáveis (Pressable, Touchable*, Button, Link) com rótulo, se a ação **escreve** (useMutation, `channel.push`, `fetch`, `api.post`), e quais estados o arquivo trata (loading, empty, error). Estático: não roda o app, não acha botão renderizado por lista dinâmica. Complete com `maestro hierarchy` na tela rodando quando o rótulo não aparece no código.

Se o app usa React Navigation sem expo-router, o `map_routes.py` do `ceo-analytics` lê o `createStackNavigator`/`createBottomTabNavigator`; use os dois.

## 2. Matriz

O script expande cada ação nos caminhos que valem teste:

| Caminho | Quando entra | Bugs de `data/bugs.csv` |
|---|---|---|
| feliz | sempre | |
| triste | sempre: entrada inválida, permissão negada, teclado cobrindo o botão | B27, B33 |
| duplo-toque | ação escreve dado | B01 |
| sem-rede | ação escreve dado: modo avião antes e durante | B12, B13, B40 |
| background-no-meio | ação escreve dado: Home e volta durante a escrita | B15, B18 |
| deep-link-frio | rota com parâmetro: app fechado, aberto, deslogado | B28, B29 |
| erro-sem-tratamento | tela busca dado e não trata erro | B12 |
| vazio | tela busca dado e não tem estado vazio | |
| reconexao | tela usa canal | B41, B42, B43 |

Uma tela com 4 botões que escrevem vira uns 20 casos. Um app de 30 telas vira 300 a 500. Por isso o risco (`01-estrategia-e-risco.md`) decide a ordem: fluxo principal inteiro primeiro, depois caminhos tristes das telas de maior risco, depois o resto.

## 3. Tempo real

```bash
python scripts/map_realtime.py <mobile> <server> [--json]
```

Pareia `handle_in` e `push/broadcast` do Phoenix com `channel.on` e `channel.push` do app. Os quatro gaps que ele reporta são casos de teste antes de serem bugs:

- **server emite e ninguém escuta:** ou o evento é inútil, ou a tela que devia reagir não reage (dado velho até pull-to-refresh).
- **app escuta e o server nunca emite:** listener morto, ou evento vem de outro lugar (Oban, Endpoint.broadcast de outro contexto: confirme antes de acusar).
- **app envia sem handle_in:** vai receber `phx_error`; o app trata?
- **handle_in que o app nunca envia:** outro ator dispara (o outro papel, um job). É a lista de eventos que o `phx_actor.mjs` precisa provocar.

A matriz multiusuário dele diz, por evento, quem é o ator B (mesmo app ou `phx_actor`) e quais bugs tentar. Detalhes em `05-multiusuario-tempo-real.md`.

## 4. Do mapa ao plano

Plano de uma sessão cabe em 10 linhas e vai no brief, não no relatório:

```
1. login papel A (Maestro login-por-papel)            feliz
2. fluxo principal A: entrar na aula → responder      feliz + duplo-toque + sem-rede
3. ator B cria pergunta (phx_actor)                   A reflete? ordem? reconexão no meio?
4. tela /class/[id]: deep link frio e deslogado
5. tours: after-hours (10 min background), saboteur (toxiproxy timeout)
6. fonte grande + escuro nas 3 abas (fonte-grande-e-escuro.yaml)
7. limpeza
```

Cada linha tem oráculo escrito antes de rodar. O que não couber no tempo fica como "não testado" no relatório, com a lista.

## Fontes

- Expo Router file-based routing: https://docs.expo.dev/router/introduction/
- Maestro `hierarchy` (PrintHierarchyCommand): https://raw.githubusercontent.com/mobile-dev-inc/maestro/main/maestro-cli/src/main/java/maestro/cli/App.kt
- Phoenix Channels: https://hexdocs.pm/phoenix/channels.html
