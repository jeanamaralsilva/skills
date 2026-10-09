# Performance cross-platform: bonito no iOS sem ficar pesado no Android

A proposta que só roda lisa num iPhone Pro não é proposta. O Android médio do mercado brasileiro tem 4 a 6 GB de RAM, GPU modesta e tela de 60 Hz. Toda proposta de tela nesta skill declara o custo e o que o Android faz diferente.

## Orçamentos

| Métrica | iOS | Android | Como medir |
|---|---|---|---|
| Frame | 16,7 ms (60 Hz), 8,3 ms (ProMotion 120 Hz) | 16,7 ms; janky frame = acima disso; P90 e P95 do `gfxinfo` | Instruments Animation Hitches; `adb shell dumpsys gfxinfo <pkg>` |
| Jank aceitável | hitch time ratio < 5 ms/s | < 5% de janky frames no fluxo | idem |
| Componentes animados ao mesmo tempo | dezenas | poucos (ordem de dez) em aparelho fraco com Reanimated; lista com item animado precisa de `memo` e `windowSize` baixo | React DevTools Profiler; `onBlankArea` do FlashList |
| Blur / glass | barato (Metal, Liquid Glass nativo) | caro: `BlurView` em lista é jank garantido; use em 1 elemento fixo (header) ou troque por cor sólida com alpha | `gfxinfo` antes e depois |
| Sombra | `shadowRadius` barato no iOS | `elevation` nativa é barata; sombra customizada (react-native-shadow-2, imagem) é cara em lista | |
| Gradiente | barato | barato parado; caro animando `colors` (re-render); shader AGSL ok em 1 elemento (API 33+) | |
| Imagem | | `expo-image` com `recyclingKey`, `contentFit`, tamanho pedido ao servidor; nunca imagem 2000 px num avatar de 40 | `onBlankArea`, memória |
| Cold start | < 2 s até tela útil | < 2 s; Hermes + bytecode já ajuda; evite 30 imports no `_layout` | vídeo com timestamp |

## O que fica igual, o que muda

| Elemento | iOS | Android |
|---|---|---|
| Tab bar | Liquid Glass nativa (`NativeTabs`), ícone SF animado | Material navigation bar com indicador M3 Expressive; ícone Material Symbols; sem glass |
| Sheet | `presentationDetents`, glass | `ModalBottomSheet` M3, drag handle, predictive back |
| Botão de destaque | glass em toolbar flutuante | `FilledButton`/`FAB` M3 com shape morph expressivo |
| Loading | skeleton + `ProgressView` | skeleton + `LinearProgressIndicator` wavy (M3 Expressive) ou `CircularProgressIndicator` |
| Gradiente vivo atrás do ícone | MeshGradient 8 s | mesma cor com 1 gradiente linear que translada (sem shader) em API < 33; shader em ≥ 33 |
| Haptics | `sensoryFeedback` | `HapticFeedbackConstants.CONFIRM`/`REJECT` (API 30+), sem vibração longa |
| Fonte | SF Pro, Dynamic Type | Roboto/Google Sans, `fontScale`; textos crescem mais: reserve altura |
| Voltar | gesto da borda | botão/gesto do sistema; predictive back mostra a tela anterior: a animação de saída precisa ser cancelável |
| Blur em fundo | ok | evitar; alternativa: `backgroundColor` com alpha 0.92 sobre scrim |

## Regras para a proposta

1. **Toda proposta tem a coluna "Android":** o que muda e o que é omitido. "Igual" só quando é mesmo igual.
2. **Nada de blur em lista no Android.** Nem `BlurView`, nem `backdrop-filter`. Em um header fixo, com `experimentalBlurMethod` só em aparelho forte, ou cor sólida.
3. **Lista grande = FlashList (ou FlatList com `getItemLayout`), item memoizado, imagem com tamanho certo.** Proposta de card com 3 animações por item é vetada para lista; vale para o item em foco.
4. **Animações fora da JS thread.** Reanimated (`useAnimatedStyle`, layout animations, CSS animations) ou nativo. `Animated` com `useNativeDriver: false` para layout é jank certo no Android.
5. **Meça em release build.** Dev build é 2 a 5x mais lento. `eas build --profile preview` e um aparelho ou emulador com `-memory 1536` (quando houver Android).
6. **Declare o custo na proposta:** "1 gradiente animado (GPU), 1 pulso por seleção, 0 blur, lista com 2 Reanimated por item visível". Isso é o que o `ceo-testes` vai medir (`09-performance-e-memoria.md` lá).

## Sinais de proposta pesada

- Glass ou blur em mais de um elemento.
- Mais de um loop decorativo por tela.
- Sombra customizada em item de lista.
- Gradiente que muda de cor por frame via props.
- Ícone animado em todos os itens de uma lista.
- Imagem sem `recyclingKey`/tamanho em lista rolável.
- `onLayout` ou `measure` dentro de animação.

Qualquer um desses na proposta vira nota "custo alto no Android" com a alternativa ao lado.

## Fontes

- Android rendering e `gfxinfo`: https://developer.android.com/topic/performance/rendering/inspect-gpu-rendering ; jank: https://developer.android.com/topic/performance/vitals/render
- Apple hitches: https://developer.apple.com/documentation/xcode/analyzing-responsiveness-issues-in-your-shipping-app
- Reanimated performance: https://docs.swmansion.com/react-native-reanimated/docs/guides/performance ; worklets/UI thread: https://docs.swmansion.com/react-native-reanimated/docs/fundamentals/glossary
- FlashList: https://shopify.github.io/flash-list/docs/ ; FlatList: https://reactnative.dev/docs/optimizing-flatlist-configuration
- expo-image: https://docs.expo.dev/versions/latest/sdk/image/ ; expo-blur limitações Android: https://docs.expo.dev/versions/latest/sdk/blur-view/
- Material 3 Expressive componentes: https://m3.material.io/blog/building-with-m3-expressive
