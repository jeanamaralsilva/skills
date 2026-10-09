# Ciclo de vida e bots

Dependência envelhece sozinha. Sem bot, ninguém fica sabendo de CVE nova nem de lib abandonada.

## Sinais de fim de vida

| Sinal | Como ver |
|---|---|
| Depreciada pelo autor | `npm view <pkg> deprecated`; Hex: `mix hex.audit` (retirada); `dotnet package list --deprecated`; `go list -m -u all` (retracted) |
| Sem release há mais de 12 meses | `npm view <pkg> time.modified`; página do Hex; `data/ui-libraries.csv` da ceo-analytics para libs de UI |
| Marcada unmaintained | React Native Directory; `cargo deny` (advisories unmaintained); `composer audit --abandoned=report` |
| Não acompanha o framework | peerDependencies que não aceitam o React/RN/Elixir atual; sem suporte à New Architecture |
| Ecossistema fechando | CocoaPods trunk fica read-only em 2026-12-02: pods novos e atualizações param de chegar pelo trunk |

Lib abandonada e central (muitos arquivos, ver acoplamento) vira decisão do Jean com prazo. Lib abandonada e periférica: troque no modo manter.

## Bots

Modelos prontos: `assets/renovate.json` e `assets/dependabot.yml`. Escolha um bot por repo.

| Configuração | Por quê |
|---|---|
| Cooldown (`minimumReleaseAge` no Renovate, `cooldown` no Dependabot) de 3 a 7 dias | versão maliciosa costuma ser removida em horas ou dias |
| Agrupar patch/minor | um PR por semana em vez de vinte |
| Expo SDK fora do bot | upgrade de SDK é `npx expo install expo@^N --fix` com changelog; pacotes do SDK seguem o SDK |
| `rangeStrategy: pin` em app (Renovate, mix) | o lock manda; range frouxo esconde mudança |
| Lockfile maintenance semanal | transitivas atualizadas sem mexer no package.json |
| GitHub Actions no bot | e fixadas por SHA |

Dependabot suporta `npm`, `mix`, `github-actions` e outros; confirme no repo se o gerenciador do projeto (bun, pnpm) está coberto antes de prometer PR automático.

## Ritmo sugerido

- Semanal: PR agrupado do bot, verificado pela escada de `references/10-verificacao-sem-build-local.md`.
- Por SDK do Expo: upgrade dedicado.
- Mensal: `ceo-deps` em modo auditar nos repos ativos.
