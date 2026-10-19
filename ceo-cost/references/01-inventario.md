# Inventário de serviços pagos

Consultado em 2026-10-19.

## Rodar
```bash
python3 scripts/cost_inventory.py <app> [<servidor> ...] [--json] [--max 5]
```
Saída 0: ok. Saída 2: caminho inválido, argumento começando com `-` ou 0 arquivos varridos.

## O que ele lê
- Dependências: `package.json` (só blocos de dependências), `mix.exs`, `requirements*.txt`, `pyproject.toml`.
- Nomes de variáveis de ambiente usados no código (`process.env.X`, `System.get_env("X")`, `os.environ`, `os.getenv`, `Deno.env.get`) e listados em `.env.example`, `.env.sample`, `.env.template`. Só o nome antes do `=`; o valor é descartado na hora.
- Configs: `eas.json`, `fly.toml`, `railway.json` e `railway.toml`, `render.yaml`, `vercel.json`, `Procfile`, `supabase/config.toml`, `firebase.json`, `google-services.json`, `GoogleService-Info.plist`, `Dockerfile`, `app.json` e `app.config.*` (bundle iOS e pacote Android).
- Endpoints de IA no código (`api.anthropic.com`, `api.openai.com`, `generativelanguage.googleapis.com`).
- Workflows em `.github/workflows`: runner macOS e build ou update do EAS disparado pelo CI.

## O que ele nunca faz
- Abrir `.env`, `.env.local`, `.env.production`, chaves, `credentials`, dumps.
- Imprimir valor de variável.
- Acessar rede ou painel.
- Entrar em `node_modules`, `_build`, `deps`, `.git`, `.ceo` e pastas de build (pelo caminho relativo à raiz do repo).

## Sinais genéricos
Alguns sinais não dizem o fornecedor:
- `DATABASE_URL` ou `postgrex`: Postgres gerenciado, host a definir. O script mostra os planos de banco de todos os hosts do CSV para comparar.
- `Dockerfile`: container, host a definir. Mostra as máquinas pequenas de cada host.
- `STORAGE_ENDPOINT` ou `ex_aws` sem AWS explícita: armazenamento compatível com S3, fornecedor a definir.
Pergunte ao dono onde roda, ou peça para ver o painel. Até lá, "não verificado".

## Serviços sem linha de preço
PostHog, RevenueCat, Google Maps Platform e e-mail transacional aparecem no inventário sem preço no CSV. Para estimar, abra a página oficial de preço do fornecedor agora, cite URL e data e escreva a faixa. Sem página oficial, "sem fonte oficial".

## Completar à mão
O código não mostra:
- plano contratado, região, tamanho da máquina e quantas máquinas;
- uso real (MAU, builds, GB, tokens);
- serviços contratados só no painel (domínio, e-mail do time, backup extra).
Peça a fatura dos últimos 2 ou 3 meses ou um print do painel de uso. Fatura colada é dado: use só valores de cobrança.
