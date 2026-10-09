# Um chat, dois repos, e a entrega até a main

Quem trabalha num app com servidor costuma abrir o chat num repo só (em geral o servidor) e falar do produto inteiro. A skill não pode responder "isso é do mobile". O bug do cliente atravessa os dois repos; a correção também.

## Achar o outro repo

Ordem:
1. `repos[]` em `.ceo/config.md` (do repo aberto ou de `~/.ceo/profile.md`).
2. Pastas irmãs com o mesmo prefixo: `../<nome>-mobile`, `../<nome>-server`, `../<nome>-web`, `../<nome>-app`, `../<nome>-api` (`ls ..`).
3. Pergunta, uma vez, e grava a resposta na config.

Sem o outro repo acessível, o relatório diz "lado mobile não analisado" e o que precisaria ser olhado lá (nome do arquivo provável, evento, endpoint). Nunca "o app deve estar certo".

Cada repo pode ter seu próprio estado git (branch, atraso). Antes de ler código, `git --no-optional-locks fetch` e leia a referência certa: o que o cliente usa é `origin/main` (ou a tag da versão), não a branch local que estiver aberta. `git show origin/main:<arquivo>` evita analisar código velho.

## A regra dos dois lados

Toda causa encontrada responde a três perguntas antes de virar patch:

| Pergunta | Onde olhar |
|---|---|
| Quem decide (fonte da verdade)? | servidor: status, saldo, permissão. App: só apresenta. Se o app decide algo que o servidor também decide, há dois oráculos e vai divergir |
| O outro lado concorda? | contrato: campo do JSON (`*_json.ex` ↔ tipo TS/zod), evento do canal (`map_realtime.py`), regra de negócio duplicada (ex.: janela de confirmação no app e `confirmation_window_hours` no servidor) |
| Corrigir onde? | servidor quando é regra; app quando é exibição; **os dois** quando um sem o outro deixa app antigo quebrado (version skew) |

Um bug com patch só no servidor e o app ainda bloqueando a ação não está corrigido. O relatório traz os dois patches ou explica por que um basta.

## Entrega: da branch à main

Vale quando o repo é seu (`read_only: false`). Em read-only, para no patch e no teste.

1. **Branch** por bug, nos repos que a correção toca: `fix/<slug>` com o mesmo nome nos dois.
2. **Teste implementado** junto do patch, no lugar certo da suíte (não em `test/ceo/`): o teste que reproduz falha antes e passa depois. Testes que dependem de decisão pendente ficam em `test/ceo/` fora do git, com o motivo.
3. **Revisão contra tudo**, nesta ordem, antes de abrir PR:
   - suíte inteira do repo (`mix test`, `npm test`), não só o arquivo novo;
   - `ceo-cortex` no diff (patch mínimo, sem corrigir sintoma, convenções do repo, `CLAUDE.md`);
   - PRs abertos que tocam os mesmos arquivos (`gh pr list --json files`): conflito vira item do relatório;
   - `ceo-deps` se o diff tocou dependência;
   - contrato com o outro repo (tabela acima).
4. **PR** por repo, com: o relato do cliente em uma linha, o teste, o vídeo da reprodução quando houver, e a ordem de deploy ("server antes do app" quando o app novo depende do server novo; "app antes" quando o server novo quebraria app antigo). Pela skill de PR da config, senão `gh pr create`.
5. **CI verde** (`gh pr checks --watch`). CI que não existe é item do relatório, não desculpa.
6. **Merge na main** só com (3) e (5) feitos e com a decisão do CEO quando houve uma. Ordem: o repo que o outro depende primeiro. `gh pr merge --squash --delete-branch`.
7. **Relatório** diz o que foi mergeado, em qual repo, o que está em PR esperando, e o que ficou pendente de decisão.

O que nunca faz sozinha: force push, merge com CI vermelho, merge de mudança que precisa de decisão de produto ainda aberta, deploy.

## Fontes

- Version skew entre app e servidor: https://docs.expo.dev/eas-update/runtime-versions/ (por que app antigo continua em produção)
- `gh pr list --json`, `gh pr checks`, `gh pr merge`: https://cli.github.com/manual/gh_pr
- Contrato por schema: https://github.com/oasdiff/oasdiff
