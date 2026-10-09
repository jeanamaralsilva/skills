# Servidor Elixir/Phoenix: testes que acham o bug antes do simulador

Metade dos bugs "do app" é do servidor: broadcast duplicado, corrida de insert, job rodando duas vezes, token revogado que ainda entra. Um teste ExUnit leva segundos; o simulador leva minutos. Comece aqui quando a hipótese estiver no servidor.

## Setup que não mente

- `mix test --warnings-as-errors`; `mix test --failed` para repetir só o que quebrou; `mix test --seed 0` quando suspeitar de ordem.
- Sandbox: `Ecto.Adapters.SQL.Sandbox.mode(Repo, :manual)` no `test_helper.exs`; `setup :set_sandbox` via `Ecto.Adapters.SQL.Sandbox.start_owner!(Repo, shared: not tags[:async])` e `on_exit(fn -> Sandbox.stop_owner(pid) end)` (padrão do `phx.new` 1.8).
- Processo filho acessa o Repo (canal, GenServer, Task): `Task` e `Task.Supervisor` propagam `$callers` sozinhos; processo genérico precisa de `Sandbox.allow(Repo, self(), pid)` ou `Process.put(:"$callers", [test_pid])`. Erro "owner exited" ou "could not checkout" é isso, não é `async: false` (B06).
- Oban em teste: `config :app, Oban, testing: :manual` (ou `:inline`); `use Oban.Testing, repo: App.Repo`.

## Canais

```elixir
use AppWeb.ChannelCase   # importa Phoenix.ChannelTest

setup do
  {:ok, _, a} = AppWeb.UserSocket |> socket("user:1", %{user_id: 1}) |> subscribe_and_join(AppWeb.RoomChannel, "room:1")
  {:ok, _, b} = AppWeb.UserSocket |> socket("user:2", %{user_id: 2}) |> subscribe_and_join(AppWeb.RoomChannel, "room:1")
  %{a: a, b: b}
end

test "pergunta chega aos dois e só uma vez", %{a: a} do
  ref = push(a, "create_question", %{"text" => "2+2?"})
  assert_reply ref, :ok, %{id: id}
  assert_push "question_created", %{id: ^id}
  assert_push "question_created", %{id: ^id}
  refute_push "question_created", _, 200
end

test "join rejeitado sem token válido" do
  assert {:error, %{reason: "unauthorized"}} =
           AppWeb.UserSocket |> socket("user:9", %{}) |> subscribe_and_join(AppWeb.RoomChannel, "room:1")
end

test "reconexão: join/3 recria o estado" do
  # derrubar o canal e entrar de novo
  Process.unlink(a.channel_pid); Process.exit(a.channel_pid, :kill)
  {:ok, reply, _} = AppWeb.UserSocket |> socket("user:1", %{user_id: 1}) |> subscribe_and_join(AppWeb.RoomChannel, "room:1", %{"last_seen_id" => 10})
  assert %{missed: [_ | _]} = reply   # o join devolve o que o cliente perdeu (B43)
end
```

`connect/3` testa o `UserSocket.connect` (token expirado → `:error`, B20). Logout remoto: `AppWeb.Endpoint.broadcast("user_socket:1", "disconnect", %{})` e o socket de A cai (B21).

## Corridas

```elixir
test "50 matrículas simultâneas: exatamente uma vence" do
  results = 1..50 |> Task.async_stream(fn _ -> Rooms.enroll(user, room) end, max_concurrency: 50, timeout: 10_000) |> Enum.map(fn {:ok, r} -> r end)
  assert Enum.count(results, &match?({:ok, _}, &1)) == 1
  assert Enum.all?(results, fn r -> match?({:ok, _}, r) or match?({:error, %Ecto.Changeset{}}, r) end)   # nunca raise Ecto.ConstraintError (B04)
end
```

Lost update (B05): dois `Task` leem o mesmo registro, dormem 50 ms, gravam; o valor final tem que refletir as duas escritas ou a segunda falhar com `Ecto.StaleEntryError` (`optimistic_lock`). Sem isso, o teste passa por sorte: rode com `--repeat-until-failure 20` (ExUnit 1.17+).

Idempotência (B02, B03): mesma `Idempotency-Key` duas vezes → mesma resposta, um efeito; mesma chave com payload diferente → 422; duas em paralelo → segunda recebe 409 ou espera.

## Jobs

```elixir
use Oban.Testing, repo: App.Repo

test "lembrete enfileirado uma vez por aula" do
  Rooms.schedule_reminder(room); Rooms.schedule_reminder(room)
  assert [_] = all_enqueued(worker: ReminderWorker, args: %{room_id: room.id})   # unique só vale no insert (B07)
end

test "perform duas vezes = um push" do
  assert :ok = perform_job(ReminderWorker, %{room_id: room.id})
  assert :ok = perform_job(ReminderWorker, %{room_id: room.id})
  assert_push_sent_once()   # seu helper; o worker precisa checar "já enviado" (B08)
end
```

`Oban.drain_queue(queue: :default, with_scheduled: true)` roda o que está na fila em modo `:manual`.

## Propriedades (StreamData)

```elixir
use ExUnitProperties
property "parse de resposta aceita qualquer texto imprimível" do
  check all text <- string(:printable, max_length: 2000), max_runs: 200 do
    assert {:ok, _} = Answers.parse(%{"text" => text})
  end
end
```

Entradas que o cliente digita e ninguém testou: emoji composto, RTL, 2000 caracteres, só espaços, `null` como string. `check all` com `integer()`, `float()`, `member_of([...])` para números com vírgula e fuso (B30 a B32).

## Fuso e tempo

- O servidor guarda UTC (`:utc_datetime_usec`) e converte na borda. Teste com `DateTime.shift_zone!/2` para `America/Manaus` e `Europe/Lisbon` (tzdata configurado: `config :elixir, :time_zone_database, Tzdata.TimeZoneDatabase`).
- DST: `DateTime.from_naive(~N[2026-03-29 02:30:00], "Europe/Lisbon")` retorna `{:gap, _, _}`; hora repetida retorna `{:ambiguous, _, _}`. O código trata os dois? (B31)
- Ordem de eventos: número de sequência por sala (`Postgres sequence` ou contador no processo da sala), não `inserted_at` (B44).

## Sobelow e segurança básica do canal

`mix sobelow --exit medium` antes de release. No canal: `join/3` checa se o usuário pode entrar naquela sala (não só se está logado); `handle_in` valida o payload com changeset; IDs vindos do cliente são comparados com `socket.assigns` (autorização por objeto, TR18).

## Fontes

- Phoenix.ChannelTest: https://phoenix.hexdocs.pm/Phoenix.ChannelTest.html ; https://phoenix.hexdocs.pm/testing_channels.html
- Sandbox e `$callers`: https://ecto-sql.hexdocs.pm/Ecto.Adapters.SQL.Sandbox.html ; https://elixir.hexdocs.pm/Task.html#module-ancestor-and-caller-tracking
- Constraints e upserts: https://ecto.hexdocs.pm/constraints-and-upserts.html
- Oban.Testing: https://oban.hexdocs.pm/Oban.Testing.html ; https://oban.hexdocs.pm/testing.html ; unique: https://oban.hexdocs.pm/unique_jobs.html
- StreamData: https://stream-data.hexdocs.pm/ExUnitProperties.html
- DateTime gaps: https://elixir.hexdocs.pm/DateTime.html
- Idempotency-Key: https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-idempotency-key-header
