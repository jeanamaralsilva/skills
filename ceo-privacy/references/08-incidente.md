# Incidente com dado pessoal

Consultado em 2026-10-19. Conter o incidente em produção é da `ceo-incident`, se instalada. Aqui fica o que é próprio de dado pessoal: medir quem e o quê, prazos, comunicação à ANPD e aos titulares, registro. Decidir se comunica é do controlador com o advogado.

## 1. Conter e medir (sem expor)

- Pare o vazamento primeiro (feche o endpoint, troque a credencial, tire o log do ar), com confirmação para cada ação em produção.
- Meça por contagem, nunca listando valores: quantos titulares, quais categorias (`data/categorias.csv`), quantos são crianças, adolescentes ou idosos, desde quando, se tem dado sensível, financeiro, senha ou token.
- Preserve evidência (logs, ids de deploy) antes de apagar.
- Anote a hora em que soube que o incidente afetou dado pessoal: o prazo conta daí.

## 2. Precisa comunicar?

A LGPD manda comunicar à ANPD e ao titular incidente que possa gerar risco ou dano relevante (art. 48) [fonte: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709compilado.htm].

Pela Resolução CD/ANPD nº 15/2024, é de comunicação obrigatória quando afeta significativamente direitos do titular **e** envolve ao menos um: dado sensível; dado de criança, adolescente ou idoso; dado financeiro; senha ou token de autenticação; dado protegido por sigilo legal; larga escala (art. 5º) [fonte: https://www.in.gov.br/en/web/dou/-/resolucao-cd/anpd-n-15-de-24-de-abril-de-2024-556243024].

Leve ao advogado com os números já medidos. A skill não decide.

## 3. Prazos

| Para quem | Prazo | Fonte |
|---|---|---|
| ANPD | 3 dias úteis do conhecimento de que afetou dado pessoal; complementar em até 20 dias úteis | Res. CD/ANPD nº 15/2024 art. 6º, https://www.in.gov.br/en/web/dou/-/resolucao-cd/anpd-n-15-de-24-de-abril-de-2024-556243024 |
| Titulares | 3 dias úteis; linguagem simples; direto e individual (e-mail, mensagem, telefone) | Res. CD/ANPD nº 15/2024 art. 9º, mesma fonte |
| Pequeno porte | prazo em dobro, salvo risco à integridade física ou moral | Res. CD/ANPD nº 15/2024 art. 6º §8º; Res. CD/ANPD nº 2/2022 art. 14, https://www.in.gov.br/en/web/dou/-/resolucao-cd/anpd-n-2-de-27-de-janeiro-de-2022-376562019 |
| Autoridade na UE (GDPR) | 72 horas; titulares sem demora se o risco for elevado | arts. 33 e 34, https://publications.europa.eu/resource/celex/32016R0679 |

## 4. Comunicação

- À ANPD: formulário eletrônico pelo peticionamento do SEI da ANPD, com login gov.br, enviado pelo encarregado ou representante com prova de vínculo [fonte: https://www.gov.br/anpd/pt-br/assuntos/incidente-de-seguranca]. Rascunho dos campos em `assets/comunicacao-incidente-template.md`.
- Aos titulares: rascunho na mesma template, seção titular. A skill escreve; o dono, com o advogado, envia.
- Nada de valor de dado pessoal nos rascunhos nem no relatório.

## 5. Registro

Todo incidente com dado pessoal, comunicado ou não, fica registrado por no mínimo 5 anos (Res. CD/ANPD nº 15/2024 art. 10) [fonte: https://www.in.gov.br/en/web/dou/-/resolucao-cd/anpd-n-15-de-24-de-abril-de-2024-556243024]. Use a mesma template; guarde em `.ceo/privacy/incidentes/` (fora do git) ou onde o jurídico mandar.

## 6. Depois

Corrija a causa (log com dado pessoal, armazenamento, permissão de acesso), rode `scripts/pii_scan.py` de novo e escreva o postmortem sem culpa (`ceo-incident`).
