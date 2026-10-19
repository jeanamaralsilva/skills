# Preços e faixas

Consultado em 2026-10-19.

## Os CSVs
- `data/pricing.csv`: uma linha por serviço, plano e métrica. `included` é a franquia do plano; `price_low` e `price_high` são o preço por `unit` (faixa quando muda por região, contexto, tamanho ou data anunciada). `base` é mensalidade (`unit=year` divide por 12; `unit=once` fica fora do total mensal). `credit` é crédito do plano que abate a métrica em `unit`.
- `data/fees.csv`: taxas de loja e de pagamento em percentual e valor fixo.
- `data/levers.csv`: alavancas de economia com quando vale, risco e fonte.
Toda linha tem `source` (página oficial) e `checked_on` (data em que foi lida).

## Reconferir antes de afirmar
1. Ache a linha (`scripts/estimate.py --list <serviço>`).
2. Reabra a `source` (WebFetch). Página que carrega por JavaScript: tente o texto bruto ou a doc de cobrança do fornecedor.
3. Confira o número. Mudou: use o novo, cite a data de hoje e diga ao dono que o CSV está desatualizado.
4. Linha com `checked_on` de mais de 30 dias: o `estimate.py` já avisa; nunca repita o número sem reabrir.

## Montar o uso
| Métrica | De onde tirar |
|---|---|
| `mau` | analytics, painel do Supabase ou Firebase Auth, EAS Update (usuários que receberam update) |
| `builds` | histórico do EAS ou do CI no mês |
| `egress_gb`, `storage_gb` | painel do host ou do storage |
| `ci_minutes`, `ci_minutes_macos` | aba de uso do GitHub |
| `input_mtok`, `output_mtok`, `cache_read_mtok`, `cache_write_mtok` | console da API de IA, ou chamadas por usuário x tokens por chamada x MAU |
| `compute_month`, `db_month` | quantas máquinas e bancos ficam ligados o mês todo |
| `receita`, `transacoes` | relatório da loja ou do gateway |

Não sabe: faixa larga (ex.: `mau=500-5000`) e diga que é faixa por falta de dado.

## Ler o resultado
- Total por moeda. USD e BRL só somam com câmbio dado pelo dono, com data.
- Por usuário ativo: o baixo divide o custo baixo pelo MAU alto; o alto divide o custo alto pelo MAU baixo.
- Avisos: preço velho, métrica sem uso informado, taxa única.
- Fica de fora: imposto, IOF e câmbio do cartão, crédito promocional, desconto negociado, plano anual pago adiantado. Diga isso no relatório.

## O que ficou sem fonte oficial em 2026-10-19
- Apple: número da taxa padrão fora do Small Business Program e fora de assinatura (a página oficial lida diz só "taxa padrão").
- GitHub: se a franquia de minutos cobre runner macOS (o CSV trata como fora, pior caso) e preço mensal dos planos.
- Firebase: preço por GB de Cloud Storage e de armazenamento do Firestore por mês; leitura e escrita em São Paulo.
- Sentry: preço do erro excedente.
- Render: disco do Postgres por GB.
- Fly.io: preço de máquina fora de iad e ewr.
- Heroku: horas incluídas no Eco.
- Mercado Pago: taxa por perfil do vendedor (a página pública mostra a padrão; a conta pode ter outra).
- Pix para pessoa jurídica: cada banco define a tarifa.
- PostHog, RevenueCat, Google Maps, e-mail transacional: não pesquisados.
Para qualquer um desses, abra a página oficial na hora. Sem ela, não dê número.
