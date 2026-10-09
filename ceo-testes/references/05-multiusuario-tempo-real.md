# Multiusuário e tempo real

Dois papéis na mesma sala (ex.: quem conduz e quem participa, atendente e cliente, dois jogadores) é onde os bugs mais caros moram e onde quase ninguém testa, porque exige dois clientes. Aqui são dois clientes sempre: o app no simulador (ator A) e um segundo ator que pode ser outro simulador ou um cliente por API.

## Ator B por API: `phx_actor.mjs`

Cliente Phoenix Channels sem dependências (protocolo v2 sobre o WebSocket nativo do Node 22+). Faz join, push, espera evento, derruba e reconecta, e imprime um log JSON.

```bash
node scripts/phx_actor.mjs --url ws://localhost:4000/socket --topic "room:42" \
  --params '{"token":"'$TEST_TOKEN_B'"}' --role user --script steps.json --verbose
```

`steps.json`:
```json
[
  {"wait": "session_started", "timeout": 30000},
  {"push": "send_answer", "payload": {"text": "42"}},
  {"repeat": 5, "push": "send_answer", "payload": {"text": "dup"}, "interval": 40},
  {"disconnect": true}, {"sleep": 3000}, {"reconnect": true},
  {"wait": "question_created", "timeout": 10000}
]
```

Saída (última linha do stdout): `{"joined","pushed":[{event,status,ms}],"received":[{event,at,payload}],"script_steps_ok","errors"}`. `status` é `ok`, `error` ou `timeout` (10 s, igual ao cliente JS). Exit 1 se algum passo falhou.

Token: a mesma coisa que o app manda em `params` do `Socket` (leia `src/lib/socket.ts` ou equivalente). Gere pelo endpoint de login da API com as credenciais do papel B (`TEST_USER_B`); nunca copie token de produção.

Para Socket.IO ou outro protocolo, o ator não serve; escreva um script equivalente com o cliente oficial e a mesma saída JSON.

## Os sete testes que valem a sessão

Derivados da matriz do `map_realtime.py`. Oráculo escrito antes de rodar.

| # | Teste | Como | Esperado | Bug |
|---|---|---|---|---|
| 1 | B dispara, A reflete | ator B `push create_question`; A na tela | A mostra em menos de 1 s [medido], sem pull-to-refresh | B09, B43 |
| 2 | Ordem | B envia 3 eventos com `interval: 10` | A mostra na ordem do servidor (número de sequência), não na de chegada | B44 |
| 3 | A em background | A em Home 2 min; B dispara; A volta | A sincroniza ao voltar (refetch por `AppState` ou rejoin com `last_seen_id`) | B15, B42, B43 |
| 4 | A reconecta no meio | Toxiproxy `reset_peer` 2 s em A; B dispara durante | A faz rejoin com backoff; evento perdido é recuperado por sync; sem loop | B41, B42 |
| 5 | Duplo toque de A | `tapOn repeat: 5` em "enviar" | B recebe 1 evento; servidor tem 1 registro | B01, B03 |
| 6 | Presença | B entra por dois clientes e sai de um | A continua vendo B online; contador não dobra | B47, B48 |
| 7 | Sessão de B expira | revogar token de B no servidor; B push | B recebe erro e volta ao login; A vê B sair | B20, B21 |

Dois simuladores só quando o oráculo é visual nos dois lados ao mesmo tempo (ex.: "os dois veem o cronômetro igual"). Nesse caso: `sim_session.py create user` e um segundo flow Maestro com `--device`, em paralelo:

```bash
maestro --device $A test -e ROLE=admin admin.yaml & maestro --device $B test -e ROLE=user user.yaml & wait
```

## Lado do servidor (ExUnit)

O teste de canal com dois clientes é curto e pega a maioria dos bugs de broadcast antes de abrir simulador:

```elixir
{:ok, _, a} = AppWeb.UserSocket |> socket("user:1", %{user_id: 1}) |> subscribe_and_join(AppWeb.RoomChannel, "room:1")
{:ok, _, b} = AppWeb.UserSocket |> socket("user:2", %{user_id: 2}) |> subscribe_and_join(AppWeb.RoomChannel, "room:1")
ref = push(a, "create_question", %{"text" => "2+2?"})
assert_reply ref, :ok
assert_push "question_created", %{"text" => "2+2?"}   # chega para a
assert_push "question_created", %{"text" => "2+2?"}   # e para b (ambos no mailbox do teste)
```

Os dois sockets entregam no mesmo processo de teste; `assert_push` duas vezes cobre os dois. Para processos separados, `socket/4` com o pid e `Task`. `assert_broadcast` cobre o PubSub; `refute_push` com timeout curto prova que o evento **não** foi duplicado. Corrida: `Task.async_stream(1..50, fn _ -> push(...) end)` e contar registros. Mais em `08-servidor-elixir.md`.

## Comportamento do cliente JS que explica bugs "aleatórios"

- `reconnectAfterMs`: 10, 50, 100, 150, 200, 250, 500, 1000, 2000 ms, depois 5 s. `rejoinAfterMs`: 1, 2, 5 s, depois 10 s. Um teste de reconexão precisa esperar mais que 10 s para ver o rejoin estável.
- `push` sem conexão vai para `pushBuffer` e é enviado ao reconectar: duplicata se o servidor processou o original e a resposta se perdeu (B41). Idempotência por chave no servidor é o conserto.
- Timeout de push: 10 s. O servidor pode ter processado e o app mostra erro (B40). O reenvio pelo usuário cria o segundo registro.
- `channel.join()` só pode ser chamado uma vez por instância; remount que cria novo channel sem `leave` do antigo gera listener duplicado (B46).
- Heartbeat 30 s: a queda só é percebida em até 30 s se o TCP não fechar. Em teste, `reset_peer` do Toxiproxy fecha na hora; `timeout` (segura sem resposta) simula a queda silenciosa.

## Fontes

- Phoenix.ChannelTest: https://phoenix.hexdocs.pm/Phoenix.ChannelTest.html ; https://phoenix.hexdocs.pm/testing_channels.html
- Dois clientes no mesmo teste: https://elixirforum.com/t/testing-a-phoenix-channel-with-multiple-clients/7748
- Cliente JS (constants, socket, push, channel): https://raw.githubusercontent.com/phoenixframework/phoenix/main/assets/js/phoenix/constants.js e socket.js
- Serializer v2 `[join_ref, ref, topic, event, payload]`: https://raw.githubusercontent.com/phoenixframework/phoenix/main/assets/js/phoenix/serializer.js
- Presence: https://phoenix.hexdocs.pm/Phoenix.Presence.html ; PubSub e ordem: https://www.erlang.org/faq/academic.html
- WebSocket global do Node 22: https://nodejs.org/api/globals.html#class-websocket
