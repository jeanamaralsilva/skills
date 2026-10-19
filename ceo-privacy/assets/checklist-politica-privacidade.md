# Checklist: política de privacidade contra o código

Marque cada item comparando o texto da política com o inventário e com `data/sdks.csv`. Cada "não" vira linha de divergência com `arquivo:linha`.
Fontes: LGPD art. 9º e art. 18 (https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709compilado.htm); Res. CD/ANPD nº 18/2024 (https://www.in.gov.br/en/web/dou/-/resolucao-cd/anpd-n-18-de-16-de-julho-de-2024-572632074); Apple 5.1.1(i) (https://developer.apple.com/app-store/review/guidelines/); Google Play User Data (https://support.google.com/googleplay/android-developer/answer/10144311).

## Onde está

- [ ] URL pública, sem login, sem geobloqueio, não PDF (Play)
- [ ] Link no App Store Connect e no Play Console
- [ ] Link dentro do app (Conta ou Ajustes e no cadastro)

## Quem

- [ ] Identidade e contato do controlador
- [ ] Identidade e contato do encarregado em destaque (ou canal do titular, se pequeno porte)

## O quê, para quê, por quanto tempo

- [ ] Toda categoria do inventário aparece, inclusive as que SDKs coletam sozinhos (identificadores, IP, dados do aparelho)
- [ ] Nenhuma categoria na política que o app não coleta (ou explicar por quê)
- [ ] Finalidade de cada categoria
- [ ] Forma e duração do tratamento; prazos ou critérios de retenção
- [ ] Se algum dado é condição para usar o app, dito com destaque

## Com quem

- [ ] Cada fornecedor ou tipo de fornecedor que recebe dado (analytics, crash, push, pagamento, anúncio)
- [ ] Transferência para fora do Brasil, se houver
- [ ] Rastreamento ou anúncio personalizado, se houver, e como recusar

## Direitos

- [ ] Lista dos direitos do art. 18 e como pedir (canal)
- [ ] Como revogar consentimento, tão fácil quanto dar
- [ ] Como excluir a conta: no app e pelo link web; o que fica retido e por quê

## Segurança e menores

- [ ] Medidas de segurança em linguagem simples
- [ ] Idade mínima ou regras para menores, coerentes com o cadastro e com o rótulo da loja

## Coerência

- [ ] App Privacy (Apple) conta a mesma história
- [ ] Data safety (Google) conta a mesma história
- [ ] Data de atualização da política mais nova que a última mudança de coleta no código
