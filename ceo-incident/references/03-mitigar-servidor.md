# Mitigar no servidor

Consultado em 2026-10-19. Comandos com fonte em `data/mitigacao.csv` (ids SV). Coluna `le_ou_muda`: `le` pode rodar já; `muda` só com confirmação explícita (`references/02-mitigar-primeiro.md`).

Nenhum comando abaixo foi rodado contra produção pela skill. Confira a versão da CLI instalada (`<cli> --help`) antes de usar, e descubra o nome do app ou serviço por comando de leitura.

## Fly.io

- Ver: `fly releases --app <app> --image`, `fly status --app <app>`, `fly logs --app <app> --no-tail`.
- Voltar: não há comando de rollback; o caminho documentado é publicar a imagem anterior: `fly deploy --image registry.fly.io/<app>:deployment-<ID>`.
- Não desfaz: migração, secrets, `fly.toml`. A imagem antiga pode não existir mais [fonte: https://docs.fly.io/blueprints/rollback-guide].

## Railway

- Ver: `railway logs --since 1h --filter @level:error` [fonte: https://docs.railway.com/cli/logs].
- Voltar: painel, Service, Deployments, menu do deployment anterior, Rollback. Restaura imagem e variáveis; deploys fora da retenção do plano não oferecem a opção [fonte: https://docs.railway.com/deployments/deployment-actions].
- `railway redeploy` refaz o atual; não é rollback [fonte: https://docs.railway.com/cli/redeploy].
- Sem fonte oficial verificada para rollback pela CLI: use o painel.

## Render

- Voltar: Deploys, um deploy com sucesso, Rollback. Desliga o auto-deploy (religue depois); não reverte disco nem domínios; usa as variáveis do deploy de destino [fonte: https://render.com/docs/rollbacks].
- Logs: página Logs do serviço; retenção depende do plano [fonte: https://render.com/docs/logging].

## Vercel

- Voltar: `vercel rollback <deployment-id|url>`; no Hobby só ao deploy imediatamente anterior [fonte: https://vercel.com/docs/cli/rollback].
- Depois do rollback, novos pushes não entram em produção até `vercel promote` [fonte: https://vercel.com/docs/cli/promote; https://vercel.com/docs/instant-rollback].
- Logs: `vercel logs --environment production --query 'level:error' --since 1h` [fonte: https://vercel.com/docs/cli/logs].

## Heroku

- Ver: `heroku releases`, `heroku logs --tail` [fontes: https://devcenter.heroku.com/articles/releases e https://devcenter.heroku.com/articles/logging].
- Voltar: `heroku rollback vNN`. Não reverte banco nem add-ons; config vars voltam junto [fonte: https://devcenter.heroku.com/articles/releases].
- Parar tráfego: `heroku maintenance:on`; workers e agendador seguem rodando [fonte: https://devcenter.heroku.com/articles/maintenance-mode].

## Docker próprio, VPS, outro

Sem doc única. Volte para a imagem ou tag anterior pelo mesmo caminho do deploy. Se não sabe qual era, `scripts/timeline.py --repo <server>` mostra commits e tags da janela.

## Por stack (inspeção)

- **Elixir/Phoenix (release):** `bin/<app> remote` abre shell no sistema rodando; `rpc` executa no nó vivo [fonte: https://mix.hexdocs.pm/Mix.Tasks.Release.html]. No Fly: `fly ssh console --pty -C "/app/bin/<app> remote"` [fonte: https://docs.fly.io/elixir/the-basics/iex-into-running-app]. Toda expressão roda em produção: proponha, mostre e espere confirmação, mesmo para leitura.
- **Rails:** nível de log em `config.log_level`; padrão `:info` em produção [fonte: https://guides.rubyonrails.org/debugging_rails_applications.html].
- **Node:** sem doc oficial única de inspeção em produção; use os logs da plataforma.
