# Integrações

A `ceo-privacy` cuida do dado pessoal. O resto ela chama, se a skill estiver instalada; sem ela, diga o que ficou de fora.

| Situação | Chamar |
|---|---|
| Vai subir versão: rótulos App Privacy e Data safety, privacy manifest, textos de permissão, exclusão de conta no app | `ceo-ship` (passe o mapa de dados e a lista de SDKs) |
| Dado pessoal exposto, vazado ou acessado sem autorização | `ceo-incident` para conter e registrar; a parte de ANPD e titulares fica aqui (`references/08-incidente.md`) |
| SDK novo, SDK sem privacy manifest, licença ou versão vulnerável | `ceo-deps` |
| Revisar a correção (log, armazenamento, endpoint de exclusão) antes de subir | `ceo-code-review` |
| Provar no aparelho que a exclusão de conta funciona de ponta a ponta | `ceo-mobile-qa` |
| Explicar o risco ao sócio ou investidor em linguagem de negócio | `ceo-brief` |

Política de privacidade e termos: a skill entrega o checklist de coerência (`assets/checklist-politica-privacidade.md`). Se o time tiver uma skill própria de redação de termos, use-a para o texto e volte aqui para conferir contra o código.
