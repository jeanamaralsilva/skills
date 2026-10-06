# Componentes premium

"App premium" não é efeito. É o componente certo para o tempo certo, com todos os estados desenhados e motion que responde ao usuário. A tabela-base é `data/components.csv` (C01 a C15). Consulte com `python scripts/search.py "<tema>" --domain components`.

## Todo componente proposto traz os estados

default, pressed, disabled, loading, error, empty (quando for lista) e success (quando for ação).

Proposta sem os estados é esboço. O maior vício de UI gerada por IA é desenhar só o caminho feliz.

## Loading: a receita

| Tempo esperado | Indicador | Fonte |
|---|---|---|
| < 1s | nenhum (indicador piscando atrapalha) | NN/g response times |
| 1 a 2s | spinner local no elemento que carrega | NN/g skeleton screens |
| 2 a 10s, página inteira com layout conhecido | skeleton **estático** e fiel ao layout final | NN/g skeleton screens |
| > 10s | barra de progresso com estimativa | NN/g response times |
| Ação reversível (like, favoritar, marcar série) | optimistic UI: mostra o resultado antes da resposta e reverte se falhar | react.dev useOptimistic |

Contraponto honesto: no estudo da Viget (2017, n=136), o skeleton teve o pior tempo percebido. Skeleton não é bala de prata. Ele funciona quando é fiel ao layout e quando o carregamento é de página inteira.

Não achamos estudo que compare shimmer com skeleton estático. Se propuser shimmer, é opinião.

Na prática em RN: um componente de skeleton que recebe a mesma estrutura da tela final. Assim, quando o dado chega, nada pula (sem layout shift).

## Bottom sheet

- **Quando:** interação curta e contextual (filtrar, escolher, confirmar, ajustar um valor).
- **Regras** (NN/g, https://www.nngroup.com/articles/bottom-sheet/):
  - Botão Fechar visível: só o grab handle deixa dúvida sobre o swipe.
  - O Voltar do Android fecha a sheet.
  - Não empilhar sheets.
  - Não usar sheet no lugar de um fluxo de várias páginas.
- **iOS 26:** a sheet nativa ganha Liquid Glass sozinha. Detents `.medium` e `.large`.
- **RN:** `@gorhom/bottom-sheet` 5 (aceita Reanimated 3.16+ ou 4). Use snap points, `enablePanDownToClose`, `BottomSheetBackdrop` e teclado tratado com `keyboardBehavior`.

## Bibliotecas

Antes de citar uma lib, confira versão, risco e o que o SDK fixa em `data/ui-libraries.csv` e `15-comunidade-e-ecossistema.md`. Regras de motion que valem sempre também estão lá.

## Motion e gestos

- **Reanimated 4.7:** exige New Architecture. Tem API de animações CSS e springs. Tudo roda na UI thread.
- **Gesture Handler 3:** para arrastar, swipe e pinch.
- **Skia 2:** para o que componente não faz (anel de progresso, gráfico, shader). Exige Reanimated 4 e React 19.
- **Não use moti** em código novo: sem release desde jan/2025 e compatibilidade com Reanimated 4 não confirmada.
- Motion responde a uma ação do usuário, e um único momento orquestrado por tela basta. Animação de entrada em toda seção é tell de IA (AV08).

## Haptics

Só em confirmação (série concluída, pagamento feito) e em seleção (picker, toggle). Um estudo com 92 pessoas mostrou que quase metade prefere digitar sem feedback, e o feedback não melhorou velocidade nem precisão. Vibrar em todo toque irrita.

`expo-haptics`: `notificationAsync` para sucesso e erro, `selectionAsync` para seleção, `performAndroidHapticsAsync` no Android.

## Empty state e primeiro uso

- **Empty state** (NN/g): comunica o status, ensina o que aparece ali e oferece uma ação direta. Área em branco nunca.
- **Onboarding:** tutorial em carrossel não melhorou o desempenho nos testes da NN/g. Prefira dica contextual no momento da ação.

## Recursos que usuários citam nas reviews (exemplo: apps de treino)

Pesquisa de 30/09/2026 em reviews públicas de Hevy, Strong, Smart Fit e BTFIT. Serve de modelo para buscar o equivalente em outros domínios:

- **Última execução ao lado da série atual** (coluna "Previous" do Hevy). As reclamações de Smart Fit e BTFIT são justamente sobre carga que não salva.
- **Timer de descanso que começa sozinho** ao marcar a série, com ±15s e pular.
- **Live Activity / Dynamic Island / relógio**: controlar sem abrir o app. É o recurso mais citado nas reviews do Strong.
- **PR detectado na hora**, com gráfico de progressão.
- **Maiores reclamações:** perder dado (sair no meio do treino apaga o progresso) e paywall de recurso que era grátis.

Método: `references/10-benchmark-mercado.md`. Fontes: App Store e Google Play do app, help center do produto.
