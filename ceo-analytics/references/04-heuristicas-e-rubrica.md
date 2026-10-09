# Heurísticas e rubrica

A rubrica existe para que duas análises do mesmo app cheguem ao mesmo resultado. Sem ela, a nota depende do humor do modelo.

## Nielsen, de 0 a 4

Pontue cada uma das 10 heurísticas (H01 a H10 em `data/heuristics.csv`):

| Nota | Significado |
|---|---|
| 4 | Sem problema observado |
| 3 | Problema cosmético, não atrapalha a tarefa |
| 2 | Atrito: a tarefa sai, mas custa |
| 1 | Erro frequente ou perda de dado |
| 0 | Bloqueia a tarefa |
| n/a | Não se aplica ou não foi observável |

A nota final é a média das heurísticas pontuadas. `n/a` sai do denominador. Escreva quantas foram `n/a`: uma nota 3,8 com 6 `n/a` diz pouco.

A nota não é o produto. O Jean quer os achados. Use a nota numa linha do veredito e siga em frente.

## Severidade do achado

| Nível | Critério | Exemplo |
|---|---|---|
| **P0** | Impede concluir a tarefa principal ou perde dado | Carga do exercício não salva |
| **P1** | Erro frequente, confusão que gera suporte, acessibilidade que exclui | Botão de 32pt, contraste 2,8:1 [medido] |
| **P2** | Atrito que o usuário contorna | Tarefa frequente com 5 toques |
| **P3** | Polimento | Espaçamento inconsistente entre cards |

Na dúvida entre dois níveis, escolha o menor e diga por quê. Inflar severidade para parecer relevante é um dos vícios da análise feita por IA.

## Laws of UX que mais aparecem em mobile

- **Doherty (H11)**: resposta abaixo de 400ms mantém o ritmo. Acima disso, dê feedback.
- **Fitts (H12)**: o CTA principal fica grande e na zona do polegar (metade de baixo da tela).
- **Hick (H13)**: muitas opções de mesmo peso atrasam a decisão. Hierarquize.

## Onde a IA erra (revise você mesmo)

No estudo com GPT-4o contra especialistas (arXiv 2506.16345), o modelo foi bem em "estética e minimalismo" e em "correspondência com o mundo real", e mal em:

- **H07 Flexibilidade e eficiência**: exige percorrer a tarefa repetida vezes. Conte os toques da tarefa mais frequente.
- **H03 Controle e liberdade**: exige testar desfazer, voltar e cancelar de verdade.

Para essas duas, não pontue a partir de um print. Percorra o fluxo (app rodando) ou siga o código da ação até o fim.

## Consulta

```bash
python <skill>/scripts/search.py "voltar android sheet" --domain heuristics
```

Cada linha traz a detecção, a severidade padrão e a fonte. A severidade padrão é ponto de partida: o contexto do app pode subir ou descer.
