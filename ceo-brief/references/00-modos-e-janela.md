# Modos e janela

## Modos

| Pedido | Modo | Janela padrão | Leitor |
|---|---|---|---|
| "como foi hoje", "o que rolou" | diário | `1d` | dono |
| "resumo da semana", "status" | semanal | `7d` | dono |
| "o que mudou desde a 2.3", "desde segunda" | desde X | tag ou data dita | dono |
| "o que eu falo pro meu sócio", "update para investidor", "prepara a reunião" | update | desde o último update (pergunte a data) ou `30d` | sócio, investidor |
| "explica esse PR", "o que essa mudança faz" | explicar PR | o PR | dono ou cliente |
| "explica o que caiu", "o que digo pro cliente" | explicar incidente | o incidente | dono ou cliente |
| "quanto falta pra lançar X" | quanto falta | desde o início da frente | dono |

Sem modo claro, faça o semanal.

## Janela

- **Tag:** `--since v2.3.0` lista o que entrou na base depois da tag. Use quando o dono fala de versão.
- **Data:** `--since 2026-10-01`. Inclusiva.
- **Prazo:** `7d`, `2w`. Contado a partir de agora ou de `--until`.
- Update para investidor ou sócio: use a data do último update que ele mandou. Repetir a mesma janela todo mês deixa os números comparáveis [fonte: https://web.archive.org/web/20201202112659/https://www.aaronkharris.com/investor-updates].

## Vários repos

Projeto com app e servidor em repos separados: rode o coletor em cada um e junte por resultado ("o cliente agora consegue X" pode precisar de mudança nos dois). Diga quando uma metade está no ar e a outra não.

## O que vem da config

`.ceo/config.md` (modelo em `assets/ceo-config.example.md`): repos e papéis, leitor padrão, idioma, limite de palavras, se o app tem loja. Sem config, assuma e diga a suposição em 1 linha se ela muda o texto.
