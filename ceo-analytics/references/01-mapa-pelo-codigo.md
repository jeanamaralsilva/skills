# Mapa pelo código

O mapa é o inventário que sustenta todo o resto. Ele responde, para cada tela: para que ela existe, o que tem nela, para que serve cada elemento, que estados ela trata e para onde ela leva.

## 1. Comece pelo script

```bash
python <skill>/scripts/map_routes.py <repo>          # texto
python <skill>/scripts/map_routes.py <repo> --json   # para o subagente
```

Ele detecta Expo Router, React Navigation, Next (app dir), Flutter (GoRoute), Compose (`composable("rota")`) e SwiftUI (NavigationStack, TabView, `.sheet`). Sai com código 2 quando não acha nada: aí o app usa navegação própria e você lê o ponto de entrada à mão (`App.tsx`, `main.dart`, `MainActivity.kt`, `@main`).

Rotas finas: muitos repos deixam em `app/` só `export { default } from '@/screens/...'`. O script segue esse reexport e mostra `rota -> arquivo real`. Analise sempre o arquivo real, nunca o wrapper.

Limite: rotas montadas em runtime (lista de telas vinda de API, `navigate(variavel)`) não aparecem. Procure por `navigate(`, `router.push(`, `Navigator.push`, `navController.navigate` para completar.

## 2. Onde olhar por stack

| Stack | Estrutura de navegação | Tela | Tema e componentes |
|---|---|---|---|
| Expo Router | `app/_layout.tsx`, `(grupos)`, `[param].tsx` | arquivo em `app/` | `theme/`, `constants/Colors.ts`, `components/ui/` |
| React Navigation | `create*Navigator`, `*.Screen` | prop `component` ou `getComponent` | `theme`, `styled-components`, `tamagui.config` |
| Next | `app/**/layout.tsx` | `page.tsx` | `tailwind.config`, `components/ui` |
| Flutter | `GoRouter`, `MaterialApp.routes` | `Widget` da rota | `ThemeData`, `lib/theme` |
| Compose | `NavHost` | função `@Composable` da rota | `MaterialTheme`, `ui/theme/` |
| SwiftUI | `NavigationStack`, `TabView` | `View` | `Assets.xcassets`, extensões de `Color` |

## 3. Design system do repo

Antes de julgar qualquer tela, descubra o vocabulário que o repo já tem:

```bash
ls <repo>/src/components/ui <repo>/components 2>/dev/null
grep -rhoE "<(Button|Card|Sheet|Modal|Input|Skeleton|Toast)\b" <repo>/src | sort | uniq -c | sort -rn
grep -rnE "#[0-9a-fA-F]{6}\b" <repo>/src --include=*.tsx | wc -l   # cores hardcoded
```

Componente local que repete a função de um do DS vai para a lista "fora do DS". Não é achado de UX, é achado de consistência (H04).

## 4. Para cada tela, extraia

- **Objetivo**: uma frase, pela ótica do usuário ("aluno vê o treino do dia").
- **Elementos interativos**: botões, inputs, listas tocáveis, gestos. Para cada um, a ação que dispara.
- **Estados**: procure pelo que o código trata de fato.
  - loading: `isLoading`, `isPending`, `isFetching`, `ActivityIndicator`, `Skeleton`
  - vazio: `data?.length === 0`, `ListEmptyComponent`
  - erro: `isError`, `error`, `catch`, `ErrorBoundary`
  - offline: `NetInfo`, `useNetInfo`
  - sucesso: toast, navegação de volta, invalidação de query
- **Saídas**: `navigate`, `push`, `back`, `replace`, deep links.

Um estado que o código não trata é um achado com evidência forte: a linha que devia tratar e não trata.

## 5. Modelo de mapa explícito

O Expensify mantém `src/ROUTES.ts` e `src/SCREENS.ts` como catálogo de todas as rotas e telas (`data/reference-apps.csv`, R02). O mapa que você entrega segue a mesma ideia: uma linha por tela.

## Saída

```
| Tela | Rota | Arquivo:linha | Objetivo | Elementos-chave | Estados | Saídas |
```

Mais a lista "fora do DS" e a contagem de literais de cor/px. Sem recomendação nesta fase.
