# Lançamento gradual e rollback

Consultado em 2026-10-19.

Não existe "desfazer" igual nas duas lojas. Planeje a volta antes de soltar.

## App Store

- **Phased release**: 7 dias, 1%, 2%, 5%, 10%, 20%, 50% e 100%, sorteando quem tem atualização automática. Pausa de até 30 dias, quantas vezes quiser. Quem procurar na loja baixa a versão nova a qualquer momento [fonte: https://developer.apple.com/help/app-store-connect/update-your-app/release-a-version-update-in-phases/].
- **Voltar**: não há botão de rollback. Opções: pausar o phased release, mandar versão corrigida (revisão expressa se for crítico, https://developer.apple.com/help/app-review/after-submitting-for-review/request-expedited-review), ou tornar uma versão indisponível para download em Last-Compatible Version Settings [fonte: https://developer.apple.com/help/app-store-connect/manage-your-apps-availability/make-a-version-unavailable-for-download/].
- Tirar o app da venda remove da loja em até 24 h, e quem já tem continua recebendo updates [fonte: https://developer.apple.com/help/app-store-connect/manage-your-apps-availability/manage-availability-for-your-app-on-the-app-store/].

## Google Play

- **Staged rollout**: só para update. O percentual não sobe sozinho; você aumenta em Gerenciar lançamento. Halt para de entregar a quem não recebeu; quem recebeu fica com a versão [fonte: https://support.google.com/googleplay/android-developer/answer/6346149].
- **Halt de release já em 100%**: a versão anterior que estava 100% volta sozinha. Não vale para a primeira release da trilha nem para o teste interno, nem quando a anterior viola política [fonte: https://support.google.com/googleplay/android-developer/answer/16285429].
- **Corrigir**: nova release com bundle corrigido e versionCode maior; o Android não aceita versionCode menor [fontes: https://support.google.com/googleplay/android-developer/answer/6346149 e https://developer.android.com/studio/publish/versioning].
- Com EAS: `submit.production.android.releaseStatus: "inProgress"` e `rollout: 0.1` mandam a 10% [fonte: https://docs.expo.dev/eas/json/].

## OTA (EAS Update)

| Ação | Comando | Fonte |
|---|---|---|
| Soltar update a 10% | `eas update --channel production --message "..." --environment production --rollout-percentage=10` | https://docs.expo.dev/eas-update/rollouts/ |
| Aumentar | `eas update:edit <GROUPID> --rollout-percentage=50` | https://docs.expo.dev/eas-update/rollouts/ |
| Desfazer rollout de update | `eas update:revert-update-rollout` | https://docs.expo.dev/eas-update/rollouts/ |
| Rollout por branch no canal | `eas channel:rollout <canal>` (durante ele, publique com `--branch`, nunca `--channel`) | https://docs.expo.dev/eas-update/rollouts/ |
| Voltar para um update anterior | `eas update:rollback` (interativo) | https://docs.expo.dev/eas-update/rollbacks/ |
| Voltar para o JS que veio no build | `eas update:roll-back-to-embedded --channel production` | https://docs.expo.dev/eas/cli/ |

## Plano padrão para o CEO

1. Build com o mesmo commit testado (fingerprint igual ao do build testado).
2. iOS com phased release ligado; Android em 10% a 20%.
3. Olhe crash e avaliações por 24 a 48 h (Crashlytics, Sentry ou o painel da loja).
4. Sem regressão, suba. Com regressão: pause/halt, corrija, nova versão.

Os percentuais e prazos do passo 2 e 3 são prática do time, não regra das lojas: diga isso se o CEO perguntar.
