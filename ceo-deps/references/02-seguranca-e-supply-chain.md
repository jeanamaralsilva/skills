# Segurança e supply chain

Dois problemas diferentes: **vulnerabilidade conhecida** (CVE num pacote legítimo) e **pacote malicioso** (versão publicada por quem roubou o token). O primeiro se acha com audit. O segundo se evita com processo: lockfile, cooldown e install sem scripts.

## Vulnerabilidade conhecida

| Ecossistema | Comando | Leitura |
|---|---|---|
| npm | `npm audit --audit-level=high --omit=dev` | `--audit-level` só define o exit code |
| pnpm | `pnpm audit --audit-level high --prod` | `--fix` grava overrides |
| bun | `bun audit --audit-level=high --prod` | lê o bun.lock; exit 1 com vulnerabilidade |
| Hex | `mix hex.audit` | Hex 2.5+: sai != 0 com pacote retirado **ou** com advisory |
| Hex | `mix deps.audit --format json` (mix_audit) | base mirego/elixir-security-advisories, sincroniza com o GitHub Advisory |
| Phoenix (código) | `mix sobelow --exit medium` | XSS, SQLi, config insegura; vermelho é alta confiança |
| Todos | `osv-scanner scan -r .` | lê lockfiles de 13+ ecossistemas; não cobre Swift/CocoaPods |
| Swift | `trivy fs --scanners vuln .` | Package.resolved e Podfile.lock |

### Sem install ou sem a ferramenta (o caso comum na auditoria)

```bash
python scripts/lock_audit.py <repo> --query           # versões exatas do lock contra o OSV
python scripts/lock_audit.py <repo> --emit batch.json # sem rede: gera o lote para consultar de outra máquina
```

Lê `mix.lock`, `bun.lock`, `package-lock.json` e `pnpm-lock.yaml` (ignorando lock que está no `.gitignore`). Sem rede para o OSV ele sai com 2 e diz "não verificado". **Não pare aí.** Faça a checagem pela web (WebFetch), nesta ordem de prioridade, só para as versões exatas do lock:

1. Servidor e parsers expostos à internet: bandit, cowboy, plug, phoenix, phoenix_live_view, mint, finch, req, hackney, postgrex; no mobile, o que faz rede ou parse (axios, firebase, libs de auth).
2. Auth e sessão: guardian, joken, assent, bcrypt, libs de OAuth.
3. Painéis e admin: oban_web, phoenix_live_dashboard.
4. O resto das dependências de runtime; ferramentas de build e teste por último.

Fontes: `https://osv.dev/list?ecosystem=Hex&q=<pacote>` (ou `ecosystem=npm`), `https://github.com/advisories?query=ecosystem%3Aerlang+<pacote>` e a página de advisories do pacote no hex.pm. Para cada CVE, anote a versão corrigida e se cabe no requisito atual do `mix.exs`/`package.json` (update seguro) ou exige major (decisão).

Numa auditoria de teste do WAYUP (out/2026), essa checagem apontou CVEs em bandit 1.10.3, plug 1.19.1, phoenix 1.8.5, mint 1.7.1, postgrex 0.22.0, guardian 2.4.0, oban_web 2.12.3 e req 0.5.17, quase todas corrigidas dentro dos requisitos atuais (lista não reconferida item a item: confirme cada advisory antes de agir). Uma auditoria que só tentou `mix hex.audit` e parou deixou tudo isso de fora.

Regras:
- **Não use `npm audit fix --force`.** A própria doc avisa que pode instalar major. Corrija com upgrade dirigido e verificação.
- **Vulnerabilidade em devDependency** pesa menos que em produção, mas ferramenta de build comprometida também é porta de entrada. Marque P2, não ignore.
- **Alcançabilidade:** prefira ferramenta que diz se o código chama a função vulnerável (govulncheck no Go). Sem isso, diga "presente no lock, alcançabilidade não verificada".

Caso real: `req` abaixo de 0.6.1 tem CVE-2026-49755 (extração de arquivo compactado sem limite, High) e CVE-2026-49756 (CRLF em multipart). O assent usa Req quando ele está presente, então o risco chega também pelo OAuth. `data/incidents.csv` IC06.

## Pacote malicioso: o que prevenir

Incidentes reais em `data/incidents.csv`: chalk/debug (set/2025, phishing do mantenedor), Shai-Hulud (worm, 500+ pacotes), Trivy e trivy-action comprometidos (mar/2026), axios 1.14.1 e 0.30.4 com RAT (mar/2026).

| Defesa | Como checar | Como aplicar |
|---|---|---|
| Lockfile commitado e install determinístico | lockfile no git; CI usa `npm ci`, `pnpm install --frozen-lockfile`, `bun ci` | trocar `npm install` por `npm ci` no CI |
| Install sem scripts no CI | `--ignore-scripts` no CI | `npm ci --ignore-scripts`; Bun já bloqueia scripts fora de `trustedDependencies` |
| Idade mínima de release (cooldown) | `.npmrc` `min-release-age`, `pnpm-workspace.yaml` `minimumReleaseAge`, `bunfig.toml`, Hex `cooldown` | npm 11.10+: `min-release-age=3` (dias); pnpm 10.16+: minutos; Bun: segundos; Hex: `mix hex.config cooldown 7d`; Renovate `minimumReleaseAge`; Dependabot `cooldown` |
| Provenance | `npm audit signatures` | preferir pacotes com trusted publishing; axios comprometido não tinha o vínculo OIDC |
| Comportamento suspeito | `socket ci` | install scripts, rede, typosquat |
| GitHub Actions fixadas por SHA | `grep -rn "uses: .*@v" .github/workflows` | trocar tag por SHA completo (caso trivy-action) |
| Deps por git | `scripts/detect_stack.py` | Hex: `ref:` com SHA de 40 caracteres em vez de `tag:` |

## Saúde do upstream

- `npm view <pkg> deprecated time.modified`: depreciado e última publicação.
- deps.dev: `https://api.deps.dev/v3/systems/npm/packages/<pkg>/versions/<v>` traz licença, advisories, data e provenance.
- OpenSSF Scorecard: `scorecard --repo=github.com/<owner>/<repo>` (Maintained, Pinned-Dependencies, Dangerous-Workflow).
- React Native Directory: marca `unmaintained` e suporte à New Architecture (o expo-doctor consulta).

Princípio (trailofbits supply-chain-risk-auditor): **dado indisponível nunca é evidência de risco nem de saúde.** Cada pacote termina como avaliado-limpo, avaliado-com-alerta ou não-avaliável.
