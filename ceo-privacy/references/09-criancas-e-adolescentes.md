# Crianças e adolescentes

Consultado em 2026-10-19. Se menores de 18 usam ou podem usar o app, isso muda o produto, não só o texto. Tudo aqui vai para o advogado; a skill aponta o que o código precisa ter.

## Brasil

**LGPD art. 14** [fonte: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709compilado.htm]
- Sempre no melhor interesse da criança e do adolescente.
- Criança: consentimento específico e destacado de pelo menos um dos pais ou responsável, com esforço razoável para verificar quem consentiu (§§1º e 5º).
- Não condicionar app ou jogo a dados além do estritamente necessário (§4º).
- Informação simples e adequada à idade (§6º).
- A ANPD admite outras bases dos arts. 7º e 11 se o melhor interesse prevalecer (Enunciado CD/ANPD nº 1/2023) [fonte: https://www.in.gov.br/en/web/dou/-/enunciado-cd/anpd-n-1-de-22-de-maio-de-2023-485306934].

**ECA Digital, Lei 15.211/2025**, em vigor desde 17/03/2026 [fonte: https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/L15211.htm]
- Vale para produto de TI direcionado a crianças e adolescentes **ou de acesso provável** por eles (art. 1º).
- Privacidade e proteção no nível mais protetivo por padrão (art. 7º).
- Conteúdo impróprio para menores: verificação de idade confiável, autodeclaração não basta (art. 9º §1º).
- Receber o sinal de idade da loja ou do sistema e ter mecanismo próprio para barrar conteúdo inadequado; dado de verificação de idade só serve para isso (arts. 13 e 14).
- Supervisão parental fácil; padrão no máximo: limitar contato de estranhos, autoplay, notificações e geolocalização (arts. 17 e 18).
- Proibido perfilamento e análise emocional para publicidade dirigida a eles; loot box proibida (arts. 20, 22 e 26).
- Contas de até 16 anos vinculadas à conta de um responsável (art. 24).
- Multa de até 10% do faturamento no Brasil, limitada a R$ 50 milhões por infração (art. 35).
- A ANPD fiscaliza e regulamenta (Decreto 12.622/2025 [fonte: https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/decreto/D12622.htm]; Decreto 12.880/2026 [fonte: https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2026/decreto/D12880.htm]). O decreto diz que o sinal de idade não leva data de nascimento exata nem identidade civil (art. 25).
- Aferição de idade: a ANPD publicou orientações preliminares em 2026; regulamento definitivo não confirmado em 2026-10-19 [fonte: https://www.gov.br/anpd/pt-br/assuntos/noticias/anpd-publica-orientacoes-preliminares-e-cronograma-para-afericao-de-idade-no-ambiente-digital]. Reabra a fonte antes de afirmar.

## Outros países e lojas

| Regra | Fonte |
|---|---|
| GDPR: criança consente sozinha a partir de 16 (o país pode baixar até 13) | art. 8(1), https://publications.europa.eu/resource/celex/32016R0679 |
| COPPA (EUA): menores de 13; consentimento parental verificável antes de coletar; repasse a terceiro com consentimento separado | 16 CFR 312, https://www.ecfr.gov/current/title-16/chapter-I/subchapter-C/part-312 |
| COPPA: emenda de 2025, conformidade obrigatória desde 22/04/2026 | https://www.govinfo.gov/content/pkg/FR-2025-04-22/html/2025-05904.htm |
| Apple Kids Category: sem dado pessoal ou de aparelho para terceiros; analytics e anúncio de terceiros só nas exceções estreitas | diretrizes 1.3 e 5.1.4, https://developer.apple.com/app-store/review/guidelines/ |
| Google Play Families: app para crianças não envia Advertising ID; só SDK de anúncio certificado | https://support.google.com/googleplay/android-developer/answer/9893335 |

## O que conferir no código

- Campo de idade ou data de nascimento no cadastro (`nascimento` no mapa): o app sabe que tem menor?
- SDK de anúncio, Meta, AdMob, Advertising ID: proibidos ou restritos para esse público.
- Localização, chat com desconhecidos, notificações: padrão desligado.
- Conta de menor ligada a responsável; tela de supervisão.
