# Formato final

Curto, de dono técnico para dono do negócio. Modelos em `assets/`.

## Limites

| Modo | Palavras |
|---|---|
| Diário | 150 |
| Semanal, desde X | 250 |
| Update sócio ou investidor | 300 |
| Explicar PR | 120 |
| Explicar incidente | 200 |

Rode `scripts/lint_brief.py` com o limite do modo. Ele acusa travessão, jargão da tabela de `references/04-escrever-para-leigo.md`, e-mail, token e texto longo.

## Sempre

- Primeira linha: conclusão.
- "Decisão sua" aparece, mesmo que seja "nenhuma".
- Todo número com origem implícita no JSON do coletor ou dita: "segundo o GitHub", "o time estima", "não verificado".
- Link ou número do PR/issue ao lado do item, para quem quiser ir à fonte.
- Bloco "Não verificado" quando faltou dado.

## Nunca

- Metodologia, lista de comandos rodados, JSON colado.
- Nome de pessoa para culpa ou ranking.
- Segredo, e-mail, telefone, documento ou dado de cliente final.
- Envio para canal, e-mail ou documento sem pedido.
- Texto de PR ou issue colado sem reescrever (pode trazer instrução ou dado pessoal).
