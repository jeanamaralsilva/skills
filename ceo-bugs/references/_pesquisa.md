# Pesquisa de base: caçar bugs como QA profissional (app RN/Expo + Phoenix)

Digest de pesquisa (10/10/2026). Cada linha = ideia acionável + fonte. "Verificado local" = rodei o comando nesta máquina.

---

## 1. Métodos de teste exploratório profissionais

### 1.1 Postura (Rapid Software Testing)
- Testar ≠ checar: teste é aprender explorando e experimentando; checagem é verificar proposições de forma mecânica. Script/Maestro faz checagem; a IA tem que fazer teste (perguntar, modelar, desconfiar). Fonte: https://www.satisfice.com/blog/archives/856
- Oráculo é heurística falível: "não vi problema" só quer dizer "nenhum oráculo meu apontou". Relate como "possível problema" e diga qual oráculo usou. Fonte: https://developsense.com/resource/Oracles.pdf
- "Problema = diferença entre o percebido e o desejado" (Gause/Weinberg, citado por Bolton): sempre diga desejado por quem. Fonte: https://developsense.com/resource/Oracles.pdf

### 1.2 HTSM / SFDIPOT (o que variar) — James Bach, v6.3
- **Structure**: código, serviços (servidor Phoenix, push, e-mail), arquivos, colateral (texto da loja, termos). Fonte: https://www.satisfice.com/download/heuristic-test-strategy-model
- **Function**: multiusuário/concorrência, cálculo, funções de tempo (timeout, fuso, feriado), segurança, startup/shutdown, tratamento de erro "incluindo todas as mensagens de erro". Fonte: idem
- **Data**: entrada/saída, preset/default, persistente, interdependente, sequência/ordem, cardinalidade (0, 1, muitos, máximo), grande/pequeno, inválido/ruído, ciclo de vida (criar→editar→apagar). Fonte: idem
- **Interfaces**: UI, interfaces de sistema (rede, logs), API, importar/exportar (ex.: contatos da agenda). Fonte: idem
- **Platform**: SO e versão, fontes do sistema, libs embutidas, consumo de memória/bateria. Fonte: idem
- **Operations**: tipos de usuário, ambiente físico (sol, uma mão, academia), uso comum, uso "desfavorecido" (descuidado/malicioso), uso extremo. Fonte: idem
- **Time**: rápido/lento, rajadas, travamentos, concorrência (dois atores no mesmo dado). Fonte: idem
- Critérios de qualidade do HTSM para classificar achado: Capability, Reliability (inclui integridade de dados), Usability (inclui acessibilidade), **Charisma** (estética, "imagem de qualidade" = o "feio" do cliente), Security, Compatibility, Performance. Fonte: idem
- Uso prático: no charter, escolha 2-3 letras do SFDIPOT para variar; travou no meio, percorra as letras atrás de ideias. Fonte: https://tessl.io/registry/testland/sfdpot-exploratory-heuristic

### 1.3 Oráculos FEW HICCUPPS (como reconhecer que é bug)
- **History**: inconsistente com a versão anterior do app (regressão). Fonte: https://developsense.com/resource/Oracles.pdf
- **Image**: inconsistente com a imagem/marca que a empresa quer passar (tela "amadora" é bug por esse oráculo). Fonte: idem
- **Comparable products**: inconsistente com apps comparáveis (concorrente, Agenda do iOS, WhatsApp). Fonte: idem
- **Claims**: inconsistente com o que alguém importante disse (issue, PR, spec, texto da loja, onboarding). Fonte: idem
- **Users' desires/expectations**: inconsistente com o que um usuário razoável quer. Fonte: idem
- **Product**: inconsistente consigo mesmo (botão igual com estilo diferente, termo diferente para a mesma coisa, data em dois formatos). Fonte: idem
- **Purpose**: inconsistente com o propósito explícito ou implícito da função. Fonte: idem
- **Statutes/Standards**: inconsistente com lei ou norma (LGPD, HIG, Material, WCAG). Fonte: idem
- **F/E/W**: Familiar problems (padrão de bug conhecido), Explainability (comportamento que ninguém consegue explicar), World (inconsistente com o mundo real, ex.: aula às 25h). Fonte: https://infinum.com/handbook/qa/testing/heuristics-in-testing
- Quando oráculos se contradizem, o papel do testador não é decidir: é mostrar o conflito. Fonte: https://developsense.com/resource/Oracles.pdf

### 1.4 Tours (Whittaker, Kelly)
- Whittaker (2009), 7 tours canônicos: Feature, Money (todo lugar com dinheiro/preço), Landmark (jornadas-herói), Intellectual (parte mais difícil), Bad-data, Configuration, Garbage-collector (visitar cada tela uma vez só para ver se existe e abre). Fonte: https://tessl.io/registry/testland/exploratory-tours-reference/files/references/tours-catalog.md
- Kelly, FCC CUTS VIDS (reconhecimento de app desconhecido): Feature, Complexity ("5 coisas mais complexas"), Claims, Configuration (o que o app guarda de config), User (5 personas), Testability, Scenario (5 cenários reais), Variability, Interoperability, Data, Structure. Fonte: https://tessl.io/registry/testland/exploratory-testing/files/references/fcc-cuts-vids.md
- Mobile, Kohl "I SLICED UP FUN": Inputs, Store, Location, Interactions/Interruptions, Communication (ligação, SMS no meio), Ergonomics, Data, Usability, Platform, Function, User scenarios, Network (troca de rede). Fonte: https://infinum.com/handbook/qa/testing/heuristics-in-testing

### 1.5 Test Heuristics Cheat Sheet (Hendrickson / Ministry of Testing)
- **Goldilocks**: grande demais, pequeno demais, normal (ex.: campo de valor com googol, negativo e típico). Fonte: https://www.ministryoftesting.com/articles/test-heuristics-cheat-sheet
- **Count 0/1/Many**, **Some/None/All**, **Beginning/Middle/End** (posição em lista e em texto). Fonte: idem
- **CRUD** e **Follow the Data**: criar→ver em outra tela→editar→apagar e conferir que todos os lugares refletem. Fonte: idem
- **Interruptions**: logout, desligar, timeout, cancelar no meio. **Starvation**: sem memória, sem rede, sem disco. Fonte: idem
- **State analysis** (mapear estados e transições) e **Sequences** (inverter ordem, desfazer, combinar). Fonte: idem
- Ataques de dado: datas (timeout, 29/02, dia inválido, horário de verão), números (limites, negativo, decimal, notação científica), strings (longas, acentos, emoji, delimitadores, injeção), violação de regra de domínio e unicidade. Fonte: idem
- API: BINMEN (Boundary, Invalid, NULL, Method, Empty, Negative) e VADER (Verbs, Auth, Data, Errors, Responsiveness) servem para o backend Phoenix. Fonte: idem

### 1.6 Session-Based Test Management
- Sessão = bloco ininterrupto de 60-120 min com **charter** (missão), notas, bugs, perguntas abertas e % de tempo em charter vs. desvio vs. setup. Fonte: https://en.wikipedia.org/wiki/Session-based_testing
- Debrief PROOF: Past, Results, Obstacles, Outlook, Feelings. Para IA: fechar cada sessão com esse resumo. Fonte: https://en.wikipedia.org/wiki/Session-based_testing
- Charter pode mudar no meio da sessão quando surge risco novo; registre a mudança. Fonte: idem

### 1.7 Bug bash
- Time-box de 1-2h, build congelado, foco declarado por área, template único (resumo, passos, esperado x observado, print). Fonte: https://www.browserstack.com/guide/run-bug-bash
- Mostrar antes exemplo de relatório bom vs. ruim; definir áreas prioritárias. Fonte: https://scottberkun.com/2008/how-to-run-a-bug-bash/
- Ganho vem da diversidade de olhares (dev, design, suporte): para IA, simular personas diferentes por rodada. Fonte: https://www.browserstack.com/guide/run-bug-bash

---

## 2. Checklist de bugs comuns em app mobile

### 2.1 Ciclo de vida
- App vai para background ao trocar de app e volta pelo app switcher no mesmo estado; idem bloquear/desbloquear tela. Fonte: https://developer.android.com/docs/quality-guidelines/core-app-quality
- Preservação de estado ao ir para background, rotacionar ou relançar (T-State_Preservation). Fonte: idem
- Rotação rápida/dobra sem quebrar layout nem perder estado; mesmas ações em retrato e paisagem. Fonte: idem
- Simular morte de processo no Android: `adb shell am kill <pacote>` com app em background, depois reabrir. Fonte: https://developer.android.com/topic/libraries/architecture/saving-states
- Opção de dev "Não manter atividades" força destruir activity ao sair (não é igual a morte de processo; teste os dois). Fonte: https://gurubase.io/g/android/use-dont-keep-activities-developer-option-testing
- RN: estados `active`/`background` e, no iOS, `inactive` (central de notificações, ligação, multitarefa). Puxe a central de notificações com um formulário aberto. Fonte: https://reactnative.dev/docs/appstate

### 2.2 Rede
- Perfis Network Link Conditioner: 3G, Edge, LTE, Very Bad Network, 100% Loss; no device iOS 17+: Ajustes → Desenvolvedor. No simulador afeta o Mac inteiro. Fonte: https://www.avanderlee.com/debugging/network-link-conditioner-utility/
- Testar: offline na abertura, cair rede no meio do envio, voltar rede, trocar Wi-Fi↔4G. Fonte: https://infinum.com/handbook/qa/testing/heuristics-in-testing
- Retry de POST sem chave de idempotência cria duplicado (cobrança/aula dupla). Teste: enviar, cortar rede antes da resposta, reenviar; conferir no banco quantos registros nasceram. Fonte: https://docs.stripe.com/api/idempotent_requests
- Startup lento: se passa de 2 s, tem que haver indicador de progresso. Fonte: https://developer.android.com/docs/quality-guidelines/core-app-quality

### 2.3 Datas, fusos, virada do dia
- Brasil aboliu horário de verão em 2019 (quase voltou em 2024): teste dispositivo com tz antiga/sem atualização e fusos BR diferentes (Manaus, Noronha). Fonte: https://en.wikipedia.org/wiki/Daylight_saving_time_in_Brazil
- Falsidades clássicas: dia nem sempre tem 86.400 s, offsets mudam, DST não é sempre 1h nem na mesma data. Fonte: https://zainrizvi.io/blog/falsehoods-programmers-believe-about-time-zones/
- Casos: evento às 23:30 BRT (vira outro dia em UTC), virada de mês/ano, 29/02, semana começando domingo vs. segunda, aparelho em outro fuso. Fonte: https://www.ministryoftesting.com/articles/test-heuristics-cheat-sheet
- Simulador: `xcrun simctl status_bar booted override --time` só muda a barra (para print), não o relógio do app. Verificado local (`xcrun simctl help status_bar`).

### 2.4 Entrada de dados
- Teclado cobrindo o campo/botão: RN `KeyboardAvoidingView` se comporta diferente em iOS e Android; teste o último campo do formulário nos dois. Fonte: https://dev.to/alvessteve/how-does-the-behavior-property-of-the-keyboardavoidingview-component-works--4bg6
- Strings: muito longa, acentos, emoji, colar texto com quebra de linha/espaço no fim, só espaços. Fonte: https://www.ministryoftesting.com/articles/test-heuristics-cheat-sheet
- Números: 0, negativo, decimal com vírgula e com ponto, limite, colar "R$ 1.234,50". Fonte: idem
- Máscaras BR (telefone com/sem 9, CPF com/sem pontuação, moeda): colar valor formatado, apagar do meio, autofill do iOS. Regra de domínio (dígito verificador) = "domain rule violation". Fonte: idem
- Unicidade: cadastrar o mesmo e-mail/aluno duas vezes. Fonte: idem

### 2.5 Listas
- 0, 1, muitos itens; primeiro/meio/último; scroll até o fim (paginação, item duplicado ou faltando na emenda). Fonte: https://www.ministryoftesting.com/articles/test-heuristics-cheat-sheet
- Estado vazio tem que dizer o status (carregando? erro? filtro errado?) e dar caminho para a ação principal. Fonte: https://www.nngroup.com/articles/empty-state-interface-design/
- Pull to refresh com rede ruim; item criado em outra tela aparece sem precisar matar o app (Follow the Data). Fonte: https://www.ministryoftesting.com/articles/test-heuristics-cheat-sheet

### 2.6 Duplo toque / submit duplicado
- Botão precisa dar feedback imediato e estado de loading; sem isso o usuário toca de novo. Teste: dois toques rápidos em "Salvar", "Pagar", "Agendar". Fonte: https://www.nngroup.com/articles/button-states-communicate-interaction/
- Conferir no backend: duplicata é bug mesmo que a UI mostre só um. Fonte: https://docs.stripe.com/api/idempotent_requests

### 2.7 Navegação
- Botão e gesto de voltar do Android funcionam em toda tela (T-Back_Nav). Fonte: https://developer.android.com/docs/quality-guidelines/core-app-quality
- Deep link frio e quente: `npx uri-scheme open <scheme>://rota --ios|--android`; também sem login e com login de outro papel. Fonte: https://docs.expo.dev/linking/into-your-app/
- Play pre-launch report: o robô abre até 3 deep links e navega 30 s em cada; bom modelo para "garbage collector tour". Fonte: https://support.google.com/googleplay/android-developer/answer/9842757?hl=en

### 2.8 Permissões
- Pedir permissão só quando a função é usada, explicar o porquê, e o app continuar funcionando se negar ou revogar depois. Fonte: https://developer.android.com/docs/quality-guidelines/core-app-quality
- iOS simulador: `xcrun simctl privacy booted grant|revoke|reset <serviço> <bundle>` (contacts, location, photos, microphone...); revogar pode matar o app. Verificado local (`xcrun simctl help privacy`).

### 2.9 Notificações push
- Simulador iOS: `xcrun simctl push booted <bundle> payload.json`. Verificado local. Expo tem ferramenta web de envio de teste com o ExpoPushToken. Fonte: https://docs.expo.dev/push-notifications/push-notifications-setup/
- Testar: app aberto, em background, morto; tocar na notificação leva à tela certa; permissão negada; texto com acento/emoji truncado. Fonte: https://developer.android.com/docs/quality-guidelines/core-app-quality

### 2.10 Acessibilidade
- Alvo de toque: iOS ≥ 44x44 pt. Fonte: https://developer.apple.com/design/human-interface-guidelines/accessibility
- Android/Material: ≥ 48x48 dp, com ~8 dp entre alvos. Fonte: https://support.google.com/accessibility/android/answer/7101858?hl=en
- Contraste texto ≥ 4,5:1 (texto grande ≥ 3:1). Fonte: https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html
- Dynamic Type no simulador: `xcrun simctl ui booted content_size accessibility-extra-extra-extra-large`; também `increase_contrast enabled`. Verificado local (`xcrun simctl help ui`).
- RN: `allowFontScaling`/`maxFontSizeMultiplier` em Text/TextInput; confira se alguém desligou escala ou se texto grande corta. Fonte: https://reactnative.dev/docs/text
- Accessibility Inspector (Xcode) audita texto cortado, label faltando e contraste; `performAccessibilityAudit` faz o mesmo em teste. Fonte: https://developer.apple.com/videos/play/wwdc2023/10035/
- Android Accessibility Scanner aponta alvo < 48dp, contraste < 3,0 e texto cortado com fonte grande. Fonte: https://support.google.com/accessibility/android/faq/6376582?hl=en
- Erro só por cor (campo vermelho sem texto) é falha: precisa de indicadores redundantes. Fonte: https://www.nngroup.com/articles/error-messages-scoring-rubric/

### 2.11 Modo escuro, telas e Android
- Todo conteúdo legível em claro e escuro (T-Theme_Support). Simulador: `xcrun simctl ui booted appearance dark`. Fontes: https://developer.android.com/docs/quality-guidelines/core-app-quality ; verificado local.
- Telas pequenas: 375x667 pt (classe iPhone 6/7/8, mesma do SE 2ª/3ª ger.) e 320x568 pt (SE 1ª ger.). Fonte: https://developer.apple.com/library/archive/documentation/DeviceInformation/Reference/iOSDeviceCompatibility/Displays/Displays.html
- Safe area: conteúdo não pode ficar sob notch/Dynamic Island/home indicator; listas roláveis vão até a borda de baixo. Fonte: https://developer.apple.com/documentation/uikit/positioning-content-relative-to-the-safe-area
- Android 15 + targetSdk 35: edge-to-edge obrigatório; checar botão/conteúdo atrás da status bar e da barra de navegação (gesto e 3 botões). Fonte: https://developer.android.com/about/versions/15/behavior-changes-15
- Performance: frame ≤ 16 ms, sem ANR/travamento. Fonte: https://developer.android.com/docs/quality-guidelines/core-app-quality

---

## 3. Polimento visual: "o cliente acha feio"

### 3.1 Por que conta como bug
- Charisma/Image do HTSM: "o produto projeta a impressão de qualidade desejada" é critério de qualidade, não frescura. Fonte: https://www.satisfice.com/download/heuristic-test-strategy-model
- Oráculo Product: inconsistência interna (dois estilos para o mesmo componente) é bug mesmo sem spec. Fonte: https://developsense.com/resource/Oracles.pdf

### 3.2 Inspeção visual tela a tela
- Checklist de design QA: cores, tipografia, espaçamento, tamanhos, raio de borda, sombras, ícones, imagens; layout: grid/alinhamento, reflow, overflow/clipping. Fonte: https://claudeskills.info/skills/Owl-Listener/designer-skills/design-qa-checklist/
- Truncamento conforme especificado e conteúdo real (nome longo, valor grande) cabendo no layout. Fonte: idem
- Margens iOS: 16 pt em largura compacta; conteúdo alinhado à margem dos botões da nav bar. Fonte: https://developer.apple.com/documentation/uikit/positioning-content-relative-to-the-safe-area
- Classes de defeito de display mais comuns (pesquisa OwlEye): sobreposição de texto, tela borrada, imagem faltando, componente cortado. Fonte: https://arxiv.org/abs/2009.01417v2
- Layout shift: elemento que pula de lugar quando algo carrega (imagem sem tamanho, fonte, item inserido acima) faz tocar no botão errado. Mudança logo após toque do usuário é aceitável. Fonte: https://web.dev/articles/cls
- Loading: skeleton para carga de tela < 10 s; spinner para 2-10 s; > 10 s barra de progresso. Tela branca seguida de "pop" de conteúdo é defeito. Fonte: https://www.nngroup.com/articles/skeleton-screens/
- Estado vazio pobre ("Nenhum item") sem explicar e sem CTA. Fonte: https://www.nngroup.com/articles/empty-state-interface-design/

### 3.3 Mensagens de erro
- Mensagem perto da origem, legível, sem jargão técnico ("Error 500", "undefined", "changeset invalid" são bugs), descrevendo o problema exato e como resolver, sem culpar o usuário. Fonte: https://www.nngroup.com/articles/error-message-guidelines/
- Preservar o que o usuário digitou após erro; não mostrar erro antes de ele terminar de digitar. Fonte: https://www.nngroup.com/articles/error-messages-scoring-rubric/

### 3.4 Texto e localização pt-BR
- Capitalização consistente: Material manda sentence case em tudo (títulos, botões, abas); o importante no app é escolher um padrão e não misturar. Fontes: https://m3.material.io/foundations/content-design/style-guide ; https://developer.apple.com/videos/play/wwdc2022/10037/
- Plural: usar `Intl.PluralRules`; atenção que em pt-BR o CLDR classifica **0 e 1 como "one"** (então "0 aula" sai se o código confiar só na regra; decida o texto do zero à parte). Fonte: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/PluralRules ; verificado local (Node: 0→one, 1→one, 2→other).
- "1 aulas", "1 alunos" = plural feito com `n + " aulas"`: grep por template literal com número + substantivo no plural. Fonte: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/PluralRules
- Moeda: `Intl.NumberFormat("pt-BR",{style:"currency",currency:"BRL"})` dá "R$ 1.234,50" com **espaço não separável (U+00A0)** depois de R$; comparação de texto em teste falha se usar espaço comum. Fonte: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/NumberFormat/NumberFormat ; verificado local.
- Sinais de bug de texto: inglês no meio do português (labels de lib, "Cancel", "Loading...", data "Oct"), ponto decimal, data MM/DD, "e.g."/"etc." em botões. Fonte: https://m3.material.io/foundations/content-design/global-writing/word-choice
- Abreviações dificultam leitura e leitor de tela: preferir palavra por extenso. Fonte: https://m3.material.io/foundations/content-design/style-guide

### 3.5 Teclado, safe area, barras
- Botão primário escondido pelo teclado, conteúdo sob notch, status bar ilegível no tema escuro, conteúdo atrás da barra de navegação Android. Fontes: https://developer.apple.com/documentation/uikit/positioning-content-relative-to-the-safe-area ; https://developer.android.com/develop/ui/views/layout/edge-to-edge
- Print limpo e comparável entre rodadas: fixar status bar (`simctl status_bar booted override --time 9:41 --batteryLevel 100`). Verificado local (`xcrun simctl help status_bar`).

---

## 4. Relatório de bug bom e severidade

### 4.1 Estrutura
- Passos mínimos e precisos (incluindo setup), Esperado, Observado, cada um simples. Fonte: https://developer.mozilla.org/en-US/docs/Mozilla/QA/Bug_writing_guidelines
- RIMGEA (Kaner): Replicar, Isolar (menos passos), Maximizar (pior consequência), Generalizar (onde mais acontece), Externalizar (quem é afetado), dizer de forma clara e neutra. Fonte: https://spin.atomicobject.com/rimgea-testing-mnemonic/
- Template de bug bash: resumo, passos, esperado x observado, screenshot. Fonte: https://www.browserstack.com/guide/run-bug-bash
- Evidência para IA: vídeo/print do passo que falha + dispositivo/OS + build + conta usada + arquivo:linha suspeito separado como hipótese. Fonte: https://developer.mozilla.org/en-US/docs/Mozilla/QA/Bug_writing_guidelines
- Diga qual oráculo indicou o problema (Claims, Product, Comparable...); se for opinião, marque como "pergunta", não "bug". Fonte: https://developsense.com/resource/Oracles.pdf

### 4.2 Severidade x prioridade
- Severidade = grau de impacto do defeito; prioridade = importância de negócio/urgência. Eixos independentes (logo errado: baixa severidade, alta prioridade). Fonte: https://contextqa.com/blog/difference-between-severity-and-priority/
- Escala Mozilla: S1 catastrófico (bloqueia, perda de dados, >25% usuários, sem contorno); S2 sério (função principal comprometida, sem contorno satisfatório); S3 normal (função não crítica ou com contorno); S4 trivial/cosmético. Fonte: https://wiki.mozilla.org/BMO/UserGuide/BugFields
- Exemplos S1 do Firefox: crash com perda de dados, função central fora para todos; S2: problema que faria o usuário trocar de produto. Fonte: https://firefox-source-docs.mozilla.org/bug-mgmt/guides/severity.html
- Em Mozilla, severidade é definida na triagem, não por quem reporta: a IA propõe severidade e justifica; quem decide é o dono. Fonte: https://wiki.mozilla.org/BMO/UserGuide/BugFields
- Polimento visual costuma ser S4 em severidade, mas pode ser prioridade alta se o cliente vê em toda tela (oráculo Image). Fonte: https://contextqa.com/blog/difference-between-severity-and-priority/

---

## 5. IA e automação em teste exploratório mobile

### 5.1 Ferramentas
- Android Monkey: eventos pseudoaleatórios repetíveis (seed), restrito a um pacote; para em crash e ANR. Bom para estresse, cego para bug visual/lógico. Fonte: https://developer.android.com/tools/help/monkey
- Maestro: YAML, espera automática e tolerância a flakiness embutidas (sem `sleep`). Fonte: https://maestro.mobile.dev
- Maestro `assertNoDefectsWithAI`: manda print a um LLM para achar texto/elemento cortado, sobreposto ou descentralizado; experimental, `optional: true` por padrão para não quebrar CI. Fonte: https://docs.maestro.dev/reference/commands-available/assertnodefectswithai
- Maestro `assertWithAI`: asserção em linguagem natural sobre o print; também experimental. Fonte: https://docs.maestro.dev/reference/commands-available/assertwithai
- Play pre-launch report: robô navega o app, roda Accessibility Test Framework e gera prints por problema. Fonte: https://support.google.com/googleplay/android-developer/answer/9844487?hl=en

### 5.2 O que a pesquisa diz sobre agentes LLM
- GPTDroid (GUI testing como Q&A com LLM): 71% de cobertura de activities, 36% mais bugs que baseline; 48 bugs novos no Google Play. Fonte: https://arxiv.org/pdf/2305.09434
- DroidAgent: agente com memória que cria objetivos de tarefa realistas (317/374 realistas), 61% de cobertura vs. 51%. Fonte: https://arxiv.org/pdf/2311.08649
- Ferramentas automáticas sem oráculo só pegam crash; bugs funcionais sem crash exigem oráculo (VisionDroid: Explorer + Monitor + Detector com MLLM sobre histórico segmentado por lógica). Fonte: https://arxiv.org/abs/2407.03037v1
- Estudo com MLLM em 71 bugs não-crash: ~49% de detecção. Ou seja, metade passa: IA complementa, não substitui. Fonte: https://arxiv.org/abs/2407.19053v1
- Detector visual dedicado (OwlEye) chegou a 85% precisão / 84% recall em defeitos de display; Nighthawk 0,84/0,84. Fontes: https://arxiv.org/abs/2009.01417v2 ; https://deepai.org/publication/nighthawk-fully-automated-localizing-ui-display-issues-via-visual-understanding
- Limites relatados de LLM em teste: degradação, aleatoriedade e falso positivo. Fonte: https://arxiv.org/pdf/2307.07221

### 5.3 Evitar falso positivo (regras práticas)
- Alucinação típica: LLM afirma estado que não está na tela (ícone "habilitado" que está desabilitado) ou bug de passo que nunca executou. Regra: só reportar com print/vídeo do momento e passos que foram de fato executados. Fonte: https://arxiv.org/abs/2407.19053v1
- Reproduzir antes de reportar (Replicate do RIMGEA); bug que não reproduz vai como "observação intermitente" com frequência (ex.: 1 em 5). Fonte: https://spin.atomicobject.com/rimgea-testing-mnemonic/
- Separar flakiness do teste de bug do app: timing absoluto/relativo, estado global compartilhado, ambiente sujo (outro testando no mesmo servidor). Fonte: https://testing.googleblog.com/2017/04/where-do-our-flaky-tests-come-from.html
- Teste E2E maior = mais flaky; isole o passo mínimo antes de concluir que é bug. Fonte: https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html
- Asserção visual por IA como sinal, não veredito: mantenha `optional` e confirme olhando o print. Fonte: https://docs.maestro.dev/reference/commands-available/assertnodefectswithai
- "Não vi bug" não prova ausência: relatório final lista o que foi coberto e o que não foi. Fonte: https://developsense.com/resource/Oracles.pdf
- Confirmar efeito no backend (registro duplicado, status) em vez de confiar só na UI: Follow the Data. Fonte: https://www.ministryoftesting.com/articles/test-heuristics-cheat-sheet
- Divergência de opinião (é bug ou é feature?) vira pergunta ao dono, não bug: oráculos diferentes, ninguém está errado. Fonte: https://developsense.com/resource/Oracles.pdf

### 5.4 Receita de sessão para o agente (síntese das fontes acima)
- 1) Recon com FCC CUTS VIDS/garbage collector: abrir toda tela uma vez, print de cada. 2) Charter por risco (SFDIPOT). 3) Sessão time-boxed com notas. 4) Cada suspeita passa por um oráculo FEW HICCUPPS nomeado. 5) RIMGEA antes de reportar. 6) Severidade proposta S1-S4. 7) Debrief PROOF com cobertura e lacunas. Fontes: https://en.wikipedia.org/wiki/Session-based_testing ; https://developsense.com/resource/Oracles.pdf ; https://spin.atomicobject.com/rimgea-testing-mnemonic/
