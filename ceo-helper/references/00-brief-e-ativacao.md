# Brief e ativação

Monte o brief em silêncio antes de mexer em código. Ele não entra na resposta.

## Config

Ordem: `.ceo/config.md` na raiz do repo, depois perguntas. O que esta skill usa: `repos[]` (app e servidor, read-only ou não), `plataformas`, analytics (PostHog, Amplitude, Firebase ou nenhum), papéis e credenciais de teste por variável de ambiente.

## Brief

```
Objetivo:     <o que o CEO quer: ex. "personal novo agenda a 1ª aula no primeiro dia">
Papéis:       <ex. personal, aluno; papel que pode trocar no mesmo login?>
Tarefa-chave: <por papel, a ação que entrega valor>
Ativado:      <por papel, o evento real que prova a ativação + prazo, ex. "1 aula criada em 24 h">
Repos:        <app> | <servidor> | read-only?
Analytics:    <ferramenta e onde fica o client no app>
Já existe:    <empty states, tooltips, telas de boas-vindas, flags de "primeira vez">
Limites:      <só OTA? prazo? textos aprovados por alguém?>
```

## Como achar o "ativado"

1. Qual ação, se o usuário fizer, faz ele voltar amanhã? Para um app de agenda é marcar o primeiro compromisso, não abrir a agenda.
2. Precisa ser um dado no servidor (linha numa tabela), não um evento de tela. Assim o checklist se marca sozinho e o backfill de veteranos funciona.
3. Um por papel. Papel que só consome (ex.: aluno) pode ter ativação "abriu o primeiro treino que o personal montou".
4. Se ninguém sabe, proponha um e marque como [estimado] no relatório. O CEO decide.

## Perguntas que mudam o desenho

- O mesmo usuário pode ter dois papéis? Se sim, estado de dica é por usuário **e** papel.
- O usuário costuma reinstalar ou trocar de aparelho? Se sim, estado no servidor é obrigatório (`04`).
- Tem gente em produção? Se sim, backfill de veteranos antes do lançamento (`04`).
