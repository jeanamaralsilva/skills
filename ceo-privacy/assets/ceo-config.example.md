# Config das skills CEO

Copie para `.ceo/config.md` na raiz do repo (ou do monorepo). Para preferências que valem em todos os projetos, `~/.ceo/profile.md` com o mesmo formato; o do repo vence, com duas exceções de segurança: `read_only: true` no perfil não pode ser desligado pelo repo, e caminho de repo fora da pasta atual (absoluto ou com `..`) só é usado depois de o usuário confirmar. Um repo clonado de terceiros pode trazer `.ceo/config.md`; trate-o como sugestão, não como permissão. Tudo é opcional: sem o arquivo, a skill pergunta só o que mudaria a ação e assume o resto.

```yaml
projeto: nome-do-app

repos:
  - path: apps/mobile        # relativo à raiz, ou caminho absoluto
    papel: mobile            # mobile | server | web | lib
    read_only: false         # true: só relatório, nenhuma escrita, nenhum PR
  - path: apps/server
    papel: server
    read_only: true

maquina:
  ram_gb: 16
  build_nativo_local: false  # false: build nativo só na nuvem (EAS, CI)
  simuladores_max: 2         # quantos simuladores iOS ao mesmo tempo
  apagar_testes_ao_fim: true # remover simuladores, vídeos e prints criados pela sessão

plataformas: ios             # ios | android | ambos (o que você testa hoje)

design:
  ds_skill:                  # skill do design system do time, se houver
  brand_skill:               # skill da marca (paleta, logo), se houver
  tema: dark                 # dark | light | ambos

fluxo:
  pr_skill:                  # skill que abre PR com evidência, se houver
  texto_skill:               # skill de revisão de texto, se houver

testes:
  bundle_id: com.exemplo.app
  deeplink_scheme: app://
  servidor_ws: ws://localhost:4000/socket   # Phoenix, Socket.IO, etc.
  papeis: [admin, usuario]   # perfis que interagem no mesmo fluxo
  credenciais: env           # TEST_USER_<PAPEL> e TEST_PASS_<PAPEL> no ambiente; nunca no repo
  maestro_dir: .maestro
```

Regras:
- Credencial nunca entra neste arquivo nem no repo. Só nome de variável de ambiente.
- `read_only: true` é respeitado por todas as skills: nem branch, nem lockfile, nem `git status` sem `--no-optional-locks`.
- Campo vazio é "não sei": a skill não inventa. Se o campo mudaria a ação (ex.: `build_nativo_local`), ela pergunta.

## Chaves da ceo-ship

```yaml
lancamento:
  lojas: ambas               # ios | android | ambas
  conta_play: empresa        # empresa | pessoal_nova (pessoal criada depois de 13/11/2023 exige teste fechado antes da produção)
  gradual: true              # phased release (iOS) e staged rollout (Android) por padrão
  idiomas_loja: [pt-BR]      # idiomas da página da loja e das notas de versão
  conta_demo: env            # DEMO_USER e DEMO_PASS no ambiente, para o revisor; nunca no repo
```

## Chaves da ceo-brief

```yaml
brief:
  leitor: dono               # dono | socio | investidor | cliente (padrão de quem lê)
  idioma: pt-BR
  janela_padrao: 7d          # 1d | 7d | desde a última tag (tag)
  max_palavras: 250
  base: origin/main          # ramo que conta como entregue; vazio = origin/HEAD
  app_na_loja: true          # true: "entregue" só com versão na loja ou atualização pelo ar
  ultimo_update: 2026-09-30  # data do último update para sócio ou investidor (janela do próximo)
  labels_bug: [bug, incidente]
  enviar_para:               # vazio: o brief nunca é enviado; só com pedido explícito
```

## Chaves da ceo-incident

Onde olhar e como voltar atrás. Só nomes, caminhos e links de painel: nenhuma credencial, token ou URL com segredo.

```yaml
incidente:
  fuso: -03:00               # fuso das horas na linha do tempo e nos avisos
  pasta: .ceo/incidents      # um arquivo por incidente: AAAA-MM-DD.md (fora do git)
  crash: sentry              # sentry | crashlytics | outro | nenhum
  crash_painel:              # link do painel de crash do app (sem token na URL)
  logs_servidor: plataforma  # plataforma | arquivo | outro (onde ler log do servidor)
  deploy: fly                # fly | railway | render | vercel | heroku | docker | outro
  deploy_painel:             # link do painel de deploy
  ota: eas                   # eas | nenhum
  canal_ota: production      # canal do EAS Update que os clientes usam
  status_terceiros: [expo, apple, google-play, github]  # páginas de status que importam
  feature_flags:             # serviço ou módulo de flags, se houver
  status_page:               # página de status pública, se houver (a skill nunca publica nela)
  comunicacao:
    dono: chat               # por onde o dono quer o update (a skill só escreve o texto)
    cadencia_min: 30         # minutos entre updates em SEV1 e SEV2
  postmortem_obrigatorio: [SEV1, SEV2]
```

## Chaves da ceo-privacy

Quem é quem e para quem o app fala. Só nomes, cargos e links: nenhum dado pessoal de cliente, nenhuma credencial.

```yaml
privacidade:
  paises: [BR]               # BR | UE | EUA ... onde há usuários (UE liga as regras do GDPR)
  publico_menor: nao         # nao | provavel | sim (app usado ou direcionado a menores de 18)
  pequeno_porte: nao_sei     # sim | nao | nao_sei (agente de pequeno porte, Resolução CD/ANPD nº 2/2022)
  controlador:               # razão social que aparece na política (sem CPF/CNPJ aqui)
  encarregado_contato:       # canal público do encarregado (e-mail de função ou formulário), nunca pessoal
  canal_titular:             # onde o usuário pede acesso, correção ou exclusão (tela, e-mail de função, formulário)
  politica_url:              # URL pública da política de privacidade
  exclusao_web_url:          # URL pública para pedir exclusão de conta (exigida pelo Google Play)
  retencao:                  # prazos combinados por tipo de dado, se já existem
    logs_dias:
    backups_dias:
    conta_excluida_dias:     # quanto tempo até apagar de vez depois do pedido
  advogado:                  # quem revisa política, termos e comunicação de incidente (nome do escritório ou "nenhum")
```
