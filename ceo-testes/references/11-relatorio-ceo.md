# Relatório CEO

O CEO quer saber: o app está pronto? o que quebrou? o que você já resolveu? o que só ele decide? Nessa ordem, no chat, sem narrar o processo.

## Estrutura

```
**Veredito:** <uma frase: pronto / não pronto por causa de X / fluxo principal ok, N bugs>

**Bugs** (do pior para o menor)
- **P0** <o que acontece para o usuário> [repro: <passos em 1 linha ou flow.yaml>] [video: runs/x.mov 00:12] `arquivo:linha` → <correção em 1 linha>
- **P1** ...
- **P2** ...

**Testado e ok:** <fluxos e caminhos que passaram, em 1 ou 2 linhas; sem tabela>
**Não testado:** <o que ficou fora e por quê: sem credencial, só no aparelho, sem tempo>
**Pendente do CEO:** <só decisões: "corrigir no servidor ou no app?", "aceitar duplicata até a próxima release?">
```

Seções vazias não aparecem. Se há 1 bug, o relatório tem 5 linhas.

## Prioridade

| | Critério | Exemplo |
|---|---|---|
| **P0** | perde dado, cobra errado, crash no fluxo principal, outro usuário vê o que não devia, loop sem saída | resposta enviada 2x conta 2 pontos; app fecha ao abrir a aula |
| **P1** | fluxo principal degradado, dado velho até refresh, estado quebrado após background, erro sem mensagem | lista não atualiza quando o outro envia; spinner infinito offline |
| **P2** | fluxo secundário, layout quebrado em fonte grande, animação travando, texto cortado | sheet não fecha com swipe; botão sob o teclado no SE |
| **P3** | cosmético, inconsistência, sugestão | ícone desalinhado; toast fica 1 s a mais |

Segurança (token aceito depois de revogado, autorização por objeto falha) é P0 sempre, com detalhes completos, mesmo que estoure o tamanho.

## Regras de evidência

- Cada bug tem **como reproduzir** (passos ou nome do flow), **onde** (`arquivo:linha` da causa provável ou `[tela: X]`) e **prova** (`[video: ...]`, `[print: ...]`, `[cmd: ...]` ou log). Sem os três, é observação, não bug.
- Número só com etiqueta: `[medido]` (cronômetro, trace, contagem), `[estimado]`, `[fonte: url]`. "Lento" vira "2,8 s do toque à lista [medido]".
- "Não reproduzido" é resultado: diga o que tentou (3 hipóteses) e o que falta para tentar de novo.
- Nunca "parece funcionar". Ou passou no oráculo ou não foi testado.
- Vídeo da reprodução: até 15 s, cortado com `ffmpeg -ss -to`. Anexo, não inline.

## Tamanho

| Modo | Limite |
|---|---|
| Regressão de uma ação, caça-bug de 1 bug | 150 palavras |
| Caça-bug com vídeo, multiusuário | 300 |
| Varredura ou estresse completo | 450 (mais a lista de "não testado") |

`python scripts/lint_report.py - < relatorio.md --max-words 300` antes de entregar. Ele acusa travessão, jargão, número sem etiqueta, bug sem evidência e excesso.

## O que não entra

- Lista de arquivos lidos, comandos rodados, ferramentas instaladas.
- O mapa inteiro de telas (fica no brief; vai como anexo se o CEO pedir).
- Explicação de como o Phoenix funciona. A causa em uma linha basta: "o `push` sem conexão vai para o buffer e é reenviado ao reconectar; o servidor não é idempotente".
- Pedido de desculpa, "infelizmente", "vale ressaltar".

## Exemplo (caça-bug, 2 bugs)

```
**Veredito:** fluxo de responder funciona; 2 bugs reproduzidos, 1 corrigido em branch.

**Bugs**
- **P0** Resposta enviada 2x com toque duplo: 2 registros e 2 pontos [repro: assets/maestro/duplo-toque.yaml, BUTTON="Enviar"] [video: runs/dup.mov 00:04] `src/features/answer/use-send.ts:31` → desabilitar enquanto `isPending`; no servidor, unique (user, question) `lib/app/answers.ex:40`. Branch `fix/double-send` com os dois testes passando.
- **P1** Lista do condutor não mostra resposta nova até pull-to-refresh [repro: phx_actor push send_answer com a lista aberta] `src/screens/room/answers.tsx:58` → ouvir `answer_received` e invalidar `['answers', roomId]` (hoje invalida `['answers']` com id errado).

**Testado e ok:** login dos 2 papéis, entrar na sala, deep link frio e quente, background 10 min, fonte grande nas 3 abas.
**Não testado:** push com app fechado (só no aparelho), modo avião (só no aparelho).
**Pendente do CEO:** o unique no servidor rejeita a 2ª resposta com erro ou devolve a 1ª como sucesso?
```

Passa no lint; 171 palavras.
