# Relatório CEO

Curto, de dono para CEO. Modelo: `assets/report-template.md`.

## Estrutura

1. **Veredito:** 1 linha: **sobe**, **sobe com risco** ou **não sobe**, e por quê.
2. **Por loja:** uma linha cada com versão, build e caminho (build novo ou OTA).
3. **Bloqueia** (P0 e P1): até 7, uma linha cada: `- **P1** <problema> → <correção> \`<arquivo:linha>\``. Evidência: arquivo do repo, `[cmd: ...]` ou `[fonte: url]`.
4. **Checklist manual:** só os itens que se aplicam e que o script não vê (conta demo, App Privacy, Data safety, screenshots, teste fechado), com quem faz.
5. **Plano de lançamento:** gradual ou não, e como voltar.
6. **Pendente do CEO:** só decisões com trade-off (ex.: "tirar suporte a iPad ou fazer prints de iPad").

## Severidade

| Nível | Critério |
|---|---|
| P0 | upload ou publicação recusada com certeza (target API, Xcode, identificador, teste fechado não cumprido) |
| P1 | rejeição provável na revisão ou quebra de quem já usa (texto de permissão padrão, sem exclusão de conta, OTA incompatível) |
| P2 | atraso ou risco menor (declaração de permissão, política de runtime frágil, iPad sem print) |
| P3 | higiene (pergunta de criptografia a cada envio, campo ignorado) |

## Limites

- Até 350 palavras. Sem metodologia, sem lista de comandos rodados.
- Data e número de regra de loja sempre com `[fonte: url]` e a data da consulta se tiver mais de 3 meses.
- Item não verificado aparece como "não verificado", nunca como ok.
- Erro e risco de segurança (credencial no repo, por exemplo) vão completos.
