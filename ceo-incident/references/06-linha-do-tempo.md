# Linha do tempo

Consultado em 2026-10-19.

O documento vivo do incidente é a principal responsabilidade de quem comanda [fonte: https://sre.google/sre-book/managing-incidents/]. Notas em tempo real reconstroem a linha do tempo do postmortem, com hora e fuso [fontes: https://www.atlassian.com/incident-management/handbook/incident-response e https://www.atlassian.com/incident-management/handbook/postmortems].

## Arquivo do incidente

`.ceo/incidents/AAAA-MM-DD.md`, a partir de `assets/linha-do-tempo-template.md`. Fica fora do git (a pasta `.ceo/` não se commita). Escreva na hora, uma linha por fato:

```
- 2026-10-19 13:50 inicio: primeiros erros 500 no login (log)
- 14:05 detectado: cliente reclamou no suporte
- 14:25 mitigado: rollback do servidor para o deploy anterior
```

Tipos: inicio, detectado, declarado, comunicado, decisao, mitigado, deploy, ota, loja, resolvido, nota. Linha só com hora usa a data do nome do arquivo. Nunca cole dado pessoal ou segredo: descreva ("e-mail do cliente", "token do serviço").

## Montar

```bash
python3 scripts/timeline.py --events .ceo/incidents/2026-10-19.md \
  --repo apps/server --repo apps/mobile --ref origin/main --tz=-03:00
```

- Junta eventos, commits do ramo e tags criadas na janela; ordena por hora.
- Sem `--since`, a janela do git começa 24 h antes do primeiro evento.
- Calcula tempo até detectar, mitigar e resolver a partir de `inicio`. Atlassian mede tempo até detectar (início à detecção) e até recuperar (início ao fim) [fonte: https://www.atlassian.com/incident-management/handbook/incident-response].
- `--json` para processar; Markdown para o postmortem.
- Git só leitura (`--no-optional-locks`, sem fetch): o resultado é tão novo quanto o último fetch. Deploy, OTA e loja não estão no git: anote como eventos (`deploy:`, `ota:`, `loja:`) com a hora que a plataforma mostra.
