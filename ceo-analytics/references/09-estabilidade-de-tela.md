# Estabilidade de tela: mexer só no que foi pedido

O pedido "ajusta o botão" não autoriza reorganizar a tela. Quando cada rodada move padding, ordem ou raio, o time perde a referência e o Jean perde a confiança no agente. A pesquisa chama isso de *design drift*, e ele piora a cada revisão: o modelo otimiza a partir da própria última saída e a tela converge para o genérico.
Fontes: https://www.superdesign.dev/blog/ai-design-system-drift e https://uxdesign.cc/ai-design-isnt-ugly-it-s-fluent-and-that-s-the-problem-131b2f4eb78c

## O ciclo

### 1. Baseline antes de tocar em qualquer coisa

- **Web:** `node <pixel-perfect>/scripts/capture.mjs --url <url> --width <w> --height <h> --out baseline.png`
- **Mobile:** print ou gravação com argent do estado atual, na mesma tela e no mesmo estado.

### 2. Declarar a região

Escreva, antes de editar, o que o pedido toca. Exemplo: "região: botão Salvar e o estado de loading dele". Todo o resto está travado: ordem, espaçamento, textos, cores e componentes.

### 3. Editar só dentro da região

No código, o diff tem que ficar contido nos elementos declarados. `git diff --stat` com arquivos fora do esperado é sinal de alerta.

### 4. Diff visual depois

```bash
magick compare -metric AE baseline.png depois.png diff.png 2>&1
```

Leia o `diff.png`:
- Vermelho **dentro** da região: a mudança pedida.
- Vermelho **fora** da região: regressão. Corrija antes de entregar.
- Contornos de glifo apenas: ruído de rasterização. Pode seguir.

### 5. Comparar com a original

Numa sequência de ajustes, a comparação é sempre com o baseline do primeiro pedido, não com a iteração anterior. É isso que impede a convergência.

## Quando o pedido é "redesenha"

Aí a disposição pode mudar, mas pelas propostas de `11-propostas-de-tela.md`, aprovadas pelo Jean antes de virar código. Depois de aprovada, a proposta vira a nova referência e a regra de estabilidade volta a valer.

## Entrega

Mudança visível sobe com `send-pr`, que grava o antes e depois e anexa no PR. Não duplique aqui o que ele já faz.
