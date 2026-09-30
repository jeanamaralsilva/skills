# Plataformas: iOS 26 e Android Material 3 Expressive

Regra de ouro: cada plataforma com o seu idioma. Um app que leva o visual do iOS para o Android, ou o contrário, parece estrangeiro nos dois.

## iOS 26: Liquid Glass

**O que é:** um material dinâmico que forma uma camada funcional para controles e navegação, por cima do conteúdo. Barras, sheets, popovers e controles padrão do SwiftUI e UIKit adotam o material sozinhos ao recompilar com o SDK novo.
Fonte: https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass

**Onde usar:**
- Só na camada de navegação: tab bar, toolbar, sidebar, sheets e controles flutuantes.
- Half sheets ficam recuadas das bordas e ficam mais opacas quando expandem.
- Remova backgrounds customizados das barras: eles brigam com o vidro.

**Onde não usar:**
- Em cards ou células de conteúdo.
- Vidro sobre vidro.
- Em todo controle custom: a Apple diz "avoid overusing".

**Legibilidade:**
- A NN/g (out/2025) criticou texto sobre vidro sobre imagem, animação em excesso e alvos pequenos: https://www.nngroup.com/articles/liquid-glass/
- Todo texto sobre vidro precisa de contraste medido com `scripts/contrast.py` contra o pior fundo possível.
- Teste com **Reduce Transparency** e **Reduce Motion** ligados.

**SwiftUI:**
- `.glassEffect(_:in:)` e `GlassEffectContainer`: agrupa elementos e permite morph entre eles.
- `.buttonStyle(.glass)` e `.glassProminent`.
- `.tabBarMinimizeBehavior(.onScrollDown)` e `Tab(role: .search)`.
- `safeAreaBar` e `backgroundExtensionEffect()`.

**React Native / Expo:**
- `expo-glass-effect`: `GlassView` e `GlassContainer`, com as props `glassEffectStyle`, `tintColor` e `isInteractive`.
  - Checagem: `isLiquidGlassAvailable()`.
  - Só iOS 26+. Nas outras plataformas vira `View`.
  - `opacity: 0` quebra o efeito.
  - https://docs.expo.dev/versions/latest/sdk/glass-effect/
- `@callstack/liquid-glass`: `LiquidGlassView`. Exige RN 0.80 ou maior e Xcode 26, não roda no Expo Go.
- Fallback: `expo-blur` no iOS antigo. No Android, blur eficiente só existe a partir do 12. Abaixo disso, use fundo sólido.

**Padrão de código:**
```tsx
const Surface = isLiquidGlassAvailable() ? GlassView : SolidSurface
```
Nunca deixe o Android herdar um blur que imita o iOS.

## Android: Material 3 Expressive

**Por que é "o Android mais bonito" com base em dado:** o Google fez 46 estudos com mais de 18 mil participantes. Os usuários acharam os elementos-chave até 4x mais rápido, a faixa de 18 a 24 anos preferiu em até 87%, e usuários com 45+ chegaram à velocidade dos mais jovens. O próprio Google avisa que expressividade não pode quebrar padrão de usabilidade.
Fonte: https://design.google/library/expressive-material-design-google-research

**O que muda:**
- **Motion por spring**, com `MotionScheme.expressive()` no Compose. Tem specs *spatial* (posição e tamanho) e *effects* (cor e opacidade).
- **35 formas novas** com shape morph.
- **Componentes novos ou atualizados**: button groups, split button, FAB menu, toolbars e loading indicator expressivo.
- **Cor dinâmica** (Material You) quando o produto permite.

**React Native:**
- `react-native-bottom-tabs` (Callstack) declara estilo Material 3 Expressive nativo no Android: https://oss.callstack.com/react-native-bottom-tabs/docs/guides/android-native-styling
- Springs do Reanimated 4 para imitar o motion (`withSpring` com damping e duração).
- React Native Paper v6 alpha tem tokens de spring, mas não encontramos suporte declarado a Expressive. Não prometa o que a lib não entrega.

**Fontes abertas para consultar M3:** o site m3.material.io vem vazio por fetch. Use os `.md` do repo `material-components-android` ou o Android Developers (`data/market-sources.csv`, M06 e M07).

## Comum aos dois

| Item | iOS | Android |
|---|---|---|
| Alvo de toque mínimo | 44x44pt | 48x48dp |
| Tamanho de fonte | Dynamic Type | `sp`, respeitando a escala do sistema |
| Voltar | swipe da borda | botão ou gesto do sistema, que fecha sheet antes de sair da tela |
| Navegação principal | tab bar (até 5) | navigation bar (3 a 5 destinos) |
| Haptics | `UIFeedbackGenerator` | `performAndroidHapticsAsync`; a doc do Expo desaconselha `impactAsync` no Android |
