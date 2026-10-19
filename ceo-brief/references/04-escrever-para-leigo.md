# Escrever para leigo

Regras com fonte: `data/escrita.csv`. O leitor é inteligente e ocupado. Linguagem simples não é tratar como bobo [fonte: https://www.nngroup.com/articles/plain-language-experts/].

## Ordem

1. **Conclusão primeiro.** A primeira frase diz se a semana foi boa, ruim ou mista e por quê. Quem parar ali já entendeu [fonte: https://www.nngroup.com/articles/inverted-pyramid/].
2. **Impacto, próximos passos, detalhe.** É a ordem BLIND do manual de escrita da Força Aérea dos EUA: conclusão, impacto, próximos passos, detalhes [fonte: https://afrotc.asu.edu/sites/default/files/afh33-337.pdf].
3. **Pedido ou decisão perto do topo**, não no fim [fonte: https://web.archive.org/web/20201202112659/https://www.aaronkharris.com/investor-updates].

## Frase

- Até 25 palavras; passou, divida [fonte: https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-language/].
- Uma ideia por frase, voz ativa: "o time corrigiu", não "foi corrigido" [fonte: https://digital.gov/guides/plain-language/writing].
- Números em dígitos: "3 correções" [fonte: https://www.nngroup.com/articles/web-writing-show-numbers-as-numerals/]. Não abrevie mil como K [fonte: https://learn.microsoft.com/en-us/style-guide/numbers].
- Sem travessão. Use ponto, vírgula ou dois-pontos.

## Jargão

A Lei 15.263/2025 (Política Nacional de Linguagem Simples, para a administração pública) pede sinônimo ou explicação para termo técnico e nome completo antes da sigla [fonte: https://www2.camara.leg.br/legin/fed/lei/2025/lei-15263-14-novembro-2025-798293-publicacaooriginal-177011-pl.html]. Vale como boa prática aqui:

| Em vez de | Escreva |
|---|---|
| PR mergeado | mudança aprovada e pronta |
| deploy em produção | no ar para os clientes |
| build, release | versão do app |
| CI quebrado | a verificação automática do código está reprovando |
| hotfix | correção urgente |
| rollback, revert | voltamos para a versão anterior |
| bug | erro, problema |
| refactor | reorganização interna, sem mudança para o cliente |
| endpoint, API | ligação entre o app e o servidor |
| staging | ambiente de teste |
| breaking change | mudança que exige atualizar o app antes |
| OTA | atualização pelo ar, sem passar pela loja |
| incidente SEV-1 | parada grave que atinge clientes |

`scripts/lint_brief.py` acusa os termos da coluna da esquerda.

## Citar PR ou issue

Diga em 1 linha do que se trata e ponha o link ou número ao lado [fonte: https://handbook.gitlab.com/handbook/communication/]. O brief resume; a fonte é o PR (mesma fonte).

## Forma

- Lista para itens, tabela só para comparar frentes [fonte: https://digital.gov/guides/plain-language/design].
- Títulos que começam pela palavra que informa: "Risco: pagamento no Android" [fonte: https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content/].
- Corte tudo que não ajuda a decidir [fonte: https://learn.microsoft.com/en-us/style-guide/top-10-tips-style-voice].
