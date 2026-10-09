# Duplicadas e sem uso

Três tipos de "a mais", com custos diferentes:

| Tipo | Exemplo | Custo |
|---|---|---|
| **Mesma lib, duas versões** | `@expo/ui` 57.0.4 e 57.0.18 | build nativo quebra ou se comporta errado; bundle maior |
| **Duas libs para a mesma função** | axios + fetch; moment + dayjs; flash-list + legend-list | dois jeitos de fazer a mesma coisa, bugs diferentes, bundle maior |
| **Lib declarada e não usada** | dependência que ninguém importa | superfície de ataque e update sem motivo |

## Mesma lib, duas versões

- JS: `npm ls <pkg>` mostra todas as cópias; `npm why <pkg>` mostra quem puxa. `npm dedupe` (ou equivalente) resolve quando os ranges permitem.
- Expo nativo: `references/03-versoes-e-compatibilidade.md`.
- Elixir: o Hex resolve uma versão por pacote; conflito aparece como erro no `mix deps.get`. Leia quem exige com `mix hex.outdated <pkg>`.

## Duas libs para a mesma função

```bash
python scripts/deps_scan.py <repo>
```

Usa `data/functional-groups.csv` (23 grupos: cliente HTTP, datas, utilitários, estado, cache de servidor, validação, formulários, estilo RN, ícones, navegação, bottom sheet, listas, armazenamento, animação, toast, uuid; em Elixir: HTTP, JSON, hash de senha, auth, jobs, e-mail, CSV).

Nem toda dupla é erro. O grupo diz quando convivem:
- **Papéis diferentes são ok:** `expo-secure-store` (segredo) com `react-native-mmkv` (cache); `assent` (OAuth) com `guardian` (token de API).
- **Dependência de outra lib é ok:** `hackney` no server pode estar ali porque o Swoosh usa como cliente padrão, mesmo com Req no app. Confirme antes de remover.
- **Migração pela metade é achado:** duas libs de lista, ou de data, quase sempre é uma migração que não terminou. Conte os arquivos de cada uma (`deps_scan.py` mostra) e proponha terminar a migração na que tem mais uso ou que é a escolha atual do time.

## Sem uso

`deps_scan.py` lista candidatas: dependências sem import no código. Ele já desconta:
- plugins citados em `app.json`/`app.config.*`;
- peers que outra lib carrega (`react-native-screens`, `react-native-worklets`, `react-native-nitro-modules`, `sweet_xml` para ExAws, `hackney` para Swoosh);
- ferramentas de dev em Elixir (`only:` ou `runtime: false`).

Antes de remover, confirme:
- JS: `npx knip --dependencies` (entende plugins de Expo, Jest, Babel).
- Elixir: busque o módulo e o nome do app (`grep -rn "Timex\|:timex"`); `mix deps.unlock --check-unused` só olha o lock, não o uso.
- Busque também em config, scripts do package.json e CI.

Caso real (WAYUP, out/2026): mobile com `@legendapp/list` e `@legendapp/state` sem import (e `@shopify/flash-list` em 11 telas, provável troca de lista que ficou pela metade); server com `timex` e `waffle_ecto` sem referência.
