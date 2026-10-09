# Regressão de PR e de dependência

"O que este PR quebra?" e "o que o upgrade do SDK quebra?" têm a mesma resposta: o diff diz quais arquivos mudaram, o mapa diz quais telas e eventos esses arquivos alimentam, a matriz diz quais casos rodar. Nada da suíte inteira; só o que o diff alcança, mais o fluxo principal.

## Gatilhos

| Pedido | Modo |
|---|---|
| "testa o PR 42", "revisa o que esse PR pode quebrar" | regressão de PR |
| "o upgrade do Expo quebra o quê", depois de `ceo-deps` aplicar correção que muda dependência nativa ou major | regressão de dependência |
| varredura | só **lista** os PRs abertos e as telas que cada um toca; não roda (custa build) |

## Do diff à matriz

```bash
gh pr list --state open --json number,title,headRefName,files --jq '.[] | "\(.number) \(.title) \(.headRefName) \([.files[].path] | join(","))"'
gh pr diff 42 --name-only                              # ou: git diff --name-only origin/main...origin/<branch>
python scripts/map_flows.py <mobile> --json > runs/map.json
```

Cruze os arquivos do diff com `screens[].file` e com os imports que eles alcançam (hooks, componentes compartilhados, `src/lib/socket.ts`). Regra prática:

| O diff toca | Casos que entram |
|---|---|
| arquivo de tela (`app/**`) | a matriz dessa tela inteira |
| hook ou componente usado por N telas (`grep -rl "from '@/components/X'"`) | feliz + triste de cada tela que importa; duplo toque onde escreve |
| `src/lib/socket*`, `channel`, `*-channel.ts` | os 7 testes de `05-multiusuario-tempo-real.md` |
| `package.json`, lockfile, `app.config.*`, plugin nativo | escada inteira (abaixo) e `varredura-de-abas.yaml` |
| servidor: `*_channel.ex`, contexto chamado por canal | teste de canal com dois clientes (`08`) e os eventos pareados pelo `map_realtime.py` |
| servidor: migration, schema, changeset | contrato: compare o schema do mobile (zod/types) com o changeset; `oasdiff` se houver OpenAPI |
| só texto, estilo, asset | `assertScreenshot` da tela contra a baseline |

Sempre: o fluxo principal (money tour) roda por último como smoke, mesmo que o diff não o toque.

## Escada de verificação (do mais barato ao mais caro)

| Degrau | Comando | Quando parar aqui |
|---|---|---|
| 1 | `npx tsc --noEmit`; `mix compile --warnings-as-errors` | diff só em tipos ou texto e tudo verde |
| 2 | `npm test -- --watchAll=false` (ou `bun test`); `mix test` | diff sem UI nem dependência |
| 3 | testes implementados pela skill: `npx jest src/__tests__/ceo`; `mix test test/ceo` | sempre que existirem |
| 4 | `npx expo export --platform ios` | pega import quebrado sem build |
| 5 | `npx @expo/fingerprint fingerprint:generate` e comparar com o do último build | fingerprint igual: não precisa de build novo, só OTA |
| 6 | `eas build -p ios --profile simulator` (perfil local, ver abaixo) e `eas build:run -p ios --latest` | fingerprint mudou |
| 7 | flows Maestro do que o diff alcança, com vídeo | qualquer mudança de UI ou de canal |
| 8 | `phx_actor` e os testes de tempo real | diff em socket, canal ou presença |

Plano free do EAS: 15 builds iOS por mês. Um PR que não muda nada nativo não gasta build: o JS vai por `expo export` e o `.app` anterior serve.

## Perfil de simulador sem mexer no repo

Se o `eas.json` do projeto não tem perfil com `"ios": {"simulator": true}`, a skill adiciona um perfil `simulator` só durante o build e restaura o arquivo depois (`git stash` do arquivo ou cópia de backup). Em repo read-only o arquivo nunca fica alterado; em repo próprio, propor commitar o perfil é um item do relatório.

```json
"simulator": { "extends": "development", "ios": { "simulator": true }, "developmentClient": true }
```

## Revisão de código junto com a regressão

A regressão responde "quebra?". A revisão responde "está certo?". Com o diff na mão, chame `ceo-cortex` para o patch e `ceo-deps` quando o diff toca dependência (`scripts/expo_check.py`, `lock_audit.py`). O relatório da ceo-testes traz os dois num bloco só: o que quebrou (com vídeo), o que a revisão apontou (arquivo:linha) e o que a dependência trouxe (CVE, duplicata, fora do SDK).

Dois PRs abertos que tocam a mesma tela ou o mesmo canal: diga isso no relatório. É o conflito que ninguém vê até o merge.

## Integração com `ceo-deps`

Depois que a `ceo-deps` aplica uma correção em branch (modo manter ou upgrade) que muda módulo nativo, SDK ou lib central, ela chama a `ceo-testes` em modo regressão de dependência com a lista de pacotes mudados. A ceo-testes sobe a escada até o degrau que a mudança exige e devolve "verificado até o degrau N" para o relatório da ceo-deps. Sem esse passo, a ceo-deps não diz "resolvido".

## Fontes

- `gh pr diff`, `gh pr list --json`: https://cli.github.com/manual/gh_pr_diff ; https://cli.github.com/manual/gh_pr_list
- Expo fingerprint: https://docs.expo.dev/versions/latest/sdk/fingerprint/ ; EAS simulator build: https://docs.expo.dev/build-reference/simulators/
- oasdiff: https://github.com/oasdiff/oasdiff
