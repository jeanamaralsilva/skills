# Invariantes de dados

Bug de regra de negócio muitas vezes não aparece na tela de quem testa: aparece no banco, semanas depois, em poucos registros. Invariante é uma regra que tem que valer para toda linha ("um contrato ativo por vínculo"). Cada uma vira um `SELECT` que lista quem viola. Resultado vazio é saúde; resultado com linhas é suspeita para investigar, não sentença.

## De onde tirar as regras

Leia o código que decide, não o que mostra: funções de saldo, jobs agendados, mudanças de status, validações. Cada regra que o código assume e o banco não garante (sem constraint, sem índice único) é candidata.

| Padrão | Pergunta em SQL | Por que quebra |
|---|---|---|
| Campo guardado x valor derivado | o contador salvo (saldo, total, restante) bate com o que a regra calcula a partir das linhas? | o contador é atualizado num caminho e esquecido em outro |
| Um ativo por dono | existe dono com mais de um registro ativo? | falta índice único parcial; duas requisições ao mesmo tempo |
| Status x data | registro "concluído" sem data de conclusão, "em andamento" há horas, "pendente" já vencido | não existe job que fecha ou vence; o job só olha uma coluna |
| Lote misturado | o agrupamento atual (ciclo, período, pacote) junta itens de antes e depois do início do contrato vigente? | renovação reaproveita o lote em vez de abrir outro |
| Data de fim | fim salvo diverge do fim do contrato vigente; fim no passado com itens ainda abertos | só um caminho recalcula a data |
| Job x estado | lembrete agendado para item cancelado; item futuro sem lembrete; job em erro repetido | cancelamento não cancela o job; agendamento falhou calado |
| Ids de espaços diferentes | a mesma coluna guarda às vezes id de usuário, às vezes id de vínculo | registro antigo some da tela de quem deveria ver |
| Dia local | data guardada em UTC comparada com "hoje" no fuso do usuário | item da noite cai no dia errado |

## Como escrever

- Um arquivo por grupo de regra; cada checagem com id (`I1.1`), uma frase do que viola e o `SELECT`.
- Saída curta: `I1.1 descrição: N` e no máximo 4 linhas de exemplo. Ids como texto, nada de dado pessoal além do necessário para achar o registro.
- No topo do grupo, a regra do código em uma ou duas linhas, com o arquivo e a função de onde ela veio. É isso que permite decidir se N > 0 é bug ou regra mal entendida.
- Visão geral opcional por grupo (contagem por status, por lote) ajuda a ver o tamanho antes de abrir exemplos.

## Onde rodar

1. **Primeiro no banco local**, com o seed da sessão. Toda checagem tem que rodar sem erro e voltar vazia nos dados que a sessão criou corretamente.
2. **Produção só com autorização explícita do dono, e só leitura.** Abra a transação como somente leitura (`SET TRANSACTION READ ONLY` ou `default_transaction_read_only`) ou use um usuário de banco só com SELECT. Nada de `UPDATE` "para corrigir já": correção de dado vira migração revisada.
3. Credenciais, ids de serviço, chaves SSH e o próprio script com SQL do app ficam no repo do app (`.ceo/invariants/`, fora do git) ou no CI dele. Nunca na pasta da skill.

## Do achado à correção

N > 0: abra 1 exemplo inteiro, reproduza o caminho que o gerou no ambiente local, escreva o teste que falha e corrija o caminho. A checagem continua no conjunto e roda de novo depois do deploy; o número tem que cair para 0 nos registros novos. Registros antigos viram migração de dados separada, com o dono decidindo.

## Fontes

- PostgreSQL, SET TRANSACTION (modo READ ONLY): https://www.postgresql.org/docs/current/sql-set-transaction.html
- PostgreSQL, default_transaction_read_only: https://www.postgresql.org/docs/current/runtime-config-client.html
