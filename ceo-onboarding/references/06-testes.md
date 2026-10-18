# Testes

## Jest (lógica, sem simulador)

Teste comportamento do `TipProvider` e das regras, com o storage mockado:

- 1 automática por sessão: segundo `requestTip` automático na mesma sessão não mostra.
- Pedido do usuário (checklist, "Rever dicas") mostra mesmo depois da automática.
- Dispensada não volta; `done` não volta; reset volta tudo.
- Status só avança (cache `dismissed` + servidor `seen` = `dismissed`).
- Sem cache e sem servidor: não mostra.
- Troca de papel usa outra chave; logout limpa.
- Alvo com medida zero ou fora da tela: não mostra.
- `EmptyState`: loading, erro e vazio são estados diferentes.

Servidor: idempotência do endpoint (mesmo POST duas vezes), status que não volta, `tip_id` desconhecido recusado, outro usuário não grava, backfill marca só quem cumpre a condição.

## Simulador (iOS e Android)

Use `ceo-mobile-qa` para a rodada com vídeo. Matriz mínima:

| Caso | Esperado |
|---|---|
| Conta nova, primeira vez na tela-alvo | Dica aparece depois do carregamento, uma vez |
| Abrir o app | Nenhuma dica na abertura |
| Tocar no alvo | Ação real acontece, dica some, conta como feita |
| "Entendi" / toque fora / voltar do Android | Fecha; não volta |
| "Pular dicas" | Nenhuma dica automática depois |
| "Rever dicas" em Perfil | Dicas voltam |
| Segunda tela-alvo na mesma sessão | Não mostra (limite de 1) |
| Reinstalar e logar | Não repete o que já viu (servidor) |
| Outro aparelho | Idem |
| Trocar de papel | Estado do outro papel, sem misturar |
| Conta veterana com dados | Nada de "primeiro X"; checklist já completo ou ausente |
| Sem rede no primeiro acesso | Sem dica; nada quebra |
| VoiceOver / TalkBack | Anúncio ao abrir, foco no texto, botões com rótulo, resto do app oculto, "Ir para" funciona |
| Reduzir Movimento | Sem escala, só fade ou nada |
| Fonte grande (maior acessível) | Balão quebra linha, nada cortado, continua dentro da área segura |
| Rotação e teclado aberto | Recorte segue o alvo ou a dica fecha |
| Teclado aberto em sheet com rodapé fixo: focar o último campo, avançar o guia, fechar o teclado | Balão nunca cobre campo nem botão; o do rodapé fica acima do botão e o formulário rola até o fim |
| Conta nova sem o pré-requisito (ex.: sem aluno) abrindo cada guia | Guia travado diz o que falta; nenhum guia "não faz nada" |
| Android edge-to-edge | Recorte alinhado com o alvo (sem desvio da status bar) |
| Alvo dentro de lista longa | Rola até o alvo antes de mostrar |
| Tema escuro | Contraste do texto 4,5:1 |

Dica de setup: um botão de debug (só em dev) que zera o estado local e chama o reset no servidor, para repetir a primeira vez sem criar conta nova.
