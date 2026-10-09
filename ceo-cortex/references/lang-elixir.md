# Elixir — common mistakes

Elixir is where AI assistants are least reliable and where habits from
object-oriented/imperative languages do the most damage. It has comparatively
little training data, so models hallucinate functions, reach for outdated APIs,
and quietly import patterns from other languages. And its core ideas -
immutability, pattern matching, processes, "let it crash" - are easy to use
*syntactically* while getting the *semantics* subtly wrong. So here the rule
"plausible is not correct" matters most: **verify every unfamiliar symbol against
current hexdocs and let the compiler talk** before trusting Elixir code.

## The mental model (get this right and most bugs disappear)
- **Immutability + rebinding.** `x = 2` rebinds the name; it never mutates data.
  Functions return *new* data (`Map.put/3`, `List.delete/2` give you a new
  structure) - the original is unchanged. Use the pin `^x` to match a variable's
  current value instead of rebinding.
- **Processes model runtime properties, not code.** Use a process (GenServer,
  Agent, Task) only for state, concurrency, or failure isolation - never to
  "organize" code. Plain functions in a module are the default.
- **Errors: tagged tuples + "let it crash", not exceptions everywhere.** Model
  *expected* failure as `{:ok, value}` / `{:error, reason}` and branch with
  `case`/`with`/pattern matching. Reserve crashing (and supervision) for the
  *unexpected*. `try/rescue` on every call is an anti-pattern ported from other
  languages.

## AI-specific Elixir mistakes (check these first)
LLMs have limited Elixir training data; treat generated Elixir as a draft to
verify, not a source of truth.

### 1. Hallucinated / non-existent functions
- **What**: calls to functions or arities that don't exist (`Enum.find_index_by`,
  a made-up `Map.deep_merge`, wrong arity on a real function).
- **Detect/fix**: the **compiler is your friend** - undefined functions are
  compile errors and "function is undefined or private" warnings. Run
  `mix compile --warnings-as-errors`. Confirm the exact name/arity in current
  hexdocs (`h Module.fun/arity` in IEx). Don't add a Hex dep without confirming
  it exists and is current (slopsquatting risk).

### 2. Other-language constructs smuggled in
- **What**: `async/await` thinking from JS or thread/lock thinking from
  Python/Java applied to `Task`/`GenServer`; mutable-loop logic; OO "manager
  objects" rebuilt as needless GenServers.
- **Fix**: use `Task.async/await` or `Task.async_stream` for concurrency,
  `Enum`/`Stream`/recursion instead of mutating loops, and plain functions
  instead of state-holding processes. If the code reads like Java with `def`,
  rewrite it in idiomatic Elixir (pipelines, pattern matching, small functions).

### 3. Outdated / deprecated APIs
- **What**: `Logger.warn/1` (deprecated in Elixir 1.15 → `Logger.warning/1`);
  `String.strip` / `String.rstrip` (→ `String.trim/*`); `Enum.chunk` (→
  `Enum.chunk_every`); `use Mix.Config` (→ `import Config`); Phoenix `~L`/EEx
  templates and `Phoenix.View` (→ HEEx `~H` and function components in Phoenix
  1.7+). Models trained on old code reproduce these.
- **Fix**: heed deprecation warnings (don't silence them); verify against the
  hexdocs for the exact Elixir/Phoenix version the project uses, since the
  current idiom changes across versions.

### 4. Near-miss semantics
- **What**: compiles and looks right but the logic is subtly off - a `case` that
  doesn't cover a clause, a pipeline passing the wrong shape, an `Enum.reduce`
  with the accumulator argument order swapped.
- **Fix**: trace the data through the pipeline; add an ExUnit test that would fail
  if it's wrong; lean on Dialyzer for type discrepancies.

## Core language logic errors

### 5. Function/`case` clause order
- **Wrong**: a broad clause before a specific one - `def f(x)` above `def f(nil)`
  means `f(nil)` never runs (the first clause matches everything). Same with
  `case`.
- **Fix**: order clauses **specific → general**; put guards/literal patterns
  first, the catch-all last.

### 6. `%{}` matches any map
- **Wrong**: `def f(%{})` to mean "empty map" - it matches *every* map, since map
  patterns match a subset of keys.
- **Fix**: guard on emptiness (`when map_size(m) == 0`) or match the specific keys
  you need (`%{id: id}`).

### 7. `==` vs `===`, and value vs identity
- **Wrong**: assuming `1 == 1.0` is false (it's true); using `==` where you need
  strict equality.
- **Fix**: `===` for strict (type-sensitive) comparison; know that `==` coerces
  numbers.

### 8. Charlists vs strings, keyword lists vs maps
- **Wrong**: confusing `'foo'` (charlist - a list of integers, often from Erlang
  libs) with `"foo"` (binary string); treating a keyword list like a map (it's an
  ordered list of `{atom, value}` allowing duplicate keys).
- **Fix**: use `"..."` strings in Elixir; convert charlists with `to_string/1`.
  Use maps for lookups; keyword lists for options/DSLs where order and duplicates
  matter. Don't `Map`-index a keyword list.

### 9. `String.to_atom/1` on user input  *(security - atom exhaustion)*
- **Wrong**: turning request params/external data into atoms. Atoms are **not
  garbage-collected**; unbounded creation crashes the VM (DoS).
- **Fix**: keep external keys as strings, or use `String.to_existing_atom/1`
  against a known set.

### 10. Errors in guards fail silently
- **Wrong**: a guard that raises (e.g. a non-allowed function, a type error) does
  not error - it just makes the clause *not match*, so you fall through to the
  wrong branch.
- **Fix**: keep guards to guard-safe expressions; when behavior is surprising,
  check whether a guard is silently failing.

### 11. Enum (eager) vs Stream (lazy)
- **Wrong**: chaining several `Enum` calls over a large collection builds a new
  full list at each step; running `Enum` over a huge/infinite source.
- **Fix**: use `Stream` for large or composed pipelines (lazy, single pass), then
  a final `Enum`/`Stream.run`. For small collections, `Enum` is fine and clearer.

## OTP & processes

### 12. GenServer as a bottleneck
- **Wrong**: routing lots of work through one GenServer. It processes **one
  message at a time**, so calls queue behind each other - throughput collapses and
  callers hit timeouts.
- **Fix**: use the GenServer for coordination/state only; offload heavy work to
  `Task`/`Task.async_stream`, run a pool, or use ETS for shared reads. Don't put
  pure logic behind a process.

### 13. Heavy/blocking work inside a callback
- **Wrong**: a slow call (HTTP, big computation) inside `handle_call` blocks the
  process and every queued caller; `GenServer.call` defaults to a **5s timeout**,
  after which the *caller* crashes. A missing `handle_call` clause crashes both
  caller and server.
- **Fix**: keep callbacks short; do slow work in a `Task` and reply later, or use
  `handle_cast`/`handle_info`; set explicit timeouts deliberately; cover all
  expected messages.

### 14. Unsupervised or mis-supervised processes
- **Wrong**: `GenServer.start/3` (or a bare `spawn`) for something that should be
  supervised → no restart on crash; wrong restart strategy/child spec.
- **Fix**: start under a supervision tree with `start_link` and an appropriate
  strategy (`:one_for_one`, etc.) and restart type (`:permanent`/`:transient`/
  `:temporary`). Let supervisors handle the unexpected.

## Ecto & Phoenix

### 15. N+1 queries via lazy preloads
- **Wrong**: loading a list then accessing associations per row (or `Repo` calls
  in a loop) → one query per record.
- **Fix**: `Repo.preload/2` up front, `preload:` in the query, or a `join` +
  `preload`. Verify by watching the logged SQL.

### 16. Forgetting cast_assoc/put_assoc on nested data
- **Wrong**: a parent changeset that omits `cast_assoc(:children)` (or
  `put_assoc`) silently drops the child changes; mismatched field types between
  migration and schema.
- **Fix**: `cast_assoc`/`put_assoc` for nested associations; keep migration and
  schema types aligned; handle `{:error, changeset}` everywhere a write can fail.

### 17. Mass assignment via a permissive cast
- **Wrong**: `cast(params, [:role, :is_admin, ...])` letting users set fields they
  shouldn't (privilege escalation).
- **Fix**: cast only user-settable fields; set sensitive fields server-side. This
  is the Elixir form of the mass-assignment anti-pattern.

### 18. SQL injection via raw queries / interpolation
- **Wrong**: interpolating input into `Ecto.Adapters.SQL.query!`/`fragment`
  strings. The Ecto query DSL parameterizes for you, but raw SQL doesn't.
- **Fix**: use the query DSL or parameterized fragments (`fragment("... = ?", ^v)`);
  never interpolate user input into SQL.

### 19. Uniqueness without a DB constraint, and pool/connection issues
- **Wrong**: relying only on `validate_*` for uniqueness (race condition);
  default pool size under load; long queries holding connections.
- **Fix**: add a DB unique index + `unique_constraint/3`; size the Repo pool and
  set query timeouts for the workload.

### 20. LiveView: heavy work and bloated socket
- **Wrong**: expensive work in `mount`/`handle_event` blocking the LiveView
  process; assigning large datasets into the socket (memory per connection); N+1
  in `render`.
- **Fix**: keep callbacks fast (offload to `Task`/`start_async`); assign only
  what the view needs (streams for big collections); preload before assigning.

## Toolchain (let the tools catch the mechanical errors)
- `mix compile --warnings-as-errors` - undefined functions, unused vars, many
  near-misses.
- `mix format` - canonical formatting (no style debates).
- **Credo** - style and many of the documented anti-patterns.
- **Dialyzer** (`:dialyxir`) with typespecs - type discrepancies and impossible
  patterns.
- **ExUnit** - behavior tests; `doctest` keeps examples honest.
- Official **anti-patterns guide** on hexdocs (code / design / process / meta) is
  the authoritative reference - cite it when justifying a refactor.

## How to review Elixir here
Start by assuming unfamiliar functions may be hallucinated - **compile with
warnings-as-errors and verify symbols in hexdocs**. Then check the mental-model
basics: is data being treated as immutable (not "mutated")? Are there processes
that should just be functions? Is failure handled with tagged tuples and `with`,
crashing only on the unexpected? Sweep clause ordering, `%{}`/map matching,
`==`/`===`, charlist/string and keyword/map mix-ups, and `String.to_atom` on
input. For OTP, look for single-GenServer bottlenecks and blocking callbacks. For
Ecto/Phoenix, hunt N+1 preloads, missing `cast_assoc`, permissive casts, raw-SQL
interpolation, and heavy LiveView callbacks. Record the project's idioms and
version-specific conventions (Phoenix/LiveView version, error-handling style) in
cortex - in a low-resource language for LLMs, captured conventions are what keep a
later edit from drifting back to non-idiomatic or deprecated code.

## Phoenix agent Iron Laws (from phxagents)
A compact checklist of non-negotiable rules for agent-written Phoenix code, from
the Iron Laws at https://phxagents.dev/iron-laws/ by Oliver Kriska
(https://github.com/oliver-kriska/claude-elixir-phoenix, MIT). Numbers match the
original list. The full plugin, with workflow commands and reviewers built on
these laws, installs in Claude Code with
`/plugin marketplace add oliver-kriska/claude-elixir-phoenix` and then
`/plugin install elixir-phoenix`.

**LiveView**
- 01. No unconditional DB query in `mount` (it runs twice); use `assign_async`.
- 02. Use streams for lists over ~100 items; plain assigns cost memory per user.
- 03. Check `connected?/1` before `PubSub.subscribe`, or you subscribe twice.
- 18. When a save shows no error and no effect, inspect `{:error, changeset}`
  before debugging the UI.
- 21. Never `assign_new` for values recomputed each mount (locale, current
  user); use `assign/3`.
- 24. Match `{:error, %Ecto.Changeset{}}` explicitly and handle other errors
  separately, so form errors still render.

**Ecto**
- 04. Never `:float` for money; use `:decimal` or integer cents.
- 05. Always pin with `^` in queries; never interpolate user input.
- 06. Separate queries (preload) for `has_many`, JOIN for `belongs_to`, to avoid
  row multiplication.
- 15. No implicit cross join: multiple sources in `from` without `on:` is a
  Cartesian product.
- 17. Deduplicate shared child records before `cast_assoc`.
- 19. Hidden inputs for every required embedded field the form doesn't edit.

**Oban**
- 07. Jobs must be idempotent (safe to retry).
- 08. Args use string keys; pattern match on `"user_id"`, not `:user_id`.
- 09. Store IDs in args, never structs.

**Security**
- 10. No `String.to_atom/1` on user input (atom exhaustion).
- 11. Authorize in every `handle_event`; authorizing in `mount` is not enough.
- 12. Never `raw/1` with untrusted content (XSS).

**OTP**
- 13. No process without a runtime reason (state, concurrency, isolation).
- 14. Supervise every long-lived process.

**Elixir and project hygiene**
- 16. Declare `@external_resource` for files read at compile time.
- 20. Wrap third-party library APIs in a project-owned module.
- 23. Mix tasks start only what they need:
  `Mix.Task.run("app.config")` plus `Application.ensure_all_started/1`, not
  `app.start`.
- 25. Capture the Gettext/CLDR locale before spawning; it is process-local, so
  pass it to Tasks and GenServers.

**Verification and style**
- 22. Verify with `mix compile && mix test` and show the result before claiming
  done, or state what remains unverified.
- 26. Rationale goes in the commit or PR, not in code comments; comments keep
  only durable facts.

## Dependency hygiene (Hex)
- `mix hex.audit`: checks the lockfile for retired packages and, since Hex 2.5,
  packages with security advisories; exits non-zero on either, so it can gate CI.
- `mix deps.audit` (from `mix_audit`): checks dependencies against the Elixir
  security advisory database.
- `mix hex.outdated --within-requirements`: exits non-zero only when an update
  is available inside the `mix.exs` requirement (plain `hex.outdated` fails on
  any newer version).
- `mix deps.unlock --check-unused`: fails if `mix.lock` has entries no longer
  used; `mix deps.unlock --unused` cleans them.
- Release cooldown (Hex 2.5): `hex: [cooldown: "7d"]` in `mix.exs` (or
  `HEX_COOLDOWN` / `mix hex.config cooldown 7d`) skips releases younger than the
  window during new resolution. It does not touch versions already locked, and it
  is lifted for a locked version that is retired or has an advisory.
- Git dependencies pinned with `ref:` to a full commit SHA, never a branch.
- Elixir/OTP compatibility: 1.20 supports OTP 27 to 29; 1.19, 26 to 28; 1.17 and
  1.18, 25 to 27; 1.15 and 1.16, 24 to 26. Check `.tool-versions`, CI and the
  release image agree.
- `req` must be 0.6.1 or later: earlier versions decompress response bodies with
  no size limit (decompression bomb, GHSA-655f-mp8p-96gv / CVE-2026-49755).
- For a full dependency audit (outdated, retired, vulnerable, unused, license and
  maintenance signals) use the `ceo-deps` skill.
