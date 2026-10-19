# Incidente AAAA-MM-DD: <o que parou, em palavras do cliente>

Arquivo: `.ceo/incidents/AAAA-MM-DD.md` (fora do git; não commitar). Fuso: <ex.: -03:00>

**Severidade:** <SEV1 | SEV2 | SEV3 | SEV4> · **Estado:** <investigando | identificado | monitorando | resolvido>
**Comandante:** <papel> · **Registro:** <papel> · **Comunicação:** <papel>
**Impacto:** <quem, quantos, o que não conseguem fazer> · desde <hora>
**Próximo update:** <hora>

## Linha do tempo
Uma linha por fato, na hora em que acontece. Tipos que o `scripts/timeline.py` entende:
inicio, detectado, declarado, comunicado, decisao, mitigado, deploy, ota, loja, resolvido, nota.

- AAAA-MM-DD HH:MM inicio: <primeiro sinal no log ou no crash, mesmo que achado depois>
- HH:MM detectado: <como soubemos: alerta, cliente, painel>
- HH:MM declarado: <SEV e quem comanda>
- HH:MM decisao: <o que foi decidido e por quê>
- HH:MM mitigado: <ação que estancou e a evidência de que estancou>
- HH:MM comunicado: <para quem, por qual canal, com pedido do dono>
- HH:MM resolvido: <métrica de volta ao normal e por quanto tempo>

## Hipóteses
- [ ] <hipótese> · evidência a favor: <...> · contra: <...>

## Comandos de produção rodados
Só depois de confirmação explícita na conversa. Um por linha, com hora e resultado.

## Pendências
- <o que falta e quem>
