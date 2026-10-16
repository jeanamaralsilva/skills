# Padrões e evidência

Cada afirmação com fonte. Linhas resumidas em `data/patterns.csv`. Os benchmarks de conclusão (Produktly, Chameleon, Userpilot) são de SaaS web e medidos por quem vende ferramenta de tour: use a direção, não o valor, para prometer algo em mobile.

## O que a evidência diz

**Tutorial de cartões no início não ajuda.** Estudo do NN/g com 70 usuários de iPhone: quem leu o tutorial achou as tarefas mais difíceis (SEQ 4,92 contra 5,49, p=0,047); sucesso e tempo sem diferença significativa. https://www.nngroup.com/articles/mobile-tutorials/

**Ajuda puxada vence ajuda empurrada.** Ajuda fora de contexto falha porque a pessoa quer produzir logo e não lembra quando precisa. Dispare por um sinal de que ela precisa agora. Fácil de fechar e de rever, junto do passo, sem explicar convenção. https://www.nngroup.com/articles/onboarding-tutorials/

**Coach mark: uma ação, uma dica por vez.** Bombardear com dicas faz dispensar mais rápido; memória de curto prazo some em cerca de 20 s; deixe claro o que é dica e o que é interativo. https://www.nngroup.com/articles/mobile-instructional-overlay/

**Empty state é a ajuda mais barata.** Três regras: dizer o status (vazio vs carregando), dar a pista ("Marque favoritos para vê-los aqui") e ter o botão da ação dentro do vazio. https://www.nngroup.com/articles/empty-state-interface-design/

**Menos passos, mais conclusão.** Produktly 2026 (88 empresas): 1 a 2 passos 73%, 3 a 5 38%, 6 a 8 25%, 9+ 8%. Iniciado pelo usuário 69% contra 23% automático. https://produktly.com/research/saas-onboarding-benchmarks-2026

**Gatilho e formato importam.** Chameleon (550+ milhões de interações): pico em 4 passos, com 5+ mais da metade abandona; disparo ao carregar 39% contra 47% por clique; indicador de progresso +12%; texto puro 44% contra texto+vídeo 21%; tour aberto a partir de checklist 67%; 38% fecham modal em menos de 4 s. https://www.chameleon.io/benchmark-report

**Checklist completa pouco, mas guia.** Userpilot (188 empresas): conclusão média 19,2%, mediana 10,1%. https://userpilot.com/blog/onboarding-checklist-completion-rate-benchmarks/ (números do trecho indexado, tabela não aberta). Por isso o checklist precisa levar direto à tela da ação, não ser uma lista de leitura.

**Plataformas.** Apple HIG: ensinar fazendo, fluxo obrigatório breve, sempre pulável, não mostrar a quem já usa. https://developer.apple.com/design/human-interface-guidelines/onboarding . Material (M1, a única página oficial que existe sobre o tema): no máximo uma descoberta de recurso por sessão; dispensou, não mostra de novo por um bom tempo; nunca ao abrir o app; em pausas naturais e ao concluir uma ação; nada de recurso avançado para usuário casual. https://m1.material.io/growth-communications/feature-discovery.html

**Mercado.** Duolingo: adiar o cadastro para depois da primeira lição deu cerca de +20% de DAU. https://review.firstround.com/the-tenets-of-a-b-testing-from-duolingos-master-growth-hacker . Notion: página "Getting Started" que é checklist funcional dentro do produto. https://goodux.appcues.com/blog/notions-lightweight-onboarding . Trainerize: guia de configuração interativo com checklist para o treinador novo. https://www.trainerize.com/blog/guide/launch-trainerize-business-steps-success/

**Retenção média de apps** (fonte secundária, só ordem de grandeza): D1 ~25%, D7 ~11 a 13%, D30 ~5 a 7%. https://www.plotline.so/blog/retention-rates-mobile-apps-by-industry . Não há estudo primário que isole "onboarding in-app aumenta retenção em X%". Não prometa esse número.

## Padrões

| Tema | Regra |
|---|---|
| Camadas | Empty state > checklist > dica de 1 passo. |
| Passos | Dica: 1. Mini-tour: até 3, com "1 de 3". |
| Gatilho | Primeira visita à tela certa, depois do conteúdo carregar; ou logo após concluir uma ação ("cadastrou o 1º cliente, agora agende"). |
| Frequência | 1 automática por sessão. Dispensou, não volta. |
| Pular e rever | "Pular dicas" sempre visível; toque fora fecha; "Rever dicas" em Perfil. |
| Alvo | Continua tocável; tocar conta como feito. |
| Checklist | 3 a 5 itens, cada um marcado por dado real, cada um leva à tela da ação. Fechável. Some ao completar. Progresso "2 de 5". |
| Progressive disclosure | Recurso avançado só vira item ou dica depois dos básicos. |
| Texto | 1 frase, verbo + benefício, sem jargão, sem imagem nem vídeo. |
| Acessibilidade | Ver `03`, seção a11y. |

## Exemplo (app de personal trainer)

Personal: checklist de 5 itens (1º aluno, 1ª aula, 1º treino, 1º pacote só depois do 1º aluno, 1ª aula fechada). Dica de 1 passo no "+" da agenda na primeira visita. Aluno: até 3 itens que só aparecem se houver o que fazer (confirmar presença, aceitar contrato, começar treino).
