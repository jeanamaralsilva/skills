# Plano de corte

Consultado em 2026-10-19.

## Para cada corte possível
| Campo | Como preencher |
|---|---|
| Economia por mês | faixa, com a conta mostrada (`estimate.py` antes e depois) |
| Risco para o cliente | nenhum, baixo (lentidão rara), médio (função some ou piora), alto (fora do ar, perda de dado) |
| Esforço | minutos (painel), horas (config), dias (código) |
| Como desfazer | o passo exato; "não tem volta" quando apaga algo |
| Quem decide | o dono para plano, escala, região, exclusão e troca de fornecedor |
| Fonte | id de `data/levers.csv` ou URL oficial |

## Ordem
1. Teto e alerta de gasto onde não há (economia de cauda, risco quase zero, esforço de minutos).
2. Ralos sem risco ao cliente: build e CI no evento certo, runner Linux, cache de build, prompt caching, log de debug em produção.
3. Ajuste de tamanho: máquina e banco com folga medida, auto stop onde a primeira requisição lenta é aceitável.
4. Troca de plano ou de fornecedor: só com 2 a 3 meses de fatura, comparação no `estimate.py` e plano de migração (ceo-deps, se instalada).
5. Nunca corte backup, monitoramento de erro ou segurança para economizar sem o dono decidir sabendo o risco.

Ordene dentro de cada grupo por economia dividida pelo risco. Corte com economia menor que o custo de uma hora do time por mês: mencione, não priorize.

## Executar
Nada de painel, escala, plano, região ou exclusão sem "sim" explícito do dono, uma ação por vez. Antes: print ou export do estado atual. Depois: confirme que o app segue de pé (ceo-mobile-qa ou o teste do time) e anote a data para comparar na próxima fatura.

Mudança no código (cache, gatilho de CI, imagem menor): em branch, com teste, e revisada (ceo-code-review, se instalada).
