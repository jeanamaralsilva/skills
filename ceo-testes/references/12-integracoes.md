# Integrações: quem faz o quê

`ceo-testes` acha e prova o bug. As outras skills e ferramentas fazem o resto. Chame no momento certo; não copie as regras delas para cá.

| Situação | Chamar | Por quê |
|---|---|---|
| Bug é de UX, não de código (fluxo confuso, estado faltando, botão escondido) | `ceo-analytics` | diagnóstico de tela e proposta; `map_routes.py` dela complementa o `map_flows.py` |
| Bug é de versão: módulo nativo duplicado, lib fora do SDK, CVE, build quebrando | `ceo-deps` | `expo_check.py`, `lock_audit.py`; e a `ceo-deps` chama esta skill (modo regressão) depois de mudar dependência nativa ou central (`13`) |
| PR aberto: "o que pode quebrar?" | esta skill (`13`) + `ceo-cortex` | regressão do que o diff alcança e revisão do patch num relatório só |
| Corrigir o bug no código (modo manter) | `ceo-cortex` | revisão sênior do patch; evita corrigir o sintoma |
| Escrever o teste da correção | skill `tdd` | red-green-refactor: o teste que reproduz o bug falha antes e passa depois; sem isso a correção não está pronta |
| Elixir/Phoenix a fundo (canal, Ecto, OTP) | plugin phxagents (`/phx:audit`, Iron Laws) | referência de arquitetura; os testes do servidor aqui são o mínimo |
| Abrir PR com a correção e a evidência | skill de PR da config (`fluxo.pr_skill`) ou `gh pr create` | vídeo antes/depois no corpo |
| QA exploratório por agente | `dogfood` (Callstack) + `data/tours.csv` | roteiro de exploração com agent-device |
| Tela web do produto | Claude in Chrome / agent-browser | mesmo processo, outro alvo |

## Ordem típica de um bug reportado pelo cliente

1. `ceo-testes` `07`: vídeo → frames → hipótese (`bugs.csv`) → reprodução mínima → causa (`arquivo:linha`).
2. `tdd`: teste que falha reproduzindo o bug (ExUnit no servidor, Jest/RNTL no app, ou flow Maestro na suíte).
3. `ceo-cortex`: correção revisada.
4. `ceo-testes` regressão: o flow tocado e o fluxo principal passam; teste novo verde.
5. PR com vídeo antes/depois.
6. `ceo-testes` limpeza.

Em repo read-only, para no passo 1 com patch sugerido e teste proposto no relatório.

## Ordem típica de uma varredura antes de release

1. `ceo-deps` auditar (5 min): nada de CVE P0 ou duplicata nativa que invalide o build.
2. `ceo-testes` varredura: mapa, matriz, fluxo principal, caminhos tristes das telas de maior risco, multiusuário, estresse curto (after-hours, saboteur, fonte grande).
3. `ceo-analytics` só nos achados de UX que a varredura levantou.
4. Relatório único: veredito "pronto" ou lista de bloqueios.

## Skills da comunidade que valem instalar

| Skill | O que dá | Onde |
|---|---|---|
| `tdd` (superpowers e variantes) | disciplina red-green-refactor, anti-padrão de testar implementação | https://github.com/obra/superpowers |
| `dogfood` (Callstack) | QA exploratório por agente no simulador | `npx skills add https://github.com/callstackincubator/agent-device --skill dogfood` |
| Maestro MCP | agente inspeciona a tela e roda YAML inline | `claude mcp add maestro -- maestro mcp` |
| argent | dev build com MCP para logs, rede e profiling | `npx @swmansion/argent init` |
| swift-ios-skills `ios-simulator` | referência de `simctl` | https://tessl.io/registry/dpearson2699/swift-ios-skills |

Instale o que o projeto usa; a skill não exige nenhuma delas para o fluxo básico (simctl + Maestro + scripts).
