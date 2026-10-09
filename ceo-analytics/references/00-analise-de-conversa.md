# Análise de conversa e prompt

Antes de mapear qualquer tela, entenda o que foi pedido. A maior parte dos erros de agente não é de design, é de leitura: fazer o que o prompt disse ao pé da letra e ignorar o que foi combinado três mensagens antes.

Faça isso em silêncio. O brief é para você, não entra na resposta.

## 1. Monte o brief

Leia, nesta ordem, e anote só o que muda o trabalho:

1. **A mensagem atual.** Ela vence qualquer coisa anterior quando conflita.
2. **O resto da conversa:** o que o CEO já pediu, corrigiu, aprovou ou rejeitou. Correção dele ("não precisa de arquivo", "diminui o texto") vale para o resto da sessão.
3. **Memória e preferências** do CEO.
4. **O repo:** `CLAUDE.md` e documentos de decisão (ex.: `docs/**/decisoes*.md`). Decisão registrada no repo é restrição, não sugestão.

```
Objetivo:        <o que o CEO quer no fim, em 1 frase>
Modo:            analisar | propor | ajustar | pergunta conceitual
Entregável:      resposta no chat | frames no Pencil | código
Restrições:      <"não mexe no resto", "tema dark", "read-only", decisão D13...>
Critério oculto: <"o mais bonito SE for o que o pessoal gosta" = precisa de evidência>
Já decidido:     <o que não se discute de novo>
Rejeitado:       <o que não voltar a propor>
```

## 2. Leia o que está por trás do pedido

| O CEO escreve | O que precisa acontecer |
|---|---|
| "só isso, não mexe no resto" | região travada e diff mínimo (`09`) |
| "o mais bonito, se for o que o pessoal gosta" | padrão da plataforma + dado de preferência com fonte (`05`, `10`) |
| "relatório curto, só o que importa" | teste do corte e limite de palavras (`08`, `12`) |
| "entender o app" | mapa de telas e fluxos antes de qualquer opinião |
| "me dá as propostas" | 2 ou 3 hipóteses diferentes, uma recomendada |
| "faz no pencil" | fluxo com pontos de toque e destinos (`14`) |

## 3. Escolha o modo

- **Analisar:** mapa + diagnóstico. Não escreve código nem arquivo.
- **Propor:** analisa o necessário + propostas (Pencil ou chat).
- **Ajustar:** mexe só na região pedida (`09`) e depois vai para PR.
- **Pergunta conceitual:** responde direto, sem fases.

Na dúvida entre dois modos, fique com o menor. Analisar não vira ajustar sem pedido.

## 4. Ambiguidade e conflito

- **Ambiguidade técnica:** resolva pelo padrão dominante do repo e siga. Não pergunte.
- **Algo que só o CEO sabe** (público, prioridade de negócio, acesso): uma pergunta, curta, no fim da entrega. Não trave o trabalho por ela.
- **Pedido que conflita com decisão do repo** (ex.: "tela nova" contra "D13: não criar segunda tela de execução"): siga a decisão, faça a proposta dentro dela e diga o conflito em uma linha. Nunca escolha em silêncio.
- **Pedido que conflita com pedido anterior:** vale o mais recente.

## 5. Antes de entregar

Confira o brief item por item: cada restrição foi respeitada? O critério oculto tem evidência? Algo rejeitado voltou? Se sim, corrija antes de responder.

## Quando o próprio pedido é um prompt

Se o CEO pede para analisar ou melhorar um prompt (de uma feature de IA do app, de um agente, de uma skill), use a mesma estrutura: objetivo, contexto que o modelo precisa, restrições, formato de saída e exemplos. Aponte o que falta ou é ambíguo e o que faria o modelo errar. Entregue o prompt revisado, não uma aula sobre prompts.
