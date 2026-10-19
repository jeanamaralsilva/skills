# Lojas e pagamento

Consultado em 2026-10-19. Números em `data/fees.csv`, com fonte. Reabra antes de afirmar.

## Contas de loja
- Apple Developer Program: anuidade (linha APPLE-DEV em `data/pricing.csv`).
- Google Play Console: taxa única de registro (PLAY-REG). Não é mensal.

## Comissão da loja sobre venda digital
- **Apple.** Small Business Program: 15% para quem fez até 1 milhão de USD de proceeds no ano anterior ou é novo, com inscrição [APPLE-SBP]. Assinatura: 30% no primeiro ano e 15% depois de 1 ano do mesmo assinante [APPLE-SUB-Y1, APPLE-SUB-Y2]. O número da taxa padrão fora disso não está na página oficial lida: confira no contrato do App Store Connect antes de citar.
- **Google Play.** 15% no primeiro 1 milhão de USD de receita no ano e 30% acima; assinatura 15% [PLAY-1M, PLAY-OVER1M, PLAY-SUB]. Modelo novo em alguns mercados (EEE, Reino Unido e EUA desde 30/06/2026; Austrália e Japão desde 30/09/2026) com taxas diferentes [PLAY-NEW-SUB]. Usuários no Brasil seguem o modelo antigo na data da consulta; confira se o app vende nesses mercados.
- Pergunta-chave: o app vende bem digital (assinatura, crédito, conteúdo) dentro do app? Se sim, a regra da loja define como cobrar; se vende serviço físico ou fora do app, gateway direto vale.

## Gateway de pagamento no Brasil
- **Stripe.** Cartão nacional com percentual mais valor fixo; internacional soma adicional; Pix por convite; boleto com valor fixo; contestação com valor fixo [STRIPE-*].
- **Mercado Pago.** Cartão com taxa que cai quanto maior o prazo de recebimento; Pix e boleto mais baratos [MP-*]. A taxa da conta pode ser outra: peça o simulador da conta.
- **Pix.** O Banco Central proíbe tarifa para pessoa natural no envio; para pessoa jurídica cada banco define [PIX-PF, PIX-PJ].

## Estimar
```bash
python3 scripts/estimate.py --fee PLAY-1M --fee APPLE-SBP --use receita=8000-12000
python3 scripts/estimate.py --fee STRIPE-CARD --use receita=20000 --use transacoes=400
```
Receita da loja em USD, gateway em BRL: totais separados.

## Alavancas
[LOJA-SBP] inscrever no Small Business Program. [PAG-PIX] Pix fora da loja. [PAG-PRAZO] prazo maior no Mercado Pago. Mudar como o app cobra dentro da loja é regra de loja: veja ceo-ship, se instalada, e não prometa economia sem conferir a diretriz da loja.
