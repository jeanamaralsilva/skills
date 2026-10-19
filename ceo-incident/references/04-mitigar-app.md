# Mitigar no app (OTA e lojas)

Consultado em 2026-10-19. Comandos com fonte em `data/mitigacao.csv` (ids OT e LJ). Detalhe de lançamento gradual: `ceo-ship`, se instalada.

## Primeiro: o problema veio de onde?

- Update OTA: a tag `expo.updates.update_id` no Sentry ou `eas update:insights <GROUPID>` [fontes: https://docs.sentry.io/platforms/react-native/guides/expo/manual-setup/expo/expo-updates/ e https://docs.expo.dev/eas/cli/].
- Versão da loja: crash concentrado numa versão ou build no Sentry, Crashlytics ou Organizer.
- Servidor: app quebra porque a API mudou ou caiu. Aí a mitigação é no servidor.

## EAS Update

Ler antes: `eas update:list --branch <branch>`, `eas channel:view <canal>`.

| Ação | Comando |
|---|---|
| Assistente de rollback (update anterior ou embutido) | `eas update:rollback` |
| Republicar um update anterior | `eas update:republish --group <GROUPID> --message "<motivo>"` |
| Voltar ao JS embutido no build | `eas update:roll-back-to-embedded --channel <canal> --runtime-version <versao> --message "<motivo>"` |
| Desfazer rollout gradual de update | `eas update:revert-update-rollout --group <GROUPID>` |

Fontes: https://docs.expo.dev/eas/cli/, https://docs.expo.dev/eas-update/rollbacks/, https://docs.expo.dev/eas-update/rollouts/.

O que dizer ao dono:
- O app procura update ao abrir, baixa e aplica no próximo reinício, salvo se baixar dentro do `fallbackToCacheTimeout` [fontes: https://docs.expo.dev/versions/latest/sdk/updates/ e https://docs.expo.dev/eas-update/how-it-works/]. Quem pegou o update ruim só melhora depois de abrir o app de novo.
- Update só chega a build com o mesmo `runtimeVersion` [fonte: https://docs.expo.dev/eas-update/runtime-versions/]. Crash de código nativo não se resolve por OTA.
- Antes de voltar, avalie se a versão antiga lê o que a nova salvou no aparelho; sem update seguro para voltar, corrija para frente [fonte: https://docs.expo.dev/eas-update/error-recovery/].
- Depois do rollback, o próximo update publicado chega a todos [fonte: https://docs.expo.dev/eas-update/rollbacks/].

## App Store

- Não há rollback de binário. Pausar o phased release: App Store Connect, versão, Phased Release for Automatic Updates, Pause. Até 30 dias somados; quem procura na loja ainda baixa a versão nova [fonte: https://developer.apple.com/help/app-store-connect/update-your-app/release-a-version-update-in-phases].
- Tornar versão indisponível: Last-Compatible Version Settings [fonte: https://developer.apple.com/help/app-store-connect/manage-your-apps-availability/make-a-version-unavailable-for-download].
- Versão corrigida com revisão expressa, só para urgência real e build já enviado [fonte: https://developer.apple.com/help/app-review/after-submitting-for-review/request-expedited-review].

## Google Play

- Halt do lançamento gradual: Manage rollout, Halt rollout. Quem recebeu fica com a versão [fonte: https://support.google.com/googleplay/android-developer/answer/6346149].
- Halt de release já em 100%: volta a servir a versão 100% anterior; não vale para a primeira release da faixa, teste interno ou anterior com violação de política [fonte: https://support.google.com/googleplay/android-developer/answer/16285429].
- Correção: bundle novo com versionCode maior [fonte: https://developer.android.com/studio/publish/versioning].

Sem fonte oficial verificada: passo a passo de tirar o app inteiro da App Store; efeito de `eas channel:pause` nos aparelhos. Não proponha esses caminhos como certos.
