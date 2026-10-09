# Versões e compatibilidade

O erro mais caro em dependência não é a versão velha, é a **combinação incompatível**: módulo nativo fora do SDK, duas cópias do mesmo módulo nativo, Elixir compilado para outro OTP.

## Expo / React Native

**Fonte da verdade:** `node_modules/expo/bundledNativeModules.json` do SDK instalado. É o que `npx expo install --check` usa. Exemplo no expo 57.0.27: `"@expo/ui": "~57.0.22"`, `"react-native": "0.86.3"`.

```bash
npx expo-doctor@latest --verbose     # 22 checks; exit 1 se algum falha
npx expo install --check             # lista desalinhados ao SDK
npx expo install --fix               # realinha (modo manter)
python scripts/expo_check.py <app> [--bundled <bundledNativeModules.json>]
```

O `expo_check.py` roda sem instalar nada. Sem `node_modules`, baixe o arquivo do SDK:
`https://raw.githubusercontent.com/expo/expo/sdk-<N>/packages/expo/bundledNativeModules.json`, ou `npm pack expo@<versão>` numa pasta temporária. Ele aponta desalinhamento minor/patch, duplicata nativa (com `node_modules`) e o caso Hermes.

### Como ler a saída do expo-doctor

| Check | Significa | Correção |
|---|---|---|
| `AutolinkingDependencyDuplicatesCheck` "Found duplicates for X" | duas versões do mesmo módulo nativo; build nativo só aceita uma | `npm why X` (ou `pnpm why --depth=10`, `yarn why`, `bun pm why`) para achar quem puxa; alinhar o range no package.json; `npm dedupe`/`pnpm dedupe`/`yarn dedupe`; se nada resolver, override temporário |
| `HermesV1VersionCheck` | expo 55, 56 ou 57 abaixo de 57.0.9 com Hermes V1 tem regressão de memória | `npx expo install expo@^57.0.9 --fix` (57.0.9 leva o RN a 0.86.2) |
| `InstalledDependencyVersionCheck` "Minor/Patch version mismatches" | pacote fora do range do SDK | `npx expo install --fix`; exceção intencional vai em `expo.install.exclude` |
| `DependencyVersionOverrideCheck` | override quebrando a cadeia expo, @expo/cli, metro | remover o override |
| `ReactNativeDirectoryCheck` | lib `unmaintained` ou sem New Architecture | trocar a lib (vira decisão do Jean se for central) |
| `LockfileCheck` | lockfile ausente | gerar e commitar |
| `StoreCompatibilityCheck` | targetSdkVersion abaixo do mínimo da Play | subir pelo `expo-build-properties` |
| `VectorIconsCheck` / `ExpoRouterReactNavigationCheck` | dois sets de ícones; react-navigation direto junto do expo-router | ficar com um |

Caso real da imagem do Jean (WAYUP, expo 57.0.4): `@expo/ui` 57.0.4 na raiz e 57.0.18 dentro de `expo-widgets`, regressão Hermes, flash-list 2.3.2 contra 2.0.2 exigido e 25 patches atrás. A causa da duplicata estava no `package.json`: `expo-widgets` fixo em 57.0.19 pedia o próprio `@expo/ui` 57.0.18. Subir `@expo/ui` e `expo-widgets` juntos para o patch atual do SDK deixou uma cópia só. Havia também um `package-lock.json` local, ignorado pelo git, com versões diferentes do `bun.lock`: não era a causa, mas é armadilha para quem rodar `npm i`.

### Update OTA e runtimeVersion

`runtimeVersion: { policy: "sdkVersion" }` só muda quando o SDK muda. Um patch de React Native, um módulo nativo novo ou a troca de versão do react-native-screens mantêm o mesmo runtime, e um `eas update` pode entregar JS que chama código nativo que o binário instalado não tem: crash. Prefira `policy: "fingerprint"` (muda sempre que algo nativo muda) ou `appVersion` com disciplina de versão. O `detect_stack.py` acusa `sdkVersion`. É P1 em app que publica OTA.

Regras:
- **Nunca `npm install <lib>@latest` para módulo nativo em projeto Expo.** Use `npx expo install <lib>`.
- **Upgrade de SDK é `npx expo install expo@^N --fix`**, um SDK por vez, lendo o changelog. Não pelo bot.
- **Monorepo:** React Native duplicado não é suportado. Se os installs isolados quebrarem, `nodeLinker: hoisted` no pnpm.

## Elixir / OTP / Phoenix

| Elixir | OTP suportado |
|---|---|
| 1.20 | 27 a 29 |
| 1.19 | 26 a 28 |
| 1.17 e 1.18 | 25 a 27 |
| 1.15 e 1.16 | 24 a 26 |

- Só a última minor recebe bugfix; as cinco últimas recebem patch de segurança. `elixir: "~> 1.15"` (padrão do `phx.new` 1.8) aceita versão sem patch: suba o mínimo.
- Fixe com sufixo do OTP: `mise use erlang@29 elixir@1.20.4-otp-29`.
- `mix hex.outdated` (diretas), `--all` (transitivas), `--within-requirements` (sai 1 só se há update dentro do `~>`, ou seja, update seguro esquecido).
- `~> 2.0` aceita até `< 3.0`; `~> 2.0.1` aceita até `< 2.1`.
- `mix compile --warnings-as-errors`: pega deprecações do Phoenix 1.8/LiveView 1.1 e os bugs do type checker do 1.19/1.20.
- LiveView 1.1 não é mais a linha atual (1.2 existe); a última 1.1 é a 1.1.32.

## Toolchain

Node: LTS par fixado em `.nvmrc`/`.tool-versions` e `engines`. Elixir/OTP: `.tool-versions` ou `mise.toml`, e a mesma versão no Dockerfile e no CI.
