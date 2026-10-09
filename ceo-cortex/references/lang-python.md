# Python — common mistakes

Python is the language with the most AI training data, which cuts both ways:
models write fluent Python quickly, and they reproduce every outdated idiom from
fifteen years of tutorials (Pydantic v1, `requests` without a timeout, string
SQL, `datetime.utcnow()`). The interpreter checks almost nothing before running,
type hints are not enforced at runtime, and async code fails by stalling rather
than crashing. So the rule "plausible is not correct" means: **run a type
checker and a linter, confirm the installed major version of every framework,
and trace every I/O call for a timeout and a blocking risk.** This page targets
Python 3.12+ with FastAPI or Django.

## The mental model (get this right and most bugs disappear)
- **Names are references; defaults are evaluated once.** A default argument is
  created when the `def` runs, not per call, so a mutable default is shared state.
  Assigning a list/dict to another name does not copy it.
- **Type hints are documentation the checker reads.** Python does not enforce
  them at runtime (Pydantic and similar do, at the boundary only). Without mypy or
  pyright in CI, a wrong hint is just a comment that lies.
- **Async is cooperative.** An `async def` runs on one event loop thread; any
  blocking call inside it (sync HTTP, sync DB driver, `time.sleep`, heavy CPU)
  freezes every other request on that loop. Async only helps when everything on
  the path awaits.
- **Explicit errors.** Catch the specific exception you can handle, close to
  where you can handle it. Bare `except:` and `except Exception: pass` hide bugs
  and also catch things like `KeyboardInterrupt` (bare) or cancellation.

## AI-specific Python mistakes (check these first)

### 1. Pydantic v1 API in a v2 project
- **What**: models still write v1. In v2: `.dict()` → `model_dump()`,
  `.json()` → `model_dump_json()`, `parse_obj` → `model_validate`, `parse_raw` →
  `model_validate_json`, `.copy()` → `model_copy()`, `update_forward_refs` →
  `model_rebuild`, `@validator`/`@root_validator` → `@field_validator`/
  `@model_validator`, `class Config` → `model_config = ConfigDict(...)`,
  `orm_mode` → `from_attributes`, `Field(regex=)` → `Field(pattern=)`,
  `Field(const=)` removed, and `BaseSettings` moved to the separate
  `pydantic-settings` package.
- **Detect/fix**: check the installed version first. Many v1 names still work in
  v2 but emit deprecation warnings; run tests with `-W error::DeprecationWarning`
  (or a filter for Pydantic's warning class) to surface them. `from pydantic.v1
  import ...` is a migration crutch, not a destination.

### 2. Outbound HTTP without a timeout
- **What**: `requests.get(url)`. The requests docs are explicit: by default
  requests do not time out, and the call can hang for minutes or more. Same
  pattern with `urllib`, SDK clients and DB connections.
- **Detect/fix**: always pass `timeout=` (a `(connect, read)` tuple is best,
  e.g. `(3.05, 27)`). Ruff's `S113` (flake8-bandit) flags requests calls without
  a timeout. With `httpx`, a default timeout exists but set it deliberately per
  client. In async code use `httpx.AsyncClient`, not `requests`.

### 3. Mutable default arguments
- **What**: `def add(item, items=[])` or `def f(opts={})`: every call shares the
  same list/dict, so state leaks across calls and requests.
- **Detect/fix**: default to `None` and create inside the body. Ruff `B006`
  (flake8-bugbear) catches it, but Ruff's default rule set is only `E4`, `E7`,
  `E9`, `F`, so `B` must be selected explicitly. Pydantic and dataclass fields
  need `Field(default_factory=list)` / `field(default_factory=list)`.

### 4. Blocking calls inside `async def`
- **What**: a FastAPI `async def` endpoint calling `requests`, a sync DB driver,
  `time.sleep`, or file I/O. FastAPI runs plain `def` endpoints and dependencies
  in a threadpool, but `async def` ones run on the event loop, so blocking there
  stalls the whole server.
- **Detect/fix**: if the path uses a blocking library, declare the endpoint with
  `def` (FastAPI's own guidance: "if you just don't know, use normal `def`").
  Otherwise use async clients (`httpx.AsyncClient`, asyncpg, async SQLAlchemy) or
  `await asyncio.to_thread(fn, ...)`. Ruff's `ASYNC` rules flag common blocking
  calls in async functions.

### 5. Fire-and-forget tasks that disappear
- **What**: `asyncio.create_task(send_email())` without keeping the result. The
  asyncio docs warn the loop holds only weak references, so the task "may get
  garbage collected at any time, even before it's done", and its exception is
  never seen.
- **Detect/fix**: keep a strong reference (a set plus `add_done_callback(set.
  discard)`) or use `asyncio.TaskGroup` (3.11+), which awaits children and
  propagates errors. For request-scoped background work in FastAPI use
  `BackgroundTasks`; for durable work use a real queue (Celery, RQ, arq, Dramatiq).

### 6. Outdated stdlib and typing idioms
- **What**: `typing.List`/`Dict`/`Optional[X]` in new 3.12 code, `TypeVar`
  boilerplate where PEP 695 syntax works (`def first[T](xs: list[T]) -> T`,
  `type Alias = ...`), `datetime.utcnow()` (deprecated in 3.12, returns a naive
  datetime), `asyncio.wait_for` patterns where `asyncio.timeout()` (3.11+) is
  cleaner, `os.path` string juggling where `pathlib` is the house style.
- **Detect/fix**: Ruff's `UP` (pyupgrade) rules with `target-version` set to the
  project's minimum Python; `DTZ` rules for naive datetimes. Use
  `datetime.now(UTC)`. Match the repo's existing style when it differs.

### 7. Hallucinated packages and wrong import names
- **What**: importing a module that is not a declared dependency (works locally
  because something else pulled it in), or adding a PyPI package whose name was
  guessed. The distribution name and the import name often differ
  (`pyyaml`/`yaml`, `python-dateutil`/`dateutil`), which is exactly where
  typosquats live.
- **Detect/fix**: confirm the package on PyPI (maintainer, release history)
  before adding it. Run `deptry`: DEP001 missing, DEP002 unused, DEP003
  transitive (imported but only present via another package), DEP004 dev
  dependency used at runtime, DEP005 stdlib module listed as a dependency.

## Framework and data traps

### 8. SQL injection through raw SQL
- **Wrong**: f-strings or `%` formatting into `cursor.execute`, Django
  `Model.objects.raw(...)`, `RawSQL`, `extra()`, or SQLAlchemy `text()`. Also
  quoting a placeholder (`'%s'`), which Django's docs call out as unsafe.
- **Fix**: pass parameters separately: `Person.objects.raw("... WHERE name = %s",
  [name])`, `cursor.execute(sql, [value])`, `text("... = :v")` with
  `{"v": value}`. Prefer the ORM/query builder; for dynamic identifiers (column or
  table names) use an allow-list, never user input. Ruff `S608` flags string-built
  SQL.

### 9. N+1 queries in the ORM
- **Wrong**: looping over a queryset and touching a relation per row
  (`for o in orders: o.customer.name`); serializers that walk relations lazily.
- **Fix**: Django `select_related` (FK/one-to-one) and `prefetch_related`
  (many); SQLAlchemy `selectinload`/`joinedload`. Verify with query logging,
  `django-debug-toolbar`, or `assertNumQueries` in tests.

### 10. Mass assignment and over-broad serializers
- **Wrong**: Django REST Framework `fields = "__all__"`, a ModelForm without an
  explicit field list, a FastAPI endpoint that accepts the ORM model shape and
  writes every attribute (including `is_admin`).
- **Fix**: separate input and output schemas; list writable fields explicitly;
  set privileged fields server-side.

### 11. Django settings and auth slips
- **Wrong**: `DEBUG = True` or a hardcoded `SECRET_KEY` reaching production,
  `ALLOWED_HOSTS = ["*"]`, `@csrf_exempt` added to make a form work, object
  lookups without an ownership check (`Order.objects.get(pk=pk)` for any user).
- **Fix**: settings from the environment, `python manage.py check --deploy` in
  CI, scope queries by the current user, keep CSRF on.

### 12. Exceptions swallowed or too broad
- **Wrong**: `except Exception: pass`, `except: ...`, logging and continuing
  after a failed write, catching `asyncio.CancelledError` (a `BaseException`) and
  not re-raising it.
- **Fix**: catch specific exceptions; re-raise with `raise ... from err`; let
  cancellation propagate. Ruff `BLE001`, `E722` and `S110` cover the common forms.

### 13. Unsafe deserialization and subprocess calls
- **Wrong**: `pickle.loads`/`yaml.load` on untrusted data, `subprocess.run(cmd,
  shell=True)` with interpolated input, `eval` on request data.
- **Fix**: JSON or `yaml.safe_load`; `subprocess.run([...], check=True)` with an
  argument list; no `eval`. Ruff's `S` (bandit) rules flag all of these.

## Versions (as of October 2026)
- Supported CPython: 3.14 (bugfix), then 3.13, 3.12 and 3.11
  (security fixes only, per devguide.python.org). 3.10 hit
  end of life in October 2026, 3.9 in October 2025. Python 3.14 evaluates
  annotations lazily (PEP 649), which changes code that introspects
  `__annotations__` at import time.
- Pin `requires-python` in `pyproject.toml` and set Ruff `target-version` and
  mypy/pyright `python_version` to the same floor so the tools judge the right
  syntax.

## Toolchain (let the tools catch the mechanical errors)
- **uv**: `uv lock`, `uv sync --locked` in CI (fails if the lockfile is stale);
  commit `uv.lock`. A release cooldown is available with `exclude-newer` (accepts
  durations like `"7 days"`) plus `exclude-newer-package` for exceptions.
- **Ruff** (`ruff check` + `ruff format`): select beyond the default, at least
  `B`, `UP`, `S`, `ASYNC`, `DTZ`, `BLE`, `SIM`, `I`, and `F401`/`F841` for dead
  imports and variables.
- **mypy** (`--strict` on new modules) or **pyright** (`strict` mode); pick the
  one the repo already uses. Add the Pydantic mypy plugin or rely on pyright's
  dataclass-transform support for models.
- **deptry** for missing, unused, transitive and misplaced dependencies.
- **pip-audit** against the lock or project (`pip-audit .`, `--locked` for lock
  files, `-r requirements.txt` otherwise). It exits 1 when it finds a known
  vulnerability, so it can gate CI.
- **pytest** with warnings as errors for your own deprecations; Django's
  `check --deploy` for settings.

## How to review Python here
First confirm versions: Python floor, Pydantic major, Django or FastAPI version.
Most AI Python mistakes are version mistakes. Then trace every I/O call: does it
have a timeout, and is it blocking inside `async def`? Sweep for mutable
defaults, fire-and-forget `create_task`, broad `except`, and string-built SQL.
Check boundaries: explicit input schemas, explicit writable fields, ownership
checks on object lookups. For dependencies, confirm each new package exists and
is declared (deptry), and that CI installs from the lockfile and runs pip-audit.
Record the project's conventions in cortex: sync vs async endpoints, Pydantic
major, ORM loading strategy, typing strictness, and the Ruff rule selection, so
the next edit does not reintroduce v1 APIs or blocking calls into async code.
