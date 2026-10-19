# Testes antes da loja: TestFlight e trilhas do Play

Consultado em 2026-10-19.

## Ordem que funciona

1. Smoke test do build de produção no aparelho ou simulador (com a skill `ceo-mobile-qa`, se instalada: fluxo principal, login, compra, push).
2. Testers internos (time).
3. Testers externos ou teste fechado (clientes amigos).
4. Produção com lançamento gradual (`references/07-lancamento-gradual-e-rollback.md`).

## TestFlight

- Build vale 90 dias.
- Até 100 testers internos (usuários do App Store Connect) e até 10.000 externos.
- Externos: o primeiro build de cada versão passa por revisão beta.

Fonte: https://developer.apple.com/help/app-store-connect/test-a-beta-version/testflight-overview/

## Trilhas do Play

| Trilha | Para quê | Fonte |
|---|---|---|
| Teste interno | até 100 testers, disponível na hora, inclusive no primeiro upload | https://support.google.com/googleplay/android-developer/answer/9845334 |
| Teste fechado | lista de testers; obrigatório antes da produção para conta pessoal criada depois de 13/11/2023: 12 testers inscritos por 14 dias seguidos | https://support.google.com/googleplay/android-developer/answer/14151465 |
| Teste aberto | qualquer pessoa entra pela loja | https://support.google.com/googleplay/android-developer/answer/9845334 |
| Produção | todos, de preferência com lançamento gradual | https://support.google.com/googleplay/android-developer/answer/6346149 |

O `eas submit` escolhe a trilha por `submit.<perfil>.android.track` (production, beta, alpha, internal) [fonte: https://docs.expo.dev/eas/json/].

## Conta pessoal nova

Se `conta_play: pessoal_nova` (ou a pessoa não sabe), confirme no Play Console antes de prometer data. O relógio dos 14 dias só começa com 12 testers inscritos. Para o CEO: "Android só pode ir para todos a partir de <data de hoje + 14 dias>, se 12 pessoas entrarem no teste hoje."
