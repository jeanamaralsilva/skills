# Integrações

A `ceo-ship` cuida do lançamento. O resto ela chama, sempre se a skill estiver instalada; sem ela, diga o que ficou de fora.

| Situação | Chamar |
|---|---|
| Antes de subir: smoke test do build de produção (login, fluxo principal, compra, push) e crash do TestFlight | `ceo-mobile-qa` |
| Target API, Xcode ou SDK do Expo abaixo do exigido; lib sem privacy manifest ou sem suporte a 16 KB | `ceo-deps` (upgrade seguro, um SDK por vez) |
| Escolher e ordenar screenshots, primeira impressão da página da loja | `ceo-ux` |
| Polimento antes de soltar ("o que o cliente vai achar feio") | `ceo-bug-bash` |
| Código que a correção tocou (tela de excluir conta, por exemplo) | `ceo-code-review` |
| Política de privacidade, termos, App Privacy, Data safety | skill de termos e privacidade do time, se houver |
| Abrir PR com as correções | skill de PR da config (`fluxo.pr_skill`) ou `gh pr create` |

A `ceo-ship` não testa o app nem atualiza dependência: ela aponta e chama.
