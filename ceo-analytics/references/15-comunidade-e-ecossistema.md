# Comunidade e ecossistema

Duas perguntas aparecem em quase toda proposta: "o pessoal gosta disso?" e "dá para construir isso hoje?". Este arquivo responde as duas com o que foi pesquisado em out/2026. Os dados consultáveis estão em `data/ui-libraries.csv`, `data/reference-apps.csv` (39 apps) e `data/market-sources.csv`.

## 1. Voz da comunidade: como usar

- **Reddit está bloqueado** para fetch e para busca restrita ao domínio. Não contorne. Use artigos que citam threads (com o link da thread) e marque como "de segunda mão".
- **Hacker News funciona pela API** (`hn.algolia.com/api/v1/search?query=...&tags=comment`). Cite o `item?id=`.
- **Comentário é sinal qualitativo, não preferência.** Para dizer "o pessoal gosta", use poll com volume, estudo ou reviews de loja em quantidade (AA09).

## 2. O que a comunidade diz (out/2026)

| Tema | Sinal | Fonte |
|---|---|---|
| Liquid Glass | Crítica dominante é legibilidade; poll da Cult of Mac teve 74% gostando. Online a crítica é sobrerrepresentada | cultofmac.com/news/cult-of-mac-readers-love-apple-liquid-glass; nngroup.com/articles/liquid-glass |
| Liquid Glass | Toggle "Tinted" do iOS 26.1 visto como insuficiente; queixas de queda de frame rate e bugs | slashgear.com/2019119; HN item 49795082 |
| Material 3 Expressive | Poll com 7 mil leitores: ~54% a favor; blur e sliders novos são o mais odiado; queixa de visual "infantil" e perda de função | androidauthority.com (poll results e dislike) |
| Visual de IA | Paleta padrão de LLM, cards com ícone em linha própria, radius alto, botão pílula, glow, barra lateral colorida | HN 48440598, 48821350, 47223444; thefountaininstitute.com/blog/signs-vibe-coded-ui |
| Premium | Velocidade percebida (Linear é o exemplo mais citado) | HN 48437609 |
| Irritações | Trial que vira cobrança cara, paywall no primeiro toque, onboarding que ninguém lê, cancelamento escondido, gesto escondido | HN 45396520, 46952714, 42786335; unstar.app (1-star reviews) |
| Loading | Skeleton elogiado por não empurrar o layout; spinner em lista finita criticado | HN 45834949, 48478450 |
| Treino | Migração Strong para Hevy; pedidos: menos toques por série, gráfico de progressão, auto progressão, free tier sem bloquear o básico | HN 49036005, 46371564; gymnoteplus.com/blog/hevy-vs-strong |

Implicação prática: Liquid Glass e M3 Expressive são o padrão de cada plataforma, mas a crítica cai sempre no mesmo lugar (legibilidade, blur, perder função). Use os dois, sem blur gratuito e sem esconder informação que existia.

## 3. Dá para construir hoje? (RN/Expo)

Antes de propor uma lib, confira em `data/ui-libraries.csv` e:

1. **Versão que o SDK fixa** (`data/market-sources.csv` M25). No Expo, instale com `npx expo install`, nunca o latest do npm: o SDK 57 fixa Reanimated 4.5.1, Gesture Handler ~2.32, Skia 2.6.2, FlashList 2.0.2 e Keyboard Controller 1.21.9.
2. **Lib viva:** release recente no npm (M24). Sem release há mais de 12 meses entra como risco na proposta (Restyle, moti, flutter_animate).
3. **Uma lib por função.** Tab bar: Native Tabs do Expo Router ou `react-native-bottom-tabs`. Sheet: TrueSheet (nativo) ou gorhom (custom). Não misture as duas no mesmo app.
4. **Siga o que o repo já usa.** Se o app já tem TrueSheet, a proposta usa TrueSheet.

## 4. Skills externas que complementam esta

Use quando estiverem instaladas. Não copie as regras delas, chame a skill.

| Skill | Para quê | Repo |
|---|---|---|
| emilkowalski/skill (`review-animations`, `animate-expo`) | Revisar e propor motion, sheets e haptics | github.com/emilkowalski/skill |
| expo/skills (`expo-native-ui`, `expo-design-system`) | UI nativa Expo e auditoria de drift do DS | github.com/expo/skills |
| ehmo/platform-design-skills | 450+ regras de HIG, Material 3 e WCAG 2.2 com certo/errado | github.com/ehmo/platform-design-skills |
| callstackincubator/agent-skills (`agent-device`) | QA exploratório no device real | github.com/callstackincubator/agent-skills |
| software-mansion-labs/react-native-skills | Viabilidade de animação e gesto na New Architecture | github.com/software-mansion-labs/react-native-skills |
| twostraws/SwiftUI-Agent-Skill | SwiftUI iOS 26 e acessibilidade | github.com/twostraws/SwiftUI-Agent-Skill |

## 5. Regras de interface que valem sempre (das skills acima)

- Feedback de toque em 100 a 150ms (scale 0.97 ou ripple). Interação até 200ms.
- Troca de tab sem animação de slide. Toggle com efeito imediato.
- Um háptico por ação, no mesmo frame do visual, nunca como único feedback.
- Animar só transform e opacity. Nunca `setState` em handler de gesto ou scroll.
- Números tabulares em timer, carga e tabela.
- Ação destrutiva pede confirmação ou oferece Desfazer. Gesto sempre tem alternativa por toque.
- Botão em loading mantém o rótulo. Erro inline junto do campo.
- Sem área morta entre itens de lista.
