# Execução segura (modo manter e upgrade)

O CEO quer que as coisas continuem funcionando. Você decide e aplica o que é seguro, prova com verificação e só devolve para ele o que tem trade-off real.

## Nunca em repo read-only

Repo read-only (config ou pedido do CEO): só relatório e patch sugerido. Leia `references/00-brief-e-escopo.md`.

## O que aplicar sozinho

Sempre numa branch nova (`deps/<data>-<assunto>`), um assunto por commit:

| Correção | Comando |
|---|---|
| Alinhar pacotes ao SDK do Expo | `npx expo install --fix` |
| Patch de SDK com bug conhecido (ex.: Hermes) | `npx expo install expo@^57.0.9 --fix` |
| Remover lockfile do gerenciador que não é usado | apagar o lockfile extra, reinstalar com o gerenciador oficial |
| Deduplicar | `npm dedupe` / `pnpm dedupe` / `yarn dedupe` |
| Patch e minor dentro do range | `npm update <pkg>`; `mix deps.update <pkg>` |
| CVE com versão corrigida dentro do mesmo major | upgrade dirigido da lib |
| Lock com sobra | `mix deps.unlock --unused` |
| Fixar toolchain | `.tool-versions` / `.nvmrc` com a versão que o CI já usa |
| Dep git por tag | trocar `tag:` por `ref:` com o SHA atual da tag |

## O que vira decisão do CEO

- Major de lib central, troca de lib, upgrade de SDK do Expo ou de Phoenix/LiveView.
- Remover dependência "sem uso" que você não confirmou com knip/grep e build.
- Licença deny.
- Mudança que exige ordem de deploy entre server e mobile.

Formato: uma linha com a decisão, o custo e a sua recomendação.

## Regras

- **Diff mínimo:** lockfile e manifest mudam; código só se a API da lib mudou.
- **Override é curativo:** se precisar, comente no PR por que e quando sai.
- **Sem `--force`, sem `--legacy-peer-deps` como solução.**
- **Verifique antes de dizer pronto** (`references/10-verificacao-sem-build-local.md`). Se o degrau de build não pôde rodar, o relatório diz "não verificado em build".
- **PR:** pela skill de PR da config (`fluxo.pr_skill`), se houver; senão `gh pr create` com os checks do CI passando e a evidência no corpo.
- **Revisão do código tocado:** se mexeu em código (API nova de lib), passe por `ceo-cortex`.
