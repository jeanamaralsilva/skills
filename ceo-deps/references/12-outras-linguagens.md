# Outras linguagens

Comandos completos com fonte em `data/checks.csv` (linhas XL01 a XL36). `python scripts/search.py "<linguagem> <tema>" --domain checks` acha a linha certa.

| Ecossistema | Vulnerabilidade | Desatualizado | Sem uso | Licença | Lockfile |
|---|---|---|---|---|---|
| Python | `pip-audit` / `uv audit` | `poetry show --outdated` | `deptry .` | `pip-licenses --allow-only` | `poetry check --lock` / uv.lock |
| Go | `govulncheck ./...` (diz se é alcançável) | `go list -m -u all` | `go mod tidy -diff` | `go-licenses check` | go.sum |
| Java/Kotlin (Gradle) | `./gradlew dependencyCheckAnalyze` (NVD API key) | `./gradlew dependencyUpdates` | `./gradlew buildHealth` | via OSV/Trivy | `--write-locks` |
| Java (Maven) | `dependency-check-maven:check` | `versions:display-dependency-updates` | `dependency:analyze` | via OSV/Trivy | n/a |
| Swift | `trivy fs --scanners vuln .` | `pod outdated` | não há ferramenta confiável | manual | Package.resolved / Podfile.lock |
| Ruby | `bundle-audit check --update` | `bundle outdated` (não verificado) | n/a | n/a | Gemfile.lock |
| Rust | `cargo audit` | `cargo outdated` (não verificado) | `cargo machete` | `cargo deny check licenses` | Cargo.lock |
| PHP | `composer audit --abandoned=report` | `composer outdated --direct` | n/a | `composer licenses` | `composer validate --check-lock` |
| .NET | `dotnet package list --vulnerable --include-transitive` | `--outdated` / `--deprecated` | n/a | n/a | packages.lock.json |
| Dart/Flutter | `dart pub get` (mostra advisories) | `dart pub outdated` | `dependency_validator` | n/a | pubspec.lock |

Transversal (qualquer stack): `osv-scanner scan -r .`, `trivy fs`, `syft` (SBOM CycloneDX/SPDX) + `grype`, OpenSSF Scorecard.

Avisos:
- **Go:** `govulncheck` em JSON/SARIF sai sempre 0; no CI trate o resultado.
- **Gradle/Maven:** Dependency-Check por CPE tem falso positivo; mantenha arquivo de supressão.
- **CocoaPods:** trunk read-only a partir de 2026-12-02. App com pods novos precisa planejar SPM.
- **.NET 10:** o comando é `dotnet package list`; no 9 ou anterior, `dotnet list package`.

Para revisão de código nessas linguagens (não de dependências), a `ceo-cortex` tem guias por linguagem.
