# Mapa pelo app rodando

O código diz o que a tela pode fazer. O app rodando diz o que ela faz de verdade: tempo de resposta, o que aparece primeiro, o que some, o que trava. A NN/g alerta que análise feita só a partir de texto perde exatamente isso.

## Ferramenta por alvo

| Alvo | Ferramenta | Observação |
|---|---|---|
| Web local ou publicado | `agent-browser` em sessão isolada, ou Claude in Chrome | `agent-browser errors` pega a exceção que o print esconde |
| React Native / Expo | argent no simulador | iOS por padrão, Android quando o assunto for Android |
| Nativo iOS/Android | simulador ou emulador com argent | mesmo ciclo |

Os comandos de gravação, print e sessão estão em `send-pr/references/visual-evidence.md`. Não copie para cá: leia lá antes do primeiro `screen-recording-start` ou `agent-browser open`.

Se o app não sobe (sem backend, sem credencial), pare e diga isso. Não descreva uma tela que você não viu.

## O que capturar

1. **Um print por estado que muda**: inicial, carregando, com dado, vazio, erro, sucesso. Não um print por página do produto.
2. **Tempo percebido** de cada ação principal, rotulado pela faixa da NN/g:
   - até 0,1s: instantâneo
   - até 1s: fluxo mantido
   - até 10s: atenção mantida, precisa de indicador
   - acima de 10s: precisa de progresso

   Escreva `[medido]` ao lado. Cronometre com o timestamp da gravação, não no olho.
3. **Alvos de toque** abaixo de 44x44pt (iOS) ou 48x48dp (Android). No web, `getBoundingClientRect()`.
4. **Voltar do Android**: fecha sheet? volta tela? sai do app sem querer?
5. **Gestos** que brigam com os do sistema (swipe da borda, home indicator).
6. **Acessibilidade rápida**: fonte grande do sistema ligada quebra o layout? Reduce Motion e Reduce Transparency (iOS) mudam algo?

Salve tudo fora do repo, no scratchpad, com nome `<fluxo>-<passo>-<estado>.png`.

## Saída

```
fluxo → passo → print → tempo [medido] → observação factual
```

Observação factual é o que aconteceu ("o botão ficou 2,3s sem feedback [medido]"), não o que devia acontecer. A opinião vem na fase de diagnóstico.
