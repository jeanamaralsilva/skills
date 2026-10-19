# Logs e armazenamento no aparelho

Consultado em 2026-10-19.

## Dado pessoal em log

Log é copiado para a plataforma de deploy, para o Sentry, para quem dá suporte, e fica sem prazo. A OWASP trata dado sensível em log como fraqueza própria (MASWE-0005) [fonte: https://mas.owasp.org/MASWE/MASVS-STORAGE/MASWE-0005/] e o Mobile Top 10 cita "unprotected logging" em M9 [fonte: https://owasp.org/www-project-mobile-top-10/2023-risks/m9-insecure-data-storage].

`scripts/pii_scan.py` acusa:
- `PRV-LOGCRED` (P1): senha, token ou segredo em `console.*`, `Logger.*`, `IO.inspect`, `logger.*`.
- `PRV-LOG` (P2): e-mail, telefone, documento, endereço, localização, IP ou objeto inteiro (`user`, `params`, `body`) no log. Log dentro de `if (__DEV__)` é ignorado.
- `PRV-TER` (P1): o mesmo indo para Sentry, Firebase, Amplitude, Mixpanel, PostHog, OneSignal e afins.

Correções por stack:

| Stack | Correção | Fonte |
|---|---|---|
| Phoenix | `config :phoenix, :filter_parameters, ["password", "token", "cpf", ...]` (padrão só `"password"`, comparação sensível a maiúsculas) ou `{:keep, [...]}` para filtrar tudo menos o listado | https://hexdocs.pm/phoenix/Phoenix.Logger.html |
| Elixir Logger | não usar `metadata: :all`; listar só chaves sem dado pessoal | https://hexdocs.pm/logger/Logger.Formatter.html |
| Ecto | `field :cpf, :string, redact: true` esconde o valor no `inspect` do schema e do changeset; `@schema_redact :all_except_primary_keys` no schema todo | https://hexdocs.pm/ecto/Ecto.Schema.html |
| Node (pino) | `redact: ["req.headers.authorization", "user.email"]` troca o valor por `[Redacted]` | https://raw.githubusercontent.com/pinojs/pino/main/docs/redaction.md |
| React Native | logue id e evento, não o objeto; tire `console.log(user)` do código de produção | |
| Sentry | `beforeSend` para limpar; `sendDefaultPii: false` | https://docs.sentry.io/platforms/react-native/data-management/sensitive-data/ |

Log já gerado com dado pessoal: avalie retenção e apague na plataforma (com confirmação). Credencial em log: troque a credencial e trate como incidente (`08-incidente.md`).

## Armazenamento no aparelho

| Onde | Criptografado? | Fonte |
|---|---|---|
| `expo-secure-store` | sim: Keychain no iOS, Keystore no Android | https://docs.expo.dev/versions/latest/sdk/securestore/ |
| AsyncStorage | não: "unencrypted, persistent key-value storage" | https://raw.githubusercontent.com/react-native-async-storage/async-storage/main/README.md |
| `react-native-mmkv` | só com `encryptionKey`; sem ela, texto puro | https://raw.githubusercontent.com/mrousavy/react-native-mmkv/main/README.md |

Controles da OWASP: MASVS-STORAGE-1 "armazena dado sensível com segurança" e MASVS-STORAGE-2 "evita vazamento de dado sensível" [fonte: https://mas.owasp.org/MASVS/05-MASVS-STORAGE/].

Regras:
- Token de acesso, refresh, senha, documento: `expo-secure-store`. `PRV-ARM` (P1) quando estão em AsyncStorage, MMKV sem chave ou `localStorage`.
- Sessão do login persistida por SDK de auth com `storage: AsyncStorage` (comum em clientes Supabase) também é token em texto puro: use um adaptador que guarde no SecureStore ou que criptografe com chave do SecureStore.
- MMKV com `encryptionKey`: a chave vem do SecureStore, nunca fixa no código [fonte: https://raw.githubusercontent.com/mrousavy/react-native-mmkv/main/README.md].
- Valor grande no SecureStore: algumas versões do iOS recusavam acima de ~2048 bytes; trate o erro [fonte: https://docs.expo.dev/versions/latest/sdk/securestore/].
- No iOS, item do Keychain pode sobreviver à desinstalação; no Android some. Na exclusão de conta e no logout, apague explicitamente [fonte: https://docs.expo.dev/versions/latest/sdk/securestore/].
- Backup do Android: com Auto Backup padrão, o Expo exclui o SecureStore do backup; com backup customizado, exclua à mão [fonte: https://docs.expo.dev/versions/latest/sdk/securestore/].
- Perfil inteiro em cache (`PRV-ARM2`, P2): guarde só o que a tela precisa offline e limpe no logout.
