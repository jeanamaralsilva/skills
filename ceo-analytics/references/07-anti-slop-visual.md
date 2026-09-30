# Anti-slop visual: como uma tela denuncia que foi feita por IA

A Anthropic chama a causa de *distributional convergence*: sem direção, o modelo cai nas escolhas mais comuns dos dados de treino, e todas as telas ficam iguais.
Fonte: https://www.claude.com/blog/improving-frontend-design-through-skills

Use esta lista em dois sentidos: para **achar** o problema numa tela existente e para **não produzir** o problema numa proposta. A lista completa com fontes está em `data/anti-patterns.csv` (AV01 a AV10).

| ID | Sinal | Como detectar no código | O que fazer |
|---|---|---|---|
| AV01 | Gradiente roxo/índigo | `grep -rnE "indigo-|purple-|violet-|#6366F1|#8B5CF6"` sem vir do tema | A paleta vem do tema ou do brandbook do projeto |
| AV02 | Uma fonte só, sem escala | uma `fontFamily` só e tamanhos soltos (13, 15, 17...) | Escala tipográfica do DS: display, título, corpo, legenda |
| AV03 | SaaS card kit | o mesmo `borderRadius` e a mesma sombra em tudo, card dentro de card | Elevação e raio por hierarquia; nem todo conteúdo precisa de card |
| AV04 | Template chrome | eyebrow em caixa alta acima de todo título, seta em todo botão | Tirar o rótulo que não informa nada |
| AV05 | Hero genérico | número grande + label + gradiente, três boxes com ícone | Abrir com o que é do domínio (o treino de hoje, não "Bem-vindo!") |
| AV06 | Paleta de IA alternativa | creme + serif + terracota, ou preto + acento neon | É o mesmo vício com outra cor |
| AV07 | Emoji como ícone | emoji em JSX, `<Text>🔥</Text>` | Um set de ícones só (o do DS) |
| AV08 | Motion espalhado | `FadeInUp` em toda seção, `bounce` | Um momento orquestrado; motion responde a ação |
| AV09 | Glass gratuito | `BlurView` ou `GlassView` em card de conteúdo | Vidro só na camada de navegação (`05-plataformas.md`) |
| AV10 | Estados ausentes | tela sem loading, empty e error; CTA "Enviar" | Os estados de `06`, e o CTA diz o que acontece ("Salvar treino") |

## Copy

- **Frase que serve para qualquer produto é copy de IA:** "Desbloqueie seu potencial", "Sua jornada começa aqui".
- **O nome da ação é o mesmo no fluxo inteiro:** botão "Concluir treino" leva ao toast "Treino concluído".
- **Mensagem de erro** diz o que houve e o que fazer. Não se desculpa sem dizer nada.
- Para copy, chame `design:ux-copy`.

## Dados de exemplo

Proposta com "Lorem ipsum", "John Doe" ou "R$ 0,00" esconde problema de layout. Use dado realista do domínio: nome de exercício longo, carga com casa decimal, lista com 0, 1 e 50 itens.

## Teste final da proposta

Troque o logo por outro. Se a tela servir para qualquer app, ela ainda é genérica. O que é específico deste produto tem que estar visível.
