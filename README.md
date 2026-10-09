# CEO skills

Quatro skills para o Claude (Cowork, Claude Code e qualquer agente que leia `SKILL.md`) que cuidam de um app mobile com servidor como um dono técnico cuidaria: UX, dependências, código e testes. Cada uma reporta curto, no tom de quem responde ao CEO: o que está bom, o que quebrou, o que já foi resolvido e o que só o dono decide. Sem narrar processo, sem inventar resultado, sem esconder erro ou risco de segurança.

Nenhuma skill depende de um projeto específico. O que varia por projeto (repos, read-only, limites da máquina, design system, papéis de teste, credenciais por variável de ambiente) vai em `.ceo/config.md` na raiz do repo. Modelo em qualquer `*/assets/ceo-config.example.md`.

| Skill | Pergunta que responde | Tamanho |
|---|---|---|
| [ceo-analytics](ceo-analytics/) | O app está bom de usar? O que propor? Como fica a animação no iOS e no Android? | 19 guias, 7 CSVs (heurísticas, anti-padrões, componentes, 39 apps de referência, fontes de mercado, libs de UI, 45 padrões de motion), 4 scripts |
| [ceo-deps](ceo-deps/) | As dependências estão seguras, compatíveis e mantidas? | 14 guias, 105 checks com fonte em 12 ecossistemas, 31 licenças, incidentes reais, 6 scripts |
| [ceo-cortex](ceo-cortex/) | O código está certo, limpo e sem repetição? | guias por linguagem (Elixir com as Iron Laws do phxagents, RN, TS/Node, Python, Go, Kotlin, Swift, Java, SQL), memória entre sessões, detector de duplicação |
| [ceo-testes](ceo-testes/) | O app funciona de verdade, com dois usuários, sem rede, depois do background? Onde está o bug do vídeo que o cliente mandou? | 13 guias, 50 bugs reproduzíveis, 66 receitas de comando, 26 tours, 5 scripts, 7 flows Maestro |

## ceo-analytics

Designer de produto sênior em forma de agente. Recebe um app (código, app rodando ou design no Pencil/Figma) e entrega:

- **Mapa do app:** telas, abas e fluxos, com o objetivo de cada tela e o que cada botão faz.
- **Diagnóstico de UI/UX:** heurísticas de Nielsen e Laws of UX. Cada achado tem severidade de P0 a P3 e evidência com `arquivo:linha`.
- **Benchmark de mercado:** só fontes gratuitas, testadas uma a uma, e o que os usuários elogiam nas reviews.
- **Propostas de tela:** 2 ou 3 hipóteses, com todos os estados (loading, vazio, erro, offline, sucesso). iOS 26 com Liquid Glass só na navegação e Android com Material 3 Expressive.
- **Motion e micro-interações:** ícone de aba que pulsa, gradiente lento atrás do ícone, sheet que acompanha o dedo, transições; com API por plataforma, duração, Reduce Motion e custo no Android.
- **Fluxo no Pencil:** pontos de toque numerados e setas até a tela de destino.

## ceo-deps

Dono técnico das dependências de um app inteiro, em um ou vários repos (ex.: mobile Expo + server Phoenix):

- **Inventário multi-repo:** gerenciadores, lockfiles (inclusive os ignorados pelo git), toolchain, deps por git, overrides, bots, CI e risco de OTA (`runtimeVersion`).
- **Segurança e supply chain:** audit de cada ecossistema, versões exatas do lock contra o OSV e defesas contra pacote malicioso (cooldown, `--ignore-scripts`, Actions fixadas por SHA).
- **Versões e compatibilidade:** Expo SDK (`bundledNativeModules.json`), duplicata de módulo nativo, regressão de Hermes e matriz Elixir/OTP.
- **Duplicadas e sem uso, licenças (SaaS e lojas), acoplamento, serviços externos e ciclo de vida.**
- **Manter:** aplica o que é seguro em branch e verifica em degraus, com o build nativo na nuvem (EAS) e no CI quando a máquina não aguenta.

## ceo-cortex

Revisão e escrita de código no nível de engenheiro sênior, com memória entre sessões (`cortex`), detector de duplicação e mapa de símbolos. Guias de armadilhas por linguagem. Antes se chamava code-cortex.

## ceo-testes

QA de app mobile (iOS primeiro) que acha e prova bug:

- **Mapa e matriz:** `map_flows.py` lista telas, botões e estados e expande cada ação em feliz, triste, duplo toque, sem rede, background no meio, deep link frio. `map_realtime.py` pareia os eventos do servidor Phoenix com os listeners do app e aponta os gaps.
- **Dois usuários de verdade:** um simulador mais `phx_actor.mjs` (cliente Phoenix Channels sem dependências) como segundo papel. Dois simuladores só quando precisa.
- **Estresse:** Toxiproxy (latência, timeout, reset), ciclo de vida, permissões, fonte grande, memória, carga com k6.
- **Evidência:** `video_frames.py` corta o vídeo do cliente nas mudanças de cena; TestFlight feedback e crash logs pela API do App Store Connect; xctrace para hitches.
- **Limpeza:** tudo que a sessão cria tem prefixo `ceo-` e é apagado no fim (`sim_session.py cleanup`).
- **Servidor:** testes ExUnit de canal com dois clientes, corridas, jobs e propriedades antes de abrir simulador.

## Instalar

Copie a pasta da skill para `~/.claude/skills/` (ou crie um link: `ln -s <este repo>/<skill> ~/.claude/skills/<skill>`), ou instale o `.skill` pelo app do Claude. Depois, no seu projeto, copie `ceo-testes/assets/ceo-config.example.md` para `.ceo/config.md` e preencha o que souber.

## Testar

```bash
for s in ceo-analytics ceo-deps ceo-cortex ceo-testes; do (cd $s/scripts && python3 -m pytest tests -q); done
```

## Contribuir

Cada linha de dado (`data/*.csv`) tem uma coluna `source` com a URL. Achado sem fonte não entra. Scripts têm teste. Nome de projeto, pessoa ou empresa não entra nas skills: o que é seu vai em `.ceo/config.md`.
