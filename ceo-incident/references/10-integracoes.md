# Integrações

A `ceo-incident` conduz o incidente. O resto ela chama, se a skill estiver instalada; sem ela, diga o que ficou de fora.

| Situação | Chamar |
|---|---|
| Pausar phased release, halt no Play, versão corrigida, OTA ou build | `ceo-ship` |
| Explicar o incidente para o dono, sócio ou cliente em linguagem de negócio | `ceo-brief` |
| Reproduzir o bug no app, provar a correção com vídeo | `ceo-mobile-qa` |
| Conferir se dados ficaram inconsistentes (SELECT só leitura) | `ceo-bug-bash` |
| Causa provável é dependência vulnerável ou SDK | `ceo-deps` |
| Revisar a correção antes de subir | `ceo-code-review` |

Bug sem urgência (um cliente, sem impacto amplo) não é incidente: `ceo-mobile-qa`.
