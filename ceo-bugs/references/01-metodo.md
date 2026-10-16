# 01. Método: sessão, missão, oráculo, RIMGEA

Fontes em `_pesquisa.md` §1 e §5.

## Testar não é checar
Script confirma o que já se sabia. A sessão existe para descobrir o que ninguém pensou. Pergunte "o que pode dar errado aqui?" em cada tela, não "o botão funciona?".

## Sessão (SBTM)
- 60 a 120 min, uma missão (charter), notas do que fez, bugs, perguntas.
- Formato da missão: "Explorar <área> com <recurso/variação> para descobrir <tipo de risco>".
- A missão pode mudar no meio se aparecer risco maior: anote a troca.
- Fecha com PROOF: o que fez, o que achou, o que atrapalhou, o que falta, impressão geral.

## Ordem dentro do app
1. **Garbage-collector tour:** abrir cada tela uma vez, print de cada (estado normal). Já pega tela que não abre, texto cortado, inglês, estado vazio pobre.
2. **Landmark tour:** as 3 a 5 jornadas que pagam a conta (ex.: num app de personal trainer, personal cadastra aluno → marca aula → monta treino → fecha aula; aluno confirma presença → faz treino → aceita contrato).
3. **Money tour:** todo lugar com valor, pacote, pagamento.
4. **Bad-data tour:** nome gigante, emoji, zero, negativo, colar texto formatado.
5. **Interruption tour:** background no meio do envio, rede caindo, outro usuário mudando o mesmo dado.
6. **Variação de plataforma:** fonte máxima, tela pequena, Android.

## SFDIPOT (o que variar)
Structure, Function, Data, Interfaces, Platform, Operations, Time. Em cada missão escolha 2 ou 3 letras. Travou: percorra as letras atrás de ideia.

## Oráculos FEW HICCUPPS (como saber que é bug)
Familiar (padrão conhecido), Explainability (ninguém explica), World (impossível no mundo real), History (era diferente antes), Image (parece amador), Comparable (WhatsApp/Agenda do iOS fazem diferente), Claims (contradiz PR, termo, texto da loja), User expectations, Product (inconsistente consigo mesmo), Purpose, Statutes (LGPD, HIG, WCAG).
Todo bug cita o oráculo. Oráculos em conflito: mostre o conflito ao CEO.

## RIMGEA antes de reportar
Replicar (2 vezes), Isolar (menos passos), Maximizar (pior consequência possível), Generalizar (onde mais acontece: outra tela, outro papel), Externalizar (quem sofre), dizer de forma neutra.
Intermitente: reporte com a frequência ("1 em 5") como observação.

## Siga o dado
Criou na tela A: aparece em B, C e no servidor? Editou: todos refletem? Apagou: some de todos e não deixa órfão? Duplo toque: conte no banco.
