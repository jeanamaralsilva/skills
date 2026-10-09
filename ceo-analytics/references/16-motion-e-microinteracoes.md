# Motion e micro-interações

Movimento é o que separa o app que "parece premium" do que "parece template". Mas movimento sem regra vira ruído e jank. Esta referência diz **o que** animar, **quanto** e **com qual API em cada plataforma**. O catálogo consultável está em `data/motion-patterns.csv` (MO01 a MO45): `python scripts/search.py "ícone de aba pulsar"`.

## Princípios (valem nas três plataformas)

1. **Movimento tem causa.** Toda animação responde a algo que o usuário fez ou a algo que mudou. Animação ornamental sem gatilho é a primeira coisa a cortar.
2. **Rápido e com spring.** Interação direta: 100 a 160 ms. Mudança de estado de UI: abaixo de 300 ms. Navegação: 300 a 400 ms. Spring com `bounce` baixo (0 a 0,2) em quase tudo; bounce alto só em celebração. Apple: `.spring(duration:bounce:)`; Material: tokens `motionSpring*`; Reanimated: `withSpring({ damping, stiffness })` ou `.springify()`.
3. **Uma coisa viva por tela.** Um loop decorativo (gradiente lento, breathe) por tela, 6 a 10 s por ciclo, pausado quando a tela sai de foco. Dois loops competem; três é tela de cassino.
4. **Só `transform` e `opacity`** em loops e gestos. Animar layout (width, height, padding), cor de fundo de muitos itens ou sombra força relayout e repaint: é a origem do jank no Android médio.
5. **Reduce Motion é obrigatório.** iOS: `@Environment(\.accessibilityReduceMotion)`; RN: `AccessibilityInfo.isReduceMotionEnabled()` / `useReducedMotion()` do Reanimated; Android: `Settings.Global.ANIMATOR_DURATION_SCALE`. Movimento grande vira fade; loop decorativo some.
6. **Haptic acompanha o estado, não o toque.** Seleção ao trocar aba ou picker; sucesso ao concluir; erro leve ao falhar. Nunca no scroll.

## Os quatro pedidos mais comuns

### Ícone da aba que reage ao selecionar

| Plataforma | Como | Nota |
|---|---|---|
| iOS 17+ (SwiftUI) | `Image(systemName:).symbolEffect(.bounce, value: selectedTab)` para um pulo único; `.symbolEffect(.pulse, isActive: isSelected)` para pulsar enquanto ativo; `.contentTransition(.symbolEffect(.replace))` para trocar outline → filled (MO01, MO02, MO09) | SF Symbols animam de graça; iOS 26 adiciona `.drawOn` (MO07) |
| Android (Compose) | `AnimatedImageVector` com `rememberAnimatedVectorPainter(image, atEnd = selected)` (MO32); ou `scale` por `animateFloatAsState` com `MotionScheme.expressive()` (MO23) | M3 Expressive já anima o indicador da navigation bar |
| React Native (Expo) | `NativeTabs` do Expo Router com `Icon sf= md=` dá a tab bar nativa (MO42); `expo-symbols` `SymbolView animationSpec={{ effect: { type: 'bounce' } }}` para o pulo no iOS (MO41, iOS only, beta); animação própria com Reanimated `withSequence(withSpring(1.15), withSpring(1))` em `transform: scale` (MO35) | Não há animação de seleção documentada no NativeTabs: se o CEO quer o pulso, é componente próprio por cima |

Regra: pulso único na seleção (≤ 250 ms). Pulso contínuo só em estado "ao vivo" (gravando, aula em andamento), e pausado quando a aba não está visível.

### Gradiente lento, quase imperceptível, atrás do ícone

| Plataforma | Como | Nota |
|---|---|---|
| iOS 18+ | `MeshGradient(width: 3, height: 3, points: ..., colors: ...)` dentro de `TimelineView(.animation)` movendo 1 ou 2 pontos (MO17); iOS 26: `.symbolColorRenderingMode(.gradient)` no próprio símbolo (MO10) | Ciclo de 8 s; amplitude de 2 a 4% da área |
| Android 13+ | `ShaderBrush(RuntimeShader(agsl))` em `drawWithCache`, uniform `time` (MO33); abaixo da API 33, `Brush.linearGradient` com offset animado | Shader roda na GPU; ok para 1 elemento, não para lista |
| React Native | Skia `LinearGradient` com `colors` por `useDerivedValue` + `interpolateColors` e `useClock` (MO43); sem Skia, `expo-linear-gradient` com `Animated` em `translateX` de um gradiente 2x maior | Nunca animar `colors` de `expo-linear-gradient` frame a frame: re-render por frame |

Se o CEO diz "quase imperceptível", meça: a diferença de cor entre os extremos do ciclo deve ser ≤ 8 de luminância (ΔL*) e o ciclo ≥ 6 s. Mais que isso é "gradiente dançando".

### Sheet que reage ao arrastar (rubber band, snap)

| Plataforma | Como | Nota |
|---|---|---|
| iOS 16+ | `.presentationDetents([.medium, .large])` dá snap, resistência e dismiss interativo de graça; `.presentationBackgroundInteraction(.enabled)` para tocar atrás | iOS 26: sheet com Liquid Glass recuada das bordas; não desenhe sheet própria onde a nativa serve |
| Android | `ModalBottomSheet` do M3 com `rememberModalBottomSheetState(skipPartiallyExpanded = false)`; predictive back encolhe o sheet (MO30) | |
| React Native | `@gorhom/bottom-sheet` ou `react-native-true-sheet` (nativo); custom com Gesture Handler 3 `usePanGesture({ onUpdate, onDeactivate })` + shared value e `withSpring` para o snap; rubber band = deslocamento além do limite dividido por 3 (MO40) | O snap decide pela velocidade (`velocityY`), não só pela posição |

Oráculo: arrastar 20 px e soltar volta ao detent (não fecha); arrastar rápido para baixo fecha mesmo com 40 px; conteúdo rola dentro do sheet só quando está expandido.

### Transições entre telas

| Plataforma | Como | Nota |
|---|---|---|
| iOS 18+ | `.navigationTransition(.zoom(sourceID:in:))` + `.matchedTransitionSource` (MO14): card vira detalhe | iOS 26 mantém; combine com `matchedGeometryEffect` dentro da mesma tela (MO13) |
| Android | `SharedTransitionLayout` + `Modifier.sharedElement(rememberSharedContentState(key))` (MO29); predictive back com preview (MO30) | |
| React Native | Reanimated layout animations: `entering={FadeInDown.duration(250)}`, `exiting`, `layout={LinearTransition.springify()}` (MO37, MO38); shared element (`sharedTransitionTag`) ainda experimental: não em produção (MO39); navegação nativa via `react-native-screens` (stack nativa) dá a transição do sistema | Expo Router `Stack` já usa a stack nativa; não reimplemente o push |

## Receita de implementação (React Native, o caso mais comum)

```tsx
// pulso único na seleção da aba
const scale = useSharedValue(1);
useEffect(() => { if (focused) scale.value = withSequence(withSpring(1.15, { damping: 12 }), withSpring(1, { damping: 14 })); }, [focused]);
const style = useAnimatedStyle(() => ({ transform: [{ scale: scale.value }] }));
// Reduce Motion
const reduce = useReducedMotion(); // Reanimated
if (reduce) scale.value = 1;
```

Reanimated 4 traz animações e transições em sintaxe CSS (`animationName`, `transitionProperty`, MO35, MO36): para loops decorativos simples é menos código e roda na thread de UI.

## Checklist para a proposta

- [ ] Cada animação tem gatilho nomeado (seleção, chegada de dado, erro, conclusão).
- [ ] Duração e curva declaradas (ex.: "spring 0,35 s bounce 0,15").
- [ ] Um loop decorativo por tela, com ciclo e pausa fora de foco.
- [ ] Só transform/opacity em loops e gestos.
- [ ] Comportamento com Reduce Motion escrito.
- [ ] Haptic por estado, listado.
- [ ] Paridade: o que o Android faz quando o iOS usa SF Symbols ou Liquid Glass (`05-plataformas.md`).
- [ ] Custo: `17-performance-cross-platform.md`, orçamento de componentes animados.

## Fontes

- SF Symbols effects: https://developer.apple.com/documentation/symbols/symboleffect ; iOS 26 drawOn: https://developer.apple.com/documentation/symbols/drawonsymboleffect
- SwiftUI: https://developer.apple.com/documentation/swiftui/view/phaseanimator(_:trigger:content:animation:) ; zoom transition: https://developer.apple.com/documentation/swiftui/navigationtransition/zoom(sourceid:in:) ; MeshGradient: https://developer.apple.com/documentation/swiftui/meshgradient ; spring: https://developer.apple.com/documentation/swiftui/animation/spring(duration:bounce:blenddurations:)
- HIG Motion: https://developer.apple.com/design/human-interface-guidelines/motion
- Material 3 motion e Expressive: https://m3.material.io/styles/motion/overview ; Compose shared element: https://developer.android.com/develop/ui/compose/animation/shared-elements ; predictive back: https://developer.android.com/guide/navigation/custom-back/predictive-back-gesture ; AGSL: https://developer.android.com/develop/ui/views/graphics/agsl
- Reanimated 4 (CSS animations, layout animations, shared element status): https://docs.swmansion.com/react-native-reanimated/ ; Gesture Handler 3: https://docs.swmansion.com/react-native-gesture-handler/
- Expo: `expo-symbols` https://docs.expo.dev/versions/latest/sdk/symbols/ ; NativeTabs https://docs.expo.dev/router/advanced/native-tabs/ ; Haptics https://docs.expo.dev/versions/latest/sdk/haptics/
- Skia gradient: https://shopify.github.io/react-native-skia/docs/shaders/gradients ; Rive: https://rive.app/docs/runtimes/react-native/react-native
