# Brief, config e modos

Antes de abrir um simulador, monte o brief em silêncio. Ele não entra na resposta.

## Config

Ordem: `.ceo/config.md` na raiz do repo, depois `~/.ceo/profile.md`, depois perguntas. Modelo em `assets/ceo-config.example.md`. O que esta skill lê:

| Campo | Para quê | Sem ele |
|---|---|---|
| `repos[]` com `papel` e `read_only` | onde está o app, onde está o servidor, onde pode escrever | procura pastas irmãs `../<nome>-mobile`, `../<nome>-server` (`14`); trata tudo como read-only |
| `maquina.ram_gb`, `simuladores_max` | quantos simuladores sobem juntos | assume 16 GB: 1 simulador + ator por API |
| `maquina.apagar_testes_ao_fim` | limpeza no fim | sempre apaga o que criou |
| `plataformas` | iOS, Android ou ambos | iOS |
| `testes.bundle_id`, `deeplink_scheme` | `simctl launch`, `openurl`, Maestro `appId` | lê `app.json`/`app.config.*` (`ios.bundleIdentifier`, `scheme`) |
| `testes.servidor_ws`, `papeis`, `credenciais` | segundo ator, login por papel | pergunta o endpoint; credenciais só por variável de ambiente |
| `testes.maestro_dir` | onde ficam os flows do time | `.maestro/` |

Credencial, nesta ordem: (1) usuários do seed de teste do próprio servidor local (Phoenix: `priv/repo/seeds*.exs` ou script de seed de QA; Node: `prisma/seed`, `db:seed`), sem configurar nada; (2) variáveis de ambiente (`TEST_USER_<PAPEL>`, `TEST_PASS_<PAPEL>`) só quando o alvo é staging; (3) pergunta no chat, uma vez, sem gravar em arquivo. Credencial nunca vai para repo, print ou relatório. Produção nunca.

## Brief

```
Objetivo:      <o que o CEO quer saber no fim, em 1 frase>
Modo:          varredura | caça-bug | regressão | multiusuário | estresse | evidência
Alvo:          <telas ou fluxos; "tudo" vira a lista do map_flows.py>
Papéis:        <quem interage: ex. admin e usuário; 1 papel se não houver tempo real>
Entrada:       <vídeo, print, crash, relato do cliente, "está bugado">
Ambiente:      simulador iOS | iPhone físico | TestFlight | servidor local | staging
Limites:       <RAM, tempo, read-only, "não mexe no servidor">
Já sabido:     <bugs conhecidos, o que o CEO já testou>
```

## Modos

| Modo | Gatilho | Entrega |
|---|---|---|
| **Varredura** | "testa o app", "vê se está tudo funcionando", app novo | mapa de telas e ações, matriz de casos, execução do fluxo principal e dos caminhos tristes de cada botão, relatório |
| **Caça-bug** | "o cliente achou bug", vídeo ou print, "trava às vezes" | reprodução dirigida: hipótese por `data/bugs.csv`, repro mínima, causa no código, correção proposta |
| **Regressão** | "mudei X", "testa o PR 42", upgrade de dependência, chamada da `ceo-deps` | só o que o diff alcança, pela escada de `13-regressao-de-pr-e-dependencias.md`; revisão do patch junto |
| **Multiusuário** | dois papéis na mesma tela, "o outro não vê", tempo real | matriz do `map_realtime.py`, um simulador + `phx_actor.mjs` (ou dois simuladores), ordem, reconexão, presença |
| **Estresse** | "estressa", "procura bug", antes de release | tours do `data/tours.csv`, duplo toque, rede ruim (Toxiproxy), background, memória, lista grande, carga (k6) |
| **Evidência** | "analisa esse vídeo", crash do TestFlight | frames do vídeo, crash log symbolicado, passo que dispara, correção |
| **Entrega** | "corrige e sobe", "dá merge depois de revisar", repo próprio | branch, teste na suíte, revisão contra tudo, PR, CI, merge na main na ordem certa (`14-um-chat-dois-repos-e-entrega.md`) |

Na dúvida, o modo menor. "Testa o botão de enviar" é regressão de uma ação, não varredura.

## Plano para aprovar, depois lotes

Rodada que passa de 30 minutos começa com um plano de até 10 linhas no chat: fluxos, casos, oráculos, ferramentas que vai instalar, tempo estimado. O CEO corta ou acrescenta. Só depois a skill abre simulador. A execução vai em lotes de cerca de 45 minutos; cada lote termina com um relatório de até 150 palavras só com o que mudou (bug novo, caso que passou a falhar, o que não rodou). O relatório final consolida. Isso permite rodar com o CEO longe e ainda assim ele delimitar.

Ferramentas que faltam (`which maestro agent-device toxiproxy-cli k6 ffmpeg magick`) entram no plano com o comando de instalação (`curl -fsSL "https://get.maestro.mobile.dev" | bash`, `npm install -g agent-device@latest`, `brew install toxiproxy k6`); aprovado o plano, a skill instala e confere a versão. Nada além do que o plano usa.

## Onde a skill escreve

Tudo que a rodada cria fica **dentro do repo, fora do git**: `.ceo/`, `runs/`, flows novos em `.maestro/ceo/`, testes implementados em `test/ceo/` (ExUnit) e `src/__tests__/ceo/` (Jest/RNTL). Esses caminhos vão em `.git/info/exclude` (ignore local, nunca commitado), então o dono do repo não vê nada e o CEO vê tudo no lugar natural. Em repo próprio, o CEO decide depois o que vira commit. Arquivo do repo alterado temporariamente (ex.: perfil de simulador no `eas.json`) é restaurado no fim da rodada, sempre.

## Primeira pergunta, só se mudar a ação

- Não há servidor rodando nem URL de staging e o fluxo precisa dele: "posso subir o servidor local com `mix phx.server` ou uso staging?"
- Dois papéis, servidor local sem seed e config sem credenciais: "qual login de cada papel?" (uma vez, no chat).
- Mac com 16 GB e o CEO pediu dois simuladores: faça com um simulador e ator por API e diga no relatório; não pergunte.
