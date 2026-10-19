# Plano de corte: AAAA-MM-DD

Economia possível: entre X e Y por mês. Nada é executado sem "sim" do dono, uma ação por vez.

| # | Corte | Economia por mês (faixa) | Risco ao cliente | Esforço | Como desfazer | Quem decide | Fonte |
|---|---|---|---|---|---|---|---|
| 1 | Teto e alerta de gasto em ... | evita surpresa | nenhum; ao bater o teto, ... para | minutos | remover o teto | dono | id em data/levers.csv |
| 2 | | | | | | | |

## Antes de executar
- Estado atual salvo (print ou export do painel, `eas.json`, `fly.toml` etc.).
- Janela combinada e quem acompanha.

## Depois
- App de pé (teste do time ou ceo-mobile-qa).
- Data anotada para comparar na próxima fatura.

## Não fazer
- Cortar backup, monitoramento de erro ou segurança sem decisão explícita do dono sabendo o risco.
- Apagar volume, bucket, banco ou projeto sem confirmar que nada usa: apagar não tem volta.
