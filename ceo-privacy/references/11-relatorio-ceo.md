# Relatório CEO

Curto, de dono técnico para dono do negócio. Modelo: `assets/report-template.md`.

## Estrutura

1. **Veredito:** 1 linha. "Risco alto", "risco médio" ou "em ordem no que dá para ver", e por quê.
2. **O que o app coleta:** 3 a 6 linhas, por tipo de dado, com para quem vai (servidor, SDK). Sensível marcado.
3. **Riscos** (P1 e P2): até 7, uma linha cada: `- **P1** <risco> → <correção> \`arquivo:linha\` [fonte: url]`.
4. **Corrigido agora:** só se o usuário pediu correção. Arquivo e teste que prova.
5. **Lojas:** o que muda no App Privacy e no Data safety, se algo mudou.
6. **Precisa de advogado:** base legal, texto da política e dos termos, comunicação de incidente, transferência internacional, menores. Uma linha cada, só o que se aplica.
7. **Decisão sua:** o que só o dono decide (ex.: tirar um SDK de anúncio, prazo de retenção, contratar encarregado).
8. **Não verificado:** painel, banco ou fornecedor que você não viu.

## Severidade

| Nível | Critério |
|---|---|
| P1 | dado pessoal ou credencial exposto ou indo para terceiro sem controle; obrigação de loja ou de lei descumprida que pode tirar o app do ar ou gerar sanção (sem exclusão de conta, token sem criptografia, CPF em log de terceiro, rótulo da loja que contradiz o código) |
| P2 | risco real, mas contido (dado pessoal em log do próprio servidor, falta de link da política, retenção sem prazo, dado literal no código) |
| P3 | higiene (campo sem `redact`, texto de permissão vago, inventário desatualizado) |

## Limites

- Até 350 palavras. Sem metodologia, sem lista de comandos rodados.
- Regra, prazo e multa sempre com `[fonte: url]`. Se a consulta tiver mais de 3 meses, reabra a fonte antes de afirmar.
- Nunca valor de dado pessoal ou segredo; só tipo e `arquivo:linha`.
- Sem juridiquês. Sem "você está em conformidade": a skill não dá parecer jurídico.
- Erro e risco de segurança (credencial no repo, dado exposto) vão completos.
