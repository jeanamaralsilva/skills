# Brief e escopo

Consultado em 2026-10-19.

## O que o dono quer saber
1. Quanto sai por mês hoje, em faixa.
2. Quanto custa cada usuário ativo no mês.
3. Para onde vai o dinheiro (top 3).
4. O que dá para cortar sem o cliente sentir, e quanto isso economiza.
5. O que muda se o app crescer 10 vezes.

## Modos
| Modo | Pedido típico | Passos |
|---|---|---|
| raio-x | "quanto custa manter o app no ar" | inventário, estimativa, relatório |
| pico | "a conta da AWS/Vercel subiu" | fatura ou painel, compare com o mês anterior, ralos; se ainda sobe, ceo-incident |
| corte | "preciso cortar custo" | inventário, ralos, plano de corte |
| IA | "quanto gasto com tokens" | `05-ia.md`, estimativa por chamada e por usuário |
| lojas e pagamento | "quanto a Apple e o Google levam" | `04-lojas-e-pagamento.md` |
| escala | "e se tivermos 10 mil usuários" | estimativa com faixa de MAU maior, ponto onde muda de plano |

## Perguntas que mudam a resposta
Pergunte só se não estiver no `.ceo/config.md` nem no código:
- Usuários ativos por mês (MAU). Sem número, use faixa e diga.
- Planos contratados hoje (o código não mostra plano).
- Região dos servidores e dos usuários (egress e máquina mudam de preço por região).
- Se há receita pela loja ou por pagamento direto, e quanto.
- Câmbio que o dono quer usar, se ele quer tudo em reais.

## Fora do escopo
- Trocar biblioteca ou SDK: `ceo-deps`.
- Queda em produção: `ceo-incident`.
- Imposto, nota fiscal, contabilidade: diga que é com o contador.
- Negociar contrato com fornecedor: a skill prepara números, o dono negocia.
