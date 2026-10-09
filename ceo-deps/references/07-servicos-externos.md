# Serviços externos

Num SaaS, parte das dependências não é pacote: é serviço (pagamento, e-mail, auth, push, storage, SMS). Se ele cai e o app não está preparado, o app cai junto.

## Inventário

Ache os serviços pelo código e pela config, não pela memória:
- Elixir: `config/runtime.exs` (chaves e URLs), módulos que usam `Req`, `Swoosh`, `ExAws`, `Assent`.
- Mobile: `app.config.ts` (plugins de Firebase, Sentry...), `src/api/`, variáveis `EXPO_PUBLIC_*`.

Para cada um: o que faz, onde é chamado, o que acontece se cair.

## O que checar em cada chamada

| Check | Bom | Ruim |
|---|---|---|
| Timeout | explícito e ligado à latência real | padrão da lib (Req: 15s de receive; fetch do Node: 300s) ou nenhum |
| Retry | só em erro transitório e operação idempotente; backoff exponencial com jitter | retry em POST sem chave de idempotência; retry em várias camadas (5 camadas x 3 tentativas = 243x de carga) |
| Circuit breaker | serviço crítico atrás de breaker (Elixir: `fuse`) | cada request espera o timeout inteiro enquanto o serviço está fora |
| Trabalho fora do request | e-mail, webhook e push em job (Oban) | envio síncrono que derruba o request quando o provedor demora |
| Fallback | degradação clara (fila, cache, mensagem ao usuário) | erro genérico ou tela vazia |
| Isolamento | cliente do serviço num módulo só | SDK chamado de qualquer lugar (lock-in) |

Req: o padrão `retry: :safe_transient` só repete GET/HEAD; `:transient` repete POST também, então precisa de idempotência. Swoosh: o cliente padrão é o Hackney (por isso a dependência existe); `Swoosh.ApiClient.Req` e Finch são alternativas.

## SLA

Regra do "nove extra" (ACM Queue): cada dependência crítica precisa de um nove a mais de disponibilidade que o serviço que depende dela. Sem isso, mitigue com fila, cache ou degradação. Não invente o SLA de um fornecedor: cite a página dele ou escreva "SLA não verificado".

## Lock-in

Pergunte só quando importa: o que custaria trocar o provedor? Se o SDK está espalhado (`references/06-arquitetura-e-acoplamento.md`), o custo é alto, e isso entra no relatório como risco, não como tarefa.
