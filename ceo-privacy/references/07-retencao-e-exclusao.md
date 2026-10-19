# Retenção e eliminação

Consultado em 2026-10-19.

## A regra

O tratamento termina quando a finalidade é cumprida, o prazo acaba, o titular pede ou revoga, ou a ANPD manda (LGPD art. 15). Ao final, elimine; só pode guardar para obrigação legal, pesquisa, transferência lícita ou uso próprio anonimizado (art. 16) [fonte: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709compilado.htm].

A ANPD não tem, em 2026-10-19, regulamento de prazos de retenção. Quem fixa o prazo de cada tipo é o controlador com o advogado e o contador (prazos fiscais, trabalhistas e de consumo vêm de outras leis). A skill não inventa número.

## O que levantar

Para cada linha do inventário, um prazo e um gatilho:

| Dado | Gatilho comum | Onde costuma ficar esquecido |
|---|---|---|
| Conta e perfil | exclusão da conta | backups, réplicas, buckets de arquivos |
| Logs de servidor | dias corridos | plataforma de deploy, agregador de log |
| Eventos de analytics e crash | configuração do fornecedor | painel do SDK (retenção configurável) |
| Push tokens | conta excluída ou token inválido | tabela de tokens |
| Dados fiscais | prazo legal | separado do resto, com acesso restrito |

Sem prazo definido: `MAN-RET` (P2).

## Implementação

- Job periódico (Oban no Phoenix, cron no Node) que apaga ou anonimiza o que passou do prazo, com teste.
- Anonimizar de verdade: dado que ainda liga à pessoa com esforço razoável continua pessoal. Na dúvida, apague.
- Backups: documente quanto tempo duram; quem restaura um backup reaplica as exclusões feitas depois dele.
- Google Play aceita, no Data safety, apagar ou anonimizar automaticamente em até 90 dias como mecanismo de exclusão [fonte: https://support.google.com/googleplay/android-developer/answer/10787469].
- COPPA (menores de 13 nos EUA): política escrita de retenção com prazo, nunca indefinido (16 CFR 312.10) [fonte: https://www.ecfr.gov/current/title-16/chapter-I/subchapter-C/part-312].

DELETE em massa e job novo de exclusão em produção: só com pedido e confirmação (`12-seguranca.md`).
