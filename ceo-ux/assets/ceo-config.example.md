# Config das skills CEO

Copie para `.ceo/config.md` na raiz do repo (ou do monorepo). Para preferências que valem em todos os projetos, `~/.ceo/profile.md` com o mesmo formato; o do repo vence. Tudo é opcional: sem o arquivo, a skill pergunta só o que mudaria a ação e assume o resto.

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
