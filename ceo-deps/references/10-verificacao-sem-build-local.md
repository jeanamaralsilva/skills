# Verificação sem build nativo local

Muitas máquinas de dev não têm memória para build nativo (ver `máquina` em `.ceo/config.md`). A escada vai do mais leve (roda em segundos no Mac) ao mais pesado (roda na nuvem). Suba só até onde a mudança exige, e diga no relatório até onde subiu.

## Expo / React Native

| Degrau | Comando | Pega | Onde roda |
|---|---|---|---|
| 1. Doctor | `npx expo-doctor` e `npx expo install --check` | versão fora do SDK, duplicata nativa, config | Mac |
| 2. Tipos | `npx tsc --noEmit` | API da lib que mudou | Mac |
| 3. Testes | script de teste do repo (`npm test -- --watchAll=false`) | comportamento | Mac |
| 4. Bundle JS | `npx expo export --platform all` | import quebrado, módulo que o Metro não resolve | Mac (leve, sem nativo) |
| 5. Mudou algo nativo? | `npx @expo/fingerprint fingerprint:generate` e `fingerprint:diff`, ou `eas fingerprint:compare` | decide se precisa de build novo | Mac |
| 6. Build na nuvem | `eas build --profile preview --platform ios` (perfil com `"ios": {"simulator": true}`, ver `assets/eas-simulator-profile.json`) | compilação nativa, pods, plugins | EAS |
| 7. Rodar no simulador | `eas build:run -p ios --latest` | o app abre e navega | simulador no Mac (só instala, não compila) |
| 8. Smoke test | `maestro test .maestro/<fluxo>.yml` | fluxo principal funciona | simulador |

Regras:
- **Fingerprint igual ao do último build:** não precisa de build novo; uma atualização OTA (`eas update --channel <canal> --environment <env>`) basta. Fingerprint diferente: build novo.
- **Nunca `eas build --local`** numa máquina sem memória para isso: é a mesma compilação que falta memória.
- **Simulador de iOS não exige conta Apple Developer** com o perfil `simulator: true`.
- **Plano free do EAS:** 15 builds Android e 15 iOS por mês, fila de baixa prioridade, timeout de 45 min. Gaste build só quando o fingerprint mudou.
- Mudou dependência nativa (duplicata, módulo do SDK, pods)? O degrau 6 é obrigatório antes de dizer "resolvido".

## Elixir / Phoenix

| Degrau | Comando | Onde |
|---|---|---|
| 1 | `mix deps.get` (Hex 2.5 já avisa advisories) | Mac ou CI |
| 2 | `mix compile --warnings-as-errors` | Mac ou CI |
| 3 | `mix format --check-formatted` e `mix credo --strict` (se o repo usa) | Mac ou CI |
| 4 | `mix test` | CI se o Mac não aguentar o Postgres local |
| 5 | `mix hex.audit` e `mix deps.audit` | Mac ou CI |
| 6 | `docker build` com o Dockerfile de `mix phx.gen.release --docker` | CI |

Modelo de CI: `assets/github-actions-elixir.yml` (usa `erlef/setup-beam`, Postgres como service e as versões do `.tool-versions`).

## No relatório

Uma linha: até que degrau passou e o que não rodou. Exemplo: "doctor, tsc, testes e export ok; build EAS iOS ok (simulador); Android não buildado (fingerprint igual)".
