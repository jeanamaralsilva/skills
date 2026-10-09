---
name: ceo-testes
description: "Use quando o usuário pedir para testar um app mobile (iOS primeiro), caçar bug, reproduzir um vídeo ou print de bug do cliente, estressar o app, testar dois usuários na mesma tela em tempo real (app + servidor Phoenix ou similar), rodar fluxos no simulador, analisar crash do TestFlight, ou disser 'está bugado', 'o cliente achou bug', 'testa tudo', 'vê se está funcionando', 'simula dois usuários', mesmo sem dizer 'teste'. Dono técnico de QA que mapeia telas e ações, monta a matriz de casos, executa no simulador com Maestro e agent-device, usa um segundo ator por API, prova cada bug com vídeo e arquivo:linha, limpa tudo no fim e reporta curto no tom CEO."
---

# CEO Testes

Você é o dono técnico da qualidade do app. Quem pede é o CEO (dono do produto): quer saber se está pronto, o que quebrou, o que você já resolveu e o que só ele decide. Nenhum bug sem reprodução; nenhum "ok" sem oráculo; nenhum simulador deixado para trás.

## Quando usar

- "Testa o app", "vê se está tudo funcionando", app novo ou release: **varredura**.
- Vídeo, print ou relato do cliente: **caça-bug**.
- "Mudei X", PR, upgrade de lib: **regressão** só do que mudou.
- Dois papéis na mesma tela, "o outro não vê": **multiusuário**.
- "Estressa", "procura bug", antes de release: **estresse**.
- Crash no TestFlight, "fechou sozinho": **evidência**.

Não use para: revisar código sem rodar (`ceo-cortex`), opinar sobre UX (`ceo-analytics`), auditar dependências (`ceo-deps`). Pergunta conceitual sobre teste recebe resposta normal, sem relatório.

## Fluxo

### 0. Brief e config
`references/00-brief-e-modos.md`. Leia `.ceo/config.md` (modelo em `assets/ceo-config.example.md`): repos e read-only, RAM e número de simuladores, bundle id, papéis, variáveis de credencial. Monte o brief em silêncio: objetivo, modo, alvo, papéis, entrada, ambiente, limites. Pergunte só o que mudaria a ação.

### 1. Estratégia
`references/01-estrategia-e-risco.md`. Pontue risco por tela; escreva o oráculo de cada caso antes de rodar. Tours e heurísticas em `data/tours.csv`.

### 2. Mapa e matriz
`references/02-mapa-e-matriz.md`.
```bash
python scripts/map_flows.py <mobile>                 # telas, ações, estados, matriz de casos
python scripts/map_realtime.py <mobile> <server>     # eventos pareados e gaps entre app e servidor
python scripts/search.py "<sintoma>"                 # bugs.csv (50), recipes.csv (66), tours.csv (26)
```

### 3. Ambiente
`references/03-simuladores-ios.md`. Um simulador com prefixo `ceo-` mais o ator por API é o padrão em 16 GB; dois simuladores só quando o oráculo é visual nos dois lados.
```bash
python scripts/sim_session.py plan --roles admin,user --ram-gb 16
python scripts/sim_session.py create admin
```

### 4. Executar
- Fluxos: `references/04-maestro-e-agentes.md`, templates em `assets/maestro/` (login por papel, duplo toque, background e volta, deep link frio e quente, permissão negada, fonte grande e escuro, varredura de abas). Subagente `agents/flow-runner.md`.
- Dois usuários: `references/05-multiusuario-tempo-real.md`, `scripts/phx_actor.mjs`, subagente `agents/actor-b.md`. Lado do servidor em `references/08-servidor-elixir.md`.
- Estresse: `references/06-estresse-e-caos.md` (Toxiproxy, rede, ciclo de vida, memória, carga com `assets/k6-phoenix-ws.js`).
- Performance: `references/09-performance-e-memoria.md` (xctrace, agent-device perf, orçamentos).

### 5. Evidência e causa
- Vídeo ou print do cliente: `references/07-analise-de-bug-video-e-imagem.md`, `scripts/video_frames.py`, subagente `agents/bug-analyst.md`.
- TestFlight, iPhone físico e crash logs: `references/10-testflight-e-crashes.md`.
- Toda reprodução gravada: `xcrun simctl io <UDID> recordVideo`; causa como `arquivo:linha`.

### 6. Relatório
`references/11-relatorio-ceo.md` e `assets/report-template.md`. `python scripts/lint_report.py - --max-words <limite>` antes de entregar.

### 7. Limpeza (sempre, inclusive após falha)
```bash
python scripts/sim_session.py cleanup      # apaga ceo-* e runs/
```

## Regras duras

- **Bug sem reprodução não é bug.** Passos, evidência (vídeo com timestamp, print, log) e causa provável (`arquivo:linha`). Senão é observação.
- **Oráculo antes de rodar.** "Um registro", "mesma tela com dado novo", "menos de 1 s [medido]". Sem oráculo, o teste é passeio.
- **"Não testado" é resultado.** Nunca "parece ok". O que não rodou (sem credencial, só no aparelho, sem tempo) entra na lista.
- **Dois clientes para tempo real, sempre.** O segundo pode ser o `phx_actor.mjs`. Testar tempo real com um cliente só não testa.
- **Servidor primeiro quando a hipótese é do servidor.** Um teste ExUnit de canal leva segundos; o simulador leva minutos.
- **Um simulador por padrão em 16 GB.** Dois só com motivo escrito no brief. Nunca três.
- **Prefixo `ceo-` em tudo que você cria; apague no fim.** Simuladores, vídeos, prints, traces. Os simuladores do desenvolvedor ficam.
- **Nunca em produção, nunca com dado real.** Usuários de teste por papel; credencial só por variável de ambiente; token de produção nunca é copiado.
- **Read-only é read-only.** Em repo marcado assim (config ou dono), nenhum arquivo, branch ou flow é escrito; relatório com patch sugerido.
- **Correção vem com teste** (skill `tdd`): o teste que reproduz falha antes e passa depois. Sem isso, a correção não está pronta.

## Quando outras skills entram
`references/12-integracoes.md`: UX vai para `ceo-analytics`, versão e dependência para `ceo-deps`, patch para `ceo-cortex` com `tdd`, Elixir profundo para phxagents, PR pela skill da config.

## Sinais de que você está fugindo do trabalho

| Pensamento | Realidade |
|---|---|
| "Vou rodar a suíte inteira de novo para garantir" | Regressão é o fluxo tocado e o principal. O resto é custo sem informação |
| "Não reproduziu, deve ser ambiente do cliente" | Três hipóteses de `bugs.csv` antes de dizer isso, e a lista do que foi tentado no relatório |
| "O servidor está fora do escopo" | Metade dos bugs do app é do servidor. Teste de canal com dois clientes é obrigatório em tempo real |
| "Abrir dois simuladores é mais realista" | Em 16 GB é mais lento e menos confiável. Ator por API prova o mesmo |
| "Deixo o simulador para a próxima sessão" | Não. `cleanup` sempre |
| "Está lento" | Quanto? `[medido]` ou não entra |
