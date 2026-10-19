# Quanto falta

A pergunta mais difícil do dono. A resposta honesta separa o que ainda é incerto do que já é execução.

## Regra do morro (Shape Up)

O Shape Up troca "% concluído" por "o que ainda é desconhecido e o que já está resolvido" [fonte: https://basecamp.com/shapeup/3.4-chapter-13]:

- **Subindo o morro:** ainda há incerteza. O time não sabe como vai fazer uma parte. Prazo aqui é chute.
- **Descendo o morro:** tudo já foi descoberto. Falta executar. Prazo aqui é estimativa razoável.
- Lista de tarefas cresce enquanto o time avança, então contar tarefas abertas não mede quanto falta (mesma fonte).
- Frente que não anda entre dois updates é uma mão levantada: algo pode estar errado (mesma fonte).

## Como responder

1. Liste as frentes da entrega (3 a 6). Fonte: milestones, labels, PRs abertos, ou pergunte ao time.
2. Para cada uma: **resolvido** (só execução), **incerto** (o que falta descobrir, em 1 frase) ou **parado** (há quantos dias, esperando o quê).
3. Dê prazo só para a parte resolvida, dizendo que é estimativa e de quem. Para a parte incerta, diga o que vai tirar a dúvida e quando.

Exemplo: "Faltam 3 frentes. Cadastro e tela de pagamento: só execução, o time estima 1 semana. Nota fiscal: ainda não sabemos se o provedor aceita o nosso formato; teste até quinta. Prazo do lançamento depende dessa resposta."

## Milestone com porcentagem

`github.milestones` traz itens abertos e fechados [fonte: https://docs.github.com/en/rest/issues/milestones]. Diga "X de Y itens prontos" e o aviso de que a lista pode crescer. Nunca converta em data.

## Sozinho com IA

Quem trabalha sozinho com agente de código raramente tem milestone. Use os PRs abertos, o branch atual e a lista que o dono der. A regra é a mesma: incerto, resolvido ou parado.
