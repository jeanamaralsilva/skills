# Implementação em React Native (Expo)

Alvo: arquitetura nova (Fabric), Expo com `expo-router`, sem módulo nativo novo. Tudo abaixo usa `react-native-svg`, `react-native-reanimated` e `react-native-screens`, que quase todo app Expo já tem. Confira no `package.json` antes; se faltar algum, é build de loja e passa pela `ceo-deps`.

## Por que componente próprio

Conferido em 09/10/2026 (`data/rn-libs.csv`, com fonte por linha):

- `react-native-copilot`, `rn-tourguide` e `react-native-spotlight-tour` têm issue aberta de arquitetura nova. A do spotlight-tour é exatamente Expo + Fabric no iOS (recorte e balão invisíveis).
- `react-native-walkthrough-tooltip` está mantida e serve para balão simples, mas não faz recorte nem tour.
- `@edwardloopez/react-native-coachmark` tem o melhor desenho (máscara SVG, `measureInWindow`, auto-scroll, a11y, reduzir movimento, storage plugável), mas tem mantenedor único e não foi testada em todas as versões de RN. Use como referência (MIT, copie trechos com crédito).
- O caso comum é 80% dica de 1 passo + checklist + empty state. Isso cabe em ~300 a 400 linhas [estimado], com controle de tema, texto, a11y e eventos.

**Plano B** (ganhar tempo): instalar `@edwardloopez/react-native-coachmark` (só JS, sai por OTA se as peers já estão no build), escrever o adaptador de storage para a versão de MMKV do app (o `mmkvStorage` embutido usa `new MMKV`, API antiga) e validar em iOS e Android na versão de RN do app antes de adotar.

## Peças

| Peça | Faz |
|---|---|
| `TipProvider` | Contexto no root. Guarda o registro de alvos, a fila, o estado visto/dispensado (cache local + servidor) e a regra de 1 automática por sessão. Expõe `requestTip(id)`, `dismiss(id)`, `complete(id)`, `resetTips()`. |
| `TipAnchor id` | Envolve o alvo. Registra o `ref` no provider (`Map<id, ref>`) ao montar, remove ao desmontar. Não muda o layout do filho. |
| `TipOverlay` | Desenha máscara, recorte e balão. Um só, no topo da árvore. |
| `useTipOnFocus(id, ready)` | Na tela: pede a dica quando a tela ganha foco (`useFocusEffect`) **e** `ready` (dados carregados, lista renderizada). |
| `FirstStepsCard` | Card do checklist na home. Itens vêm do servidor. "2 de 5", barra, fechar. Cada item navega para a tela da ação e chama `requestTip` lá. |
| `EmptyState` | Ícone, 1 frase do porquê, botão da ação. Use em `ListEmptyComponent`. Diferencie de loading e de erro. |

## Medir o alvo

- `ref.current.measureInWindow((x, y, w, h) => ...)` depois de `requestAnimationFrame` ou `InteractionManager.runAfterInteractions`, para pegar o layout final.
- Meça de novo em: foco da tela, `onLayout` do alvo, mudança de `Dimensions` (rotação), teclado abrindo ou fechando (`Keyboard` listeners), fim do scroll.
- `w === 0 || h === 0` ou fora da tela: não mostre. Se o alvo está numa `ScrollView`/`FlatList`, role até ele primeiro (`scrollTo`/`scrollToIndex`) e meça no fim do scroll.
- **Android:** `measureInWindow` e `Modal` podem desalinhar pela altura da status bar, sobretudo com edge-to-edge (issues #21 do coachmark e #203 do spotlight-tour). Teste em aparelho ou emulador com edge-to-edge e compense com `StatusBar.currentHeight` ou `useSafeAreaInsets` só se medir o desvio.

## Desenhar

- Host: `FullWindowOverlay` do `react-native-screens` no iOS (fica acima de sheets nativos) e `Modal transparent statusBarTranslucent` no Android. Ou um Portal no root se o app já tem um.
- Máscara: `Svg` tela cheia com `Defs > Mask`: um `Rect` branco tela cheia e um `Rect` preto com `rx` no lugar do alvo (com margem de 6 a 8 pt [estimado]); um `Rect` escurecido usando a máscara.
- Toque: o overlay escurecido fecha a dica; o buraco precisa deixar o toque passar. Jeito simples: quatro `Pressable` ao redor do recorte (cima, baixo, esquerda, direita) e nada no buraco, com o host em `pointerEvents="box-none"`. Tocar no alvo dispara a ação real e o provider chama `complete(id)`.
- Balão: abaixo do alvo se couber, senão acima (flip). Limite à área segura. Seta apontando para o centro do alvo. Texto + "Entendi" + "Pular dicas" (+ "1 de 3" no mini-tour).
- Animação: Reanimated, fade + escala curta (150 a 250 ms [estimado]). Com `useReducedMotion()` (síncrono), só fade ou nada.

## Acessibilidade

- Balão com `accessibilityViewIsModal` (iOS) e o resto do app com `importantForAccessibility="no-hide-descendants"` (Android) enquanto a dica está aberta.
- Ao abrir: `AccessibilityInfo.announceForAccessibility(texto)` e foco no texto (`AccessibilityInfo.setAccessibilityFocus` com `findNodeHandle`).
- Botões com `accessibilityRole="button"` e `accessibilityLabel` claros ("Pular todas as dicas").
- Leitor de tela ligado: o alvo não está acessível por baixo do overlay, então ofereça no balão um botão "Ir para <ação>" que executa a mesma ação.
- Contraste do texto 4,5:1 (WCAG 1.4.3), alvo de toque 44 pt (Apple HIG), texto cresce com a fonte do sistema e o balão quebra linha sem cortar.
- Fontes: https://reactnative.dev/docs/accessibility , https://docs.swmansion.com/react-native-reanimated/docs/device/useReducedMotion/ , https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum

## Sistema

- **Android voltar:** `BackHandler` fecha a dica e retorna `true`.
- **Navegação:** a tela perdeu foco, a dica fecha sem contar como dispensada.
- **App em background:** fecha; não reabre sozinho na mesma sessão.
- **Sessão:** "sessão" é do cold start até o app ficar em background por mais de N minutos (30 [estimado]). Guarde em memória, não em disco.
- **Fila:** um pedido por vez; se já mostrou a automática da sessão, novos pedidos automáticos são descartados (não enfileirados para depois). Pedido vindo de toque do usuário (item do checklist, "Rever dicas") ignora o limite.

## Checklist

- Itens e estado vêm do servidor (`04`), já derivados de dados reais. O app não decide se o item está feito.
- Atualiza ao voltar para a home (invalide a query no foco ou após a mutação da ação).
- Item que depende de outro só aparece depois (ex.: pacote só depois do 1º cliente).
- Completo: mostra um "Tudo pronto" uma vez e some. Fechado: some e não volta; acessível de novo em "Rever dicas".
