# 06. Aprendizados de exemplo (semente)

Padrões que renderam bug em apps React Native/Expo com backend próprio. Use como ponto de partida do `.ceo/aprendizados.md` do projeto: copie os que se aplicam e troque "onde procurar" pelo caminho real do repo depois de confirmar.

Formato: `padrão → onde procurar da próxima vez`.

## Onde apps costumam quebrar
- **Contrato do validador x resposta do servidor.** O app valida a resposta (ex.: zod) e o servidor manda outro formato (campo aninhado, `null` onde o schema espera string): o parse falha e a tela mostra "não encontrado" ou vazio para sempre → rode os schemas do app contra a resposta real de cada GET que ele usa.
- **Erro desenhado como vazio.** Query sem ramo de erro cai no estado vazio ("Nenhum item"): o usuário acha que perdeu dado → toda tela com query; derrube o servidor ou devolva 500 e veja se aparece erro com "tentar de novo".
- **Fonte máxima quebra overlay.** Modal, sheet, tooltip e balão com altura fixa cortam texto ou saem da tela; cabeçalho com ícones estoura; botão de altura fixa corta rótulo → repita o garbage-collector inteiro com `content_size` no máximo; é onde mais rende bug visual.
- **Sheet + teclado com rodapé fixo.** Com o teclado aberto, a faixa de ações do rodapé (ex.: `footer` de uma lib de bottom sheet) fica transparente por cima dos campos ou o fim do formulário não é alcançável → em todo sheet com rodapé e campo, foque o último campo, abra o teclado e role até o fim.
- **Dismiss → present de modais.** Um sheet ou modal abre outro sem esperar o primeiro fechar: no iOS o segundo não abre e o fluxo parece morto → todo `dismiss()` seguido de `present()`; escolha cada item de cada sheet que leva a outro sheet.
- **Regra só no app.** Botão escondido ou validação na UI (ex.: confirmar agendamento que já passou, janela de prazo) que o servidor aceita pela API → para cada regra de UI, tente a mesma ação direto na API.
- **Unicidade por caixa.** Duplicata passa com maiúsculas diferentes (e-mail, nome de entidade); mapa de erro do servidor comparado com caixa ("Internal Server Error" escapa da tradução) → crie duplicado por API com caixa trocada; compare chaves de erro sem caixa.
- **Erro mostrado em dobro.** O hook mostra toast com a mensagem do servidor e a tela ainda abre um alerta genérico "Tente novamente" → todo `catch` depois de `mutateAsync` (ou equivalente); provoque um 422 e conte os avisos.

## Falsos positivos comuns
- Teste do servidor que falha só perto da meia-noite (fuso) não é bug novo: confirme na branch principal antes.
- "Não apareceu" pode ser regra de produto (1 vez por sessão, carência, alvo fora da tela): leia a regra antes de reportar.

## Atalhos de ambiente
- O scratchpad da sessão some quando a sessão reinicia: seed, scripts e prints que precisam sobreviver ficam em `<repo>/.ceo/runs/`.
- Reserve contas por frente (API, simulador): uma frente sujando a conta da outra gera falso "vazio".
