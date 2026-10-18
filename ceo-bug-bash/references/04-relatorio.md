# 04. Bug e relatório

## Um bug
- Título: o que o usuário vê, não a causa ("Valor do pacote aparece R$ 1234.5").
- Passos mínimos (com conta e dado usados), esperado, observado.
- Evidência: caminho do print/vídeo do momento.
- Oráculo: qual (Product, Image, World...).
- Severidade proposta e porquê. Causa provável `arquivo:linha` marcada como hipótese até o teste provar.
- "Já existia" quando não veio da última mudança.

## Severidade (P0 a P3, mesma escala das outras skills ceo-*; base Mozilla S1-S4)
- **P0** (S1): bloqueia função central, perde dado, cobra errado, vaza dado de outro usuário, crash no fluxo principal. Sem contorno. Falha de segurança é P0 sempre.
- **P1** (S2): função importante quebrada com contorno ruim, dado velho até refresh, erro sem mensagem; o usuário trocaria de app.
- **P2** (S3): função secundária errada ou com contorno razoável; layout quebrado em fonte grande.
- **P3** (S4): cosmético. Pode ter prioridade alta se aparece em toda tela (oráculo Image).

## Relatório ao CEO
1. Uma frase: quantos bugs, quantos corrigidos, se dá para soltar.
2. Corrigidos: lista curta por severidade, o que o usuário via antes, PR.
3. Abertos que precisam dele: a decisão em 1 linha cada.
4. Não testado: o que ficou de fora e por quê.
5. Notei, não mexi: até 3.
Sem código, sem narrar o processo. Erro e risco completos.
