# Inventário

```bash
python scripts/detect_stack.py <repo> [<repo2> ...]          # texto
python scripts/detect_stack.py <repo> [<repo2> ...] --json   # para subagente
```

Detecta, até 3 níveis de pasta:

| Item | Por que importa |
|---|---|
| Ecossistemas por manifest (package.json, mix.exs, pubspec, pyproject, go.mod, Gradle, Podfile, Package.swift...) | Decide quais tracks e ferramentas rodar |
| Lockfiles e gerenciadores | Mais de um lockfile JS no mesmo projeto é P1; sem lockfile, o install não é determinístico |
| Toolchain fixada (.nvmrc, .tool-versions, mise.toml, engines, packageManager) | Sem Node/Elixir/OTP fixados, cada máquina e o CI compilam diferente |
| Versões que mandam na compatibilidade (expo, react-native, phoenix, live_view, requisito de elixir) | Base do track de versões |
| Deps por git | Ficam fora do audit do registry e sem checksum; tag é mutável |
| overrides/resolutions | Curativos que precisam de data para sair |
| Dependabot/Renovate e workflows de CI | Sem bot, ninguém fica sabendo de CVE nova |

## Depois do script, confirme à mão

1. **Qual gerenciador o time usa de verdade:** `packageManager` no package.json, scripts de CI, README, `CLAUDE.md`. O lockfile do gerenciador que sobra deve ser removido (no modo manter, em branch).
2. **Expo:** se o projeto é CNG (sem `ios/` e `android/` commitados) ou tem pastas nativas commitadas. Com `ios/Podfile.lock` commitado, os pods também são dependência a auditar.
3. **Elixir:** `mix.lock` commitado, `.tool-versions`/`mise.toml`, Dockerfile (versão de Elixir/OTP da imagem).
4. **Monorepo:** um package.json na raiz com workspaces muda as regras (`references/03-versoes-e-compatibilidade.md`, monorepo).

## Exemplo real (app Expo + server Phoenix, out/2026)

- mobile: Expo `^57.0.0`, RN 0.86.0, **bun.lock e package-lock.json juntos**, Node fixado em `.tool-versions`, sem bot, sem CI.
- server: Phoenix `~> 1.8.3`, LiveView `~> 1.1.0`, `elixir: "~> 1.15"`, heroicons por **tag**, Elixir/OTP não fixados, sem bot, sem CI.
