# Coleta

```bash
python3 scripts/collect.py <repo> --since <AAAA-MM-DD|7d|2w|tag> [--until AAAA-MM-DD] [--ref origin/main] [--no-gh] [--limit 100]
```

Só leitura. Sem `shell=True`, cada comando com timeout de 30 s. Sem rede além do `gh`.

## De onde vem cada campo

| Campo | Comando | Fonte |
|---|---|---|
| `git.items`, `by_type`, `areas` | `git --no-optional-locks log --first-parent <ref> --since --until` | https://git-scm.com/docs/git-log |
| `git.ref` | `origin/HEAD`, senão `origin/main`, `origin/master`, `main`, `master` | https://git-scm.com/docs/git-symbolic-ref |
| `git.last_fetch` | data do arquivo `FETCH_HEAD` | https://git-scm.com/docs/git-fetch |
| `git.items[].type` | prefixo Conventional Commits (`feat`, `fix`, `!` = quebra compatibilidade) | https://www.conventionalcommits.org/en/v1.0.0/ |
| `github.prs_merged` | `gh pr list --state merged --search "merged:>=AAAA-MM-DD" --json ...` | https://cli.github.com/manual/gh_pr_list e https://docs.github.com/en/search-github/searching-on-github/searching-issues-and-pull-requests |
| `github.prs_open` | `gh pr list --state open --json ...,statusCheckRollup,reviewDecision` | https://cli.github.com/manual/gh_pr_list |
| `github.issues` | `gh issue list --state all --search "updated:>=AAAA-MM-DD"` | https://cli.github.com/manual/gh_issue_list |
| `github.ci` | `gh run list --created ">=AAAA-MM-DD"` | https://cli.github.com/manual/gh_run_list e https://docs.github.com/en/rest/actions/workflow-runs |
| `github.releases` | `gh release list --json tagName,publishedAt,...` | https://cli.github.com/manual/gh_release_list |
| `github.deployments` | `gh api repos/{owner}/{repo}/deployments` e `.../deployments/<id>/statuses` | https://docs.github.com/en/rest/deployments/deployments e https://docs.github.com/en/rest/deployments/statuses |
| `github.milestones` | `gh api repos/{owner}/{repo}/milestones?state=open` | https://docs.github.com/en/rest/issues/milestones |

`{owner}` e `{repo}` são preenchidos pelo próprio `gh api` a partir do repo atual [fonte: https://cli.github.com/manual/gh_api].

## Por que a base e não o branch aberto

O que conta como pronto é o que está no ramo principal. O branch aberto na máquina pode ser trabalho em andamento. O coletor usa `origin/HEAD` e avisa quando o branch atual é outro.

## Leia os avisos

| Aviso | O que fazer |
|---|---|
| clone local desatualizado | o GitHub tem PR mergeado que a base local não tem. Use os dados do GitHub para "o que entrou"; não rode fetch em repo que não é seu sem pedir |
| sem registro de git fetch | o histórico local pode estar velho; diga isso se o brief depende só do git |
| atingiu --limit | número é mínimo ("mais de 100"); aumente `--limit` |
| seção `nao_verificado` | diga o motivo em 1 linha no brief (ex.: "CI não verificado: gh sem login") |

## O que o coletor não vê

- Loja de app (versão publicada, revisão, nota, crash) e atualização pelo ar.
- Deploy feito fora do GitHub (painel do provedor, script local) quando o provedor não grava deployment no GitHub.
- Monitoramento de erro, uptime, métricas de produto e pagamentos.
- Tempo da mudança até produção (lead time): o coletor não calcula.
- GitLab, Bitbucket e outros: só a parte git funciona; o resto vira `nao_verificado`.
- Corpo de PR, issue e comentário: não é coletado de propósito (ver `references/09-seguranca.md`). Para explicar um PR, leia só aquele PR.

Para cada item fora, pergunte ao dono ou chame a skill certa (`references/10-integracoes.md`).
