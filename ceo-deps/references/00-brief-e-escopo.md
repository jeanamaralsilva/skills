# Brief e escopo

Antes de rodar qualquer comando, leia a config (`.ceo/config.md` na raiz do repo; depois `~/.ceo/profile.md`; modelo em `assets/ceo-config.example.md`) e monte o brief em silêncio. Ele não entra na resposta. Sem config, use os padrões abaixo e pergunte só o que mudaria a ação (ex.: "posso criar branch neste repo?").

```
Repos:        <caminho de cada um e o papel: mobile, server, web, lib>
Modo:         auditar | manter | upgrade
Read-only?:   sim (só relatório) | não (pode criar branch)
Licença:      saas | mobile (loja) | ambos
Gatilho:      <o que o CEO colou ou pediu: saída do expo-doctor, CVE, erro de build...>
Restrições:   <ex.: "não buildo local", "não mexe no SDK agora">
```

## Modos

| Modo | Quando | O que entrega |
|---|---|---|
| Auditar | "analisa as dependências", "como estão as libs" | Relatório com achados e o que fazer. Não toca em nada |
| Manter | "resolve o expo-doctor", "deixa funcionando", saída de erro colada | Correções seguras aplicadas e verificadas, relatório curto |
| Upgrade | "sobe para o SDK 58", "atualiza o Phoenix" | Plano, upgrade em branch, verificação completa, pendências |

Na dúvida, o modo menor. Auditar não vira manter sem pedido.

## Read-only

Repo listado como `read-only` na config, ou que o CEO disse não ser dele, é analisado só para relatório. Lá:
- Nenhuma escrita: nem branch, nem lockfile, nem `node_modules`.
- `git` sempre com `--no-optional-locks` (um `git status` comum grava `.git/index.lock` e pode deixar trava).
- Se o CEO pedir correção num repo read-only, entregue o patch e os comandos para quem é dono do repo aplicar.

## Gatilho colado

Quando o CEO cola a saída de uma ferramenta (expo-doctor, `mix deps.get`, build do EAS), ela é o ponto de partida: cada linha da saída vira um item do relatório, com causa e correção. Confirme a causa no repo antes de propor (ex.: duplicata de `@expo/ui` aninhada em `expo-widgets`: rode `npm why @expo/ui` ou leia o lockfile).

## Multi-repo

Com mais de um repo, a pergunta que só a visão conjunta responde é: **o contrato entre eles está em dia?** (`references/06-arquitetura-e-acoplamento.md`, seção multi-repo).
