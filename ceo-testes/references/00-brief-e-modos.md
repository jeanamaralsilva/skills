# Brief, config e modos

Antes de abrir um simulador, monte o brief em silêncio. Ele não entra na resposta.

## Config

Ordem: `.ceo/config.md` na raiz do repo, depois `~/.ceo/profile.md`, depois perguntas. Modelo em `assets/ceo-config.example.md`. O que esta skill lê:

| Campo | Para quê | Sem ele |
|---|---|---|
| `repos[]` com `papel` e `read_only` | onde está o app, onde está o servidor, onde pode escrever | procura `app/` ou `src/app/` (mobile) e `mix.exs`/`package.json` com `phoenix`/`socket.io` (servidor); trata tudo como read-only |
| `maquina.ram_gb`, `simuladores_max` | quantos simuladores sobem juntos | assume 16 GB: 1 simulador + ator por API |
| `maquina.apagar_testes_ao_fim` | limpeza no fim | sempre apaga o que criou |
| `plataformas` | iOS, Android ou ambos | iOS |
| `testes.bundle_id`, `deeplink_scheme` | `simctl launch`, `openurl`, Maestro `appId` | lê `app.json`/`app.config.*` (`ios.bundleIdentifier`, `scheme`) |
| `testes.servidor_ws`, `papeis`, `credenciais` | segundo ator, login por papel | pergunta o endpoint; credenciais só por variável de ambiente |
| `testes.maestro_dir` | onde ficam os flows do time | `.maestro/` |

Credencial nunca vai para arquivo, print ou relatório. Se a config pede `TEST_USER_ADMIN` e a variável não existe, diga isso e pare o fluxo que depende dela.

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
| **Regressão** | "mudei X", PR, upgrade de dependência | só os fluxos que tocam a mudança (via `map_flows.py --screen` e `git diff --name-only`), baseline visual antes e depois |
| **Multiusuário** | dois papéis na mesma tela, "o outro não vê", tempo real | matriz do `map_realtime.py`, um simulador + `phx_actor.mjs` (ou dois simuladores), ordem, reconexão, presença |
| **Estresse** | "estressa", "procura bug", antes de release | tours do `data/tours.csv`, duplo toque, rede ruim (Toxiproxy), background, memória, lista grande, carga (k6) |
| **Evidência** | "analisa esse vídeo", crash do TestFlight | frames do vídeo, crash log symbolicado, passo que dispara, correção |

Na dúvida, o modo menor. "Testa o botão de enviar" é regressão de uma ação, não varredura.

## Primeira pergunta, só se mudar a ação

- Não há servidor rodando nem URL de staging e o fluxo precisa dele: "posso subir o servidor local com `mix phx.server` ou uso staging?"
- Dois papéis e a config não diz as credenciais: "qual variável tem o login de cada papel?"
- Mac com 16 GB e o CEO pediu dois simuladores: faça com um simulador e ator por API e diga no relatório; não pergunte.
