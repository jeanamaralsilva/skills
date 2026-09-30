# Propostas de tela

Uma proposta boa tem uma hipótese. Três variações de cor não são três propostas: são uma proposta indecisa.

## Quantas e quais

**2 ou 3 alternativas, cada uma apostando numa hipótese diferente.** Exemplo, para a tela "executar treino":

- **A. Foco na série atual:** um exercício por vez em tela cheia, timer de descanso grande, próximo exercício em prévia. Aposta: menos distração no meio do treino.
- **B. Lista do treino inteira:** todas as séries visíveis com a coluna "anterior", check por série e timer em barra fixa. Aposta: o aluno quer ver o todo e registrar rápido.
- **C. Híbrido:** lista com a série ativa expandida e o resto recolhido.

Recomende uma, com o porquê em uma frase ligada a evidência (benchmark, review, heurística).

## O que cada alternativa tem que ter

Use `assets/screen-proposal-template.md`:

1. **Hipótese** em uma frase.
2. **Estrutura:** wireframe ou mockup, com a hierarquia de cima para baixo.
3. **Componentes do DS** usados. Gap no DS vira pedido, não componente inventado.
4. **Estados:** default, loading, vazio, erro, offline e sucesso. Desenhe pelo menos o loading e o erro.
5. **iOS:** onde entra o Liquid Glass (só navegação e controles flutuantes).
6. **Android:** quais elementos do Material 3 Expressive (motion por spring, button group, loading indicator).
7. **Funções:** o que a tela faz de novo. Exemplos: Live Activity, optimistic UI, desfazer.
8. **Risco:** o que pode dar errado ou o que custa caro implementar.

## Onde desenhar

| Situação | Onde |
|---|---|
| O Jean usa Pencil ou o repo tem `.pen` | Pencil MCP: frame por alternativa, lado a lado |
| Exploração visual rápida, fora de repo | artifact do tipo Design |
| Proposta já aprovada, para implementar | código no repo, com `pixel-perfect` contra a referência |
| Repo INFLEET | componentes HeraDS (`infleet-herads`) |
| Tema do repo definido (ex.: dark-only) | respeite o tema, não proponha modo claro |

## Qualidade antes de mostrar

- Passe a proposta pela lista de `07-anti-slop-visual.md`. Troque o logo mentalmente: se servir para qualquer app, está genérica.
- Use dado realista: nome de exercício longo, 0 itens, 50 itens, texto em pt-BR.
- Toque mínimo: 44pt no iOS e 48dp no Android. CTA principal na metade de baixo.
- Contraste de todo texto sobre fundo novo medido com `contrast.py`.

## Depois da escolha

A alternativa aprovada vira a referência. A partir daí vale `09-estabilidade-de-tela.md`: ajustes posteriores não redesenham.
