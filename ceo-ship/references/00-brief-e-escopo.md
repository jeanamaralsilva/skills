# Brief e escopo

Antes de rodar qualquer coisa, leia a config (`.ceo/config.md` na raiz do repo; depois `~/.ceo/profile.md`; modelo em `assets/ceo-config.example.md`, seção "Chaves da ceo-ship") e monte o brief em silêncio. Ele não entra na resposta. Sem config, pergunte só o que muda a ação.

```
App:          <caminho; Expo gerenciado (CNG), Expo com ios/ e android/ no git, ou nativo>
Lojas:        ios | android | ambas
Pedido:       lançar versão | só OTA | primeira publicação | respondeu rejeição | rollback
O que mudou:  <commits/PRs desde a última versão na loja>
Conta Play:   empresa | pessoal criada depois de 13/11/2023
Read-only?:   sim (só relatório) | não (pode editar app config em branch)
```

## Modos

| Modo | Quando | O que entrega |
|---|---|---|
| Pré-voo | "vou subir versão", "posso mandar pra loja?", "o que falta pra publicar" | Veredito (sobe, sobe com risco, não sobe), achados P0 a P3, checklist manual |
| OTA ou build | "dá pra mandar por update?", "precisa de build novo?" | Decisão com prova (fingerprint ou lista de mudanças nativas) e comandos |
| Primeira publicação | app nunca foi para a loja | Pré-voo completo mais contas, trilhas, teste fechado, página da loja |
| Rejeição | colaram a mensagem da Apple ou do Google | Diretriz, causa no código, correção e texto de resposta |
| Rollback | "a versão nova quebrou" | O que dá para desfazer em cada loja e no OTA, e o passo a passo |

Na dúvida, pré-voo. Pré-voo não edita nada sem pedido.

## O que mudou desde a última versão

É a pergunta que decide OTA ou build e o que testar. Ache a última versão publicada (tag git, `eas build:list --platform ios --limit 5`, ou pergunte) e liste as mudanças. Mudança nativa (lib nativa nova ou atualizada, permissão, config plugin, SDK) muda a decisão: `references/05-versao-ota-ou-build.md`.

## Read-only

Repo marcado `read_only: true` ou que não é do CEO: só relatório. `git` com `--no-optional-locks`. Correção vira patch para o dono aplicar.
