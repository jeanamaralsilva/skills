# Estabilidade de tela: mexer só no que foi pedido

O pedido "ajusta o botão" não autoriza reorganizar a tela. Quando cada rodada move padding, ordem ou raio, o time perde a referência e o CEO perde a confiança no agente. A pesquisa chama isso de *design drift*, e ele piora a cada revisão: o modelo otimiza a partir da própria última saída e a tela converge para o genérico.
Fontes: https://www.superdesign.dev/blog/ai-design-system-drift e https://uxdesign.cc/ai-design-isnt-ugly-it-s-fluent-and-that-s-the-problem-131b2f4eb78c

## O ciclo

### 1. Baseline antes de tocar em qualquer coisa

- **Web:** `npx playwright screenshot --viewport-size "<w>,<h>" <url> baseline.png`
- **Mobile:** print ou gravação com argent do estado atual, na mesma tela e no mesmo estado.

### 2. Declarar a região

Escreva, antes de editar, o que o pedido toca. Exemplo: "região: botão Salvar e o estado de loading dele". Todo o resto está travado: ordem, espaçamento, textos, cores e componentes.

### 3. Editar só dentro da região

No código, o diff tem que ficar contido nos elementos declarados. `git diff --stat` com arquivos fora do esperado é sinal de alerta.

Não reindente o que não mudou. Se mover um bloco para dentro de um novo container obriga a reindentar, prefira uma estrutura que não obrigue (container irmão, `Fragment` já existente, estilo absoluto). O diff bruto não pode passar de 2x o `git diff -w`: diff inflado esconde a mudança real do revisor. Deixe o formatter do repo (Prettier) só para o que você tocou.

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

Aí a disposição pode mudar, mas pelas propostas de `11-propostas-de-tela.md`, aprovadas pelo CEO antes de virar código. Depois de aprovada, a proposta vira a nova referência e a regra de estabilidade volta a valer.

## Entrega

Mudança visível sobe num PR com o antes e depois anexados (pela skill de PR da config, se houver).
