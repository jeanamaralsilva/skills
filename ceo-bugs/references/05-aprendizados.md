# 05. Aprendizados (atualize ao fim de toda rodada)

Formato: `- [data] padrão → onde procurar da próxima vez (evidência)`.

## Onde este app costuma quebrar
- [2026-10-10] Dado de vínculo errado: tela do aluno somando aulas/pacote de outro personal ou de outro vínculo → toda tela que agrega por aluno sem filtrar pelo vínculo.
- [2026-10-10] Ação permitida em estado que não deveria: confirmar aula cancelada ou já passada → todo botão de ação que depende de status e hora; teste com aula passada, cancelada e remarcada.
- [2026-10-10] Voltar para o lugar errado em tela escondida de aba (`href: null`) → todo push entre abas; o voltar precisa saber de onde veio.
- [2026-10-10] Dado velho depois de aceitar algo ou voltar do background → invalidação de cache após mutação e foco do app.
- [2026-10-10] Retomada de cadastro: tela inicial calculada por campos diferentes dos que o servidor exige → compare a regra de "perfil completo" do servidor com a do app.
- [2026-10-10] Overlay/balão com altura reservada fixa quebra com fonte máxima → todo Modal, sheet e tooltip com fonte máxima.
- [2026-10-10] Renovação/recorrência duplicando ou truncando registros → todo job que gera N itens: rodar duas vezes e com N grande.

- [2026-10-10] Contrato app x servidor divergente: o app valida a resposta com zod e o servidor manda outro formato (ex. `data.trainer` aninhado) → a tela mostra "não encontrado" para sempre. Rode os schemas zod do app contra a resposta real de cada GET (achou "Personal não encontrado" no perfil do personal visto pelo aluno).
- [2026-10-10] 500 por falta de validação no changeset: texto > 255, `null` explícito em coluna NOT NULL, tipo errado (string onde é lista), número que estoura a coluna → toda rota de escrita com BINMEN; o app mostra erro genérico.
- [2026-10-10] Erro de carga desenhado como estado vazio ("Nenhum contrato") → toda tela com query sem ramo `isError`; o usuário acha que perdeu dado.
- [2026-10-10] Dinheiro com `toFixed` em telas antigas convivendo com formatador pt-BR nas novas → `scripts/ugly_scan.py` regra money-tofixed.
- [2026-10-10] Mapa de tradução de erro do servidor sensível a maiúsculas ("Internal Server Error" do Phoenix escapa) → compare sem caixa.

- [2026-10-10] Dado velho na tela do outro papel: personal edita, aluno vê o valor antigo e aceita (cache de 5 min sem refetch em foco) → toda tela onde um papel decide sobre algo que o outro edita (contrato, aula, cobrança): edite por API e abra no app sem matar.
- [2026-10-10] Ação de domínio fora do tempo: fechar aula futura conta como realizada e desconta saldo → toda transição de status ligada a horário (iniciar, fechar, falta, confirmar) com aula de amanhã.
- [2026-10-10] Mensagem de validação do zod em inglês ("Too small: expected number…") → todo schema de formulário com min/max sem mensagem; teste com 0 e vazio.
- [2026-10-10] Fonte máxima quebra listas (nome some), cabeçalho com ícones (sai da tela), botões de altura fixa e iniciais de avatar → rode o garbage-collector inteiro uma segunda vez com content_size no máximo; é onde mais rende bug visual.
- [2026-10-10] Correção de "voltar" com navigate para a origem deixa a tela na pilha da outra aba → ao corrigir navegação entre abas, toque na aba de onde a tela foi emprestada depois de voltar.
- [2026-10-10] Unicidade só no app: mesmo aluno/e-mail duas vezes, com caixa diferente → crie duplicado por API com maiúsculas.

- [2026-10-10] Edição concorrente: personal muda o treino com o aluno no meio dele; o app do aluno trava em erro do servidor ("exercício não faz parte do treino") → todo fluxo longo do aluno (treino, contrato) com o ator B editando por API no meio.
- [2026-10-10] Histórico reescrito: sessão antiga mostra nome e exercícios atuais do treino (servidor não guarda cópia) → todo histórico que referencia entidade editável: edite a entidade e abra o histórico.
- [2026-10-10] Mesmo estado com rótulo diferente em cada tela (Confirmada/Agendada/Pendente) → para cada status, visite Home, Agenda, detalhe e lista e compare o texto.
- [2026-10-10] Regra só no app (confirmar aula passada, janela de 48h) → toda regra de UI: tente pela API.

- [2026-10-10] Erro em dobro: o hook faz toast com a mensagem do servidor e a tela ainda abre um Alert genérico "Tente novamente" → todo catch depois de mutateAsync; provoque um 422 e conte os avisos.
- [2026-10-10] Aceite sem versão: a tela aberta guarda o valor antigo e o servidor aceita o atual → todo botão de aceite/pagamento: o ator B muda o valor com a tela aberta e a caixa marcada.

- [2026-10-11] Tour guiado/spotlight: alvo no header nativo sai cortado; alvo atrás da tab bar destaca a barra; alvo repetido na tela anterior faz o guia pular etapas; re-registro do alvo ao fim da transição da tela empilhada pausa o guia; balão inline herda a largura do alvo e vira coluna com fonte máxima → todo guia: rode cada passo do zero com conta nova, em telas empilhadas, com fonte máxima e com o alvo fora da dobra.
- [2026-10-11] Toast em dobro (o do recurso novo + o da tela) e texto da dica que não bate com o rótulo do botão → compare o texto de cada dica com o botão real no print.

- [2026-10-14] Teclado aberto em sheet com rodapé fixo (TrueSheet `footer`): a faixa de ações do rodapé fica transparente e por cima dos campos (técnica do exercício sob "Como executar/Duplicar/Remover"), e o balão do guia preso ao rodapé cobre o fim do formulário → em todo sheet com `footer`, foque o último campo, abra o teclado e role até o fim; nada do rodapé pode desenhar sobre conteúdo, e o fim do formulário tem que ser alcançável (vídeo de usuário real).
- [2026-10-14] Sheet `detents={["auto"]}` com `scrollable`: no iOS o `scrollable` prende o ScrollView ao fundo e o sheet abre na altura máxima, com um vazio embaixo das opções → `scripts/ugly_scan.py` regra sheet-auto-scrollable; abra todo sheet curto e meça o vazio no print. Nasceu de uma correção de fonte grande que trouxe o `scrollable` junto.
- [2026-10-14] Balão posicionado pela medida feita com o teclado aberto: o rodapé estava no meio da tela, o balão foi para baixo e ficou lá depois que o teclado fechou → toda dica junto de botão de rodapé: abra o teclado, avance o guia, feche o teclado e confira o lado do balão.
- [2026-10-14] Fluxo que pede o mesmo dado duas vezes (cadastro do aluno já gera as aulas e o passo seguinte manda "marcar aula" de novo) → na jornada do personal, liste o que cada passo pede e marque repetição como bug de produto (pergunta ao CEO).
- [2026-10-14] Edição em massa ausente: abrir um sheet por item para preencher séries/reps de 8 exercícios → em toda lista que o usuário edita item a item, conte os toques para preencher 5 itens; acima de ~3 por item, é bug de usabilidade para relatar.
- [2026-10-14] Contrato ativo sem aulas no calendário e validade da Home diferente da vigência do contrato → para cada contrato aceito, confira no servidor que existem aulas do pacote e compare a validade mostrada na Home, no Perfil e no contrato (C13).

- [2026-10-16] Sheet que abre outro sheet sem esperar o primeiro fechar: no iOS o segundo não abre e o fluxo parece morto ("Como usar o app" > Cadastrar aluno voltava à Home sem abrir o cadastro) → todo `dismiss()` seguido de `present()` em outra tela: espere a promessa do dismiss; teste escolhendo cada item de cada sheet que leva a outro sheet.

## Falsos positivos que já enganaram
- [2026-10-10] Teste do servidor que falha entre 00:00 e 01:01 (fuso) não é bug novo: confirme na main antes.
- [2026-10-10] "Dica não apareceu" pode ser regra de produto (1 por sessão, 5 s de carência, alvo fora da tela). Leia a regra antes de reportar.

## Atalhos de ambiente que funcionam
- [2026-10-10] Servidor local sem mexer em config: `mix run --no-start` com `Application.put_env` do Repo (database própria) e `:phoenix, :serve_endpoints, true`; porta por `PORT=`.
- [2026-10-10] Dev client copiado de outro simulador (`simctl get_app_container` + `simctl install`); `simctl create` precisa do identificador completo do tipo e runtime.
- [2026-10-10] Metro com `CI=1` não recarrega: para comparar versões suba um segundo Metro em outra porta.
- [2026-10-10] argent: `describe` dá coordenadas normalizadas; campo de senha não aparece (fica logo abaixo do e-mail); com teclado numérico aberto, não toque "para fechar" em cima dele.
- [2026-10-10] Confirmação de e-mail desligada sem provedor de e-mail: register + login direto no ambiente local.

- [2026-10-10] Saldo "4 restantes" com contrato de 3 aulas não era bug: renovação soma o que sobrou do pacote anterior. Leia a regra de produto da memória antes de reportar dinheiro.
- [2026-10-10] "Personal vazia" deixa de ser vazia se a frente de API usar a mesma conta: reserve contas por frente (API cria as suas).

- [2026-10-10] O scratchpad da sessão some quando a sessão reinicia: script de seed, servidor e prints que precisam sobreviver ficam numa pasta própria fora do git (ex. `<repo>/.ceo/runs/`, com `.git/info/exclude`), não no scratchpad.

## Charters que renderam mais
- [2026-10-10] C10 API (BINMEN + autorização + duplo POST + schemas do app contra resposta real): 1 S2 e uma família de 500 em 9 min de máquina, sem simulador. Rode sempre primeiro.
- [2026-10-10] C01 garbage-collector + fonte máxima: 10 bugs (1 S2 de layout em 6 telas) em 90 min.
- [2026-10-10] C02+C05 jornada do personal com conta nova + dados ruins + conferência no servidor: 1 S2 (contrato velho para o aluno), 6 S3, em 70 min.
- [2026-10-10] C03+C06+C07 aluno + tempo + interrupção com ator B por API: 1 S2 (treino velho trava), 3 S3, em 50 min. Ator B mudando dado no meio é o que mais rende.
- [2026-10-10] Verificação final com os dois lados (app + servidor das branches de correção) e o ator B: confirmou 14 de 14 e ainda achou 2 S3 que só aparecem combinando as correções. Nunca pule.
- [2026-10-10] Varredura estática de "feio" (ugly_scan + leitura): 14 defeitos visíveis em 6 min. Rode em paralelo com o ambiente subindo.
