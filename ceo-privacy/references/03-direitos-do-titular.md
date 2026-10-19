# Direitos do titular e exclusão de conta

Consultado em 2026-10-19.

## O que o titular pode pedir (LGPD art. 18)

Confirmação de que você trata dados dele; acesso; correção; anonimização, bloqueio ou eliminação do desnecessário; portabilidade; eliminação do que foi tratado com consentimento; saber com quem você compartilhou; saber que pode negar o consentimento; revogar [fonte: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709compilado.htm]. O pedido é gratuito e, ao corrigir ou apagar, você avisa quem recebeu o dado (art. 18 §§5º e 6º) [fonte: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709compilado.htm].

## Prazos

| Norma | Prazo | Fonte |
|---|---|---|
| LGPD, acesso | formato simplificado na hora, ou declaração completa em até 15 dias do pedido (art. 19) | https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709compilado.htm |
| LGPD, cópia | com base em consentimento ou contrato, cópia eletrônica integral (art. 19 §3º) | https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709compilado.htm |
| ANPD, pequeno porte | prazo em dobro para pedidos do titular (Res. CD/ANPD nº 2/2022 art. 14) | https://www.in.gov.br/en/web/dou/-/resolucao-cd/anpd-n-2-de-27-de-janeiro-de-2022-376562019 |
| GDPR | 1 mês, prorrogável por mais 2 (art. 12(3)) | https://publications.europa.eu/resource/celex/32016R0679 |

A ANPD não tem, em 2026-10-19, regulamento próprio sobre direitos do titular; vale o texto da lei.

## Como atender um pedido (fluxo técnico)

1. **Confirme a identidade** pelo canal da conta (logado no app, ou e-mail da conta). Nunca mande dado para um contato novo que só diz ser o titular.
2. **Ache tudo da pessoa** pelo mapa de dados (`01-mapa-de-dados.md`): tabelas, arquivos, aparelho, SDKs (Sentry, Firebase, push).
3. **Consulta só leitura**, proposta antes e rodada com "sim" (`12-seguranca.md`).
4. **Responda** com `assets/resposta-titular-template.md`: rascunho para o dono enviar. O export vai em formato legível por máquina (JSON ou CSV) e por canal seguro, nunca colado no chat da skill.
5. **Registre** o pedido, a data e a resposta (sem o conteúdo exportado).

## Exclusão de conta (Apple e Google)

| Loja | Regra | Fonte |
|---|---|---|
| Apple | quem cria conta oferece a exclusão dentro do app; desativar não basta; sem exigir ligação ou e-mail | diretriz 5.1.1(v), https://developer.apple.com/app-store/review/guidelines/ |
| Apple | fácil de achar; pode ter confirmação e reautenticação; informar prazo e o que fica retido por lei; Sign in with Apple revoga o token pela REST API; vale para todos os países | https://developer.apple.com/support/offering-account-deletion-in-your-app/ |
| Google Play | caminho no app e link web público declarado no Console; apagar os dados ligados à conta e pedir o mesmo aos fornecedores; pode reter por segurança, fraude ou regulação, informando | https://support.google.com/googleplay/android-developer/answer/13327111 |
| Google Play | desativar ou congelar conta não conta como exclusão | https://support.google.com/googleplay/android-developer/answer/10144311 |

O que o backend apaga ou anonimiza, no mínimo: perfil, credenciais e tokens de sessão, push tokens, arquivos (fotos, documentos), dados em SDK que tenha API de exclusão (Crashlytics avisa que limpar o user id não apaga o histórico [fonte: https://firebase.google.com/docs/crashlytics/android/customize-crash-reports]). O que fica por obrigação legal (nota fiscal, por exemplo) fica separado e dito ao usuário.

Implementação típica:
- **App:** item "Excluir conta" em Conta ou Perfil, tela que explica o que some e o que fica, confirmação, chamada autenticada, logout e limpeza do SecureStore e do armazenamento local.
- **Phoenix:** rota `delete "/me"` (ou equivalente) no escopo autenticado, contexto `Accounts.delete_user/1` numa transação (`Ecto.Multi`), job para arquivos e fornecedores. **Node:** mesmo desenho com o ORM do projeto.
- **Web:** página pública com o mesmo fluxo, para o Play.
- **Prova:** teste automatizado do endpoint e uma conta descartável apagada de ponta a ponta (`ceo-mobile-qa`, se instalada).

`scripts/pii_scan.py` aponta `PRV-CTA` (app sem caminho) e `PRV-CTA2` (servidor sem endpoint). Não achar não prova que não existe: confira o nome que o projeto usa.
