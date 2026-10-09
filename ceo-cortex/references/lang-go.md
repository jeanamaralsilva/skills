# Go — common mistakes

Go is small and explicit, so AI-written Go usually compiles and looks idiomatic.
The bugs hide in what the language leaves to discipline: errors are values you
can ignore, goroutines are cheap to start and easy to leak, `context` must be
threaded by hand, and the zero value of several types (nil map, nil channel,
zero `http.Client`) is either a panic or a hang waiting to happen. The language
also moves faster than training data: Go 1.22 changed loop variable semantics,
1.25 to 1.27 added APIs and vet checks models don't know. So "plausible is not
correct" here means: **read the `go` line in `go.mod`, run `go vet`,
staticcheck and govulncheck, and trace every goroutine to its exit.**

## The mental model (get this right and most bugs disappear)
- **Errors are values.** A function that can fail returns `error` last; the
  caller checks it immediately, adds context with `%w`, and returns. No
  exceptions; `panic` is for programmer errors and truly unrecoverable states.
- **Every goroutine needs an owner and an exit.** Before writing `go f()`, know
  who waits for it, how it stops (context cancellation, closed channel, done
  signal), and where its error goes.
- **`context.Context` carries cancellation and deadlines down the call tree.**
  First parameter, named `ctx`, never stored in a struct, never `nil`. If a
  function does I/O, it takes a context and passes it on.
- **Zero values are a design tool, with sharp exceptions.** A zero `sync.Mutex`
  or `bytes.Buffer` is ready to use; a nil map panics on write; a nil channel
  blocks forever; a zero `http.Client` has no timeout.

## AI-specific Go mistakes (check these first)

### 1. Ignored or context-free errors
- **What**: `result, _ := doThing()`, `defer f.Close()` on a file you wrote to
  (the write error from `Close` is lost), `return err` up five layers so the log
  says only `EOF`, or `fmt.Errorf("failed: %v", err)` which breaks
  `errors.Is`/`errors.As` because `%v` does not wrap.
- **Detect/fix**: `errcheck` (in golangci-lint's standard set) flags unchecked
  errors. Wrap with `fmt.Errorf("load user %d: %w", id, err)`; compare with
  `errors.Is`, extract with `errors.As` or the generic `errors.AsType` (Go 1.26).
  Go 1.27's vet `printf` check also flags wrapping a *pointer* to an error type
  with `%w` when the value type implements `error`, which usually breaks
  `errors.Is`.

### 2. Goroutine leaks
- **What**: a goroutine sends on an unbuffered channel nobody reads after an
  early `return`; a worker loops on `for { select { case msg := <-ch: ... } }`
  with no `ctx.Done()` case; a ticker never stopped. The Go 1.26 release notes
  use exactly this fan-out example: returning on the first error leaks every
  remaining sender.
- **Detect/fix**: give the channel enough buffer for all senders, or select on
  `ctx.Done()` in every blocking send/receive. Use `errgroup.WithContext` for
  fan-out with first-error cancellation, or `sync.WaitGroup.Go` (Go 1.25). The
  `goroutineleak` pprof profile (experimental in 1.26, generally available in
  1.27) reports goroutines blocked on unreachable primitives; `go.uber.org/goleak`
  catches leaks in tests.

### 3. Context not propagated
- **What**: `context.Background()` or `context.TODO()` created deep inside a
  request path, `http.NewRequest` instead of `http.NewRequestWithContext`, DB
  calls without the `...Context` variant, a context stored in a struct field.
- **Detect/fix**: thread `ctx` from the handler (`r.Context()`) to every I/O
  call; use `db.QueryContext`, `NewRequestWithContext`. Derive timeouts with
  `context.WithTimeout` and always `defer cancel()` (vet's `lostcancel` flags a
  missing cancel). `Background()` belongs in `main`, tests and top-level jobs.

### 4. Loop variable assumptions from before Go 1.22
- **What**: since Go 1.22, each iteration of a `for` loop has its own variable,
  but only in modules whose `go.mod` declares `go 1.22` or later. Models still add
  `v := v` shadow copies (now noise) or, worse, rely on the old shared-variable
  behavior in a module pinned to an older `go` line.
- **Detect/fix**: read the `go` directive first. On 1.22+, delete `v := v`
  copies (the `go fix` modernizers can do this). On older modules, closures and
  `&v` inside loops still capture one shared variable.

### 5. APIs newer or older than the module allows
- **What**: using `errors.AsType`, `new(expr)` (1.26), generic methods (1.27) or
  `sync.WaitGroup.Go` (1.25) in a module whose `go` line is older; or hand-rolling
  helpers the standard library now has (`slices`, `maps`, `min`/`max`,
  `strings.CutLast` in 1.27).
- **Detect/fix**: `go vet`'s `stdversion` analyzer (run by `go test` by default
  since 1.27) reports standard library symbols too new for the file's Go version.
  Run `go fix ./...` (rewritten in 1.26 around "modernizers") on a branch and
  review its diff rather than writing helpers by hand.

### 6. Hallucinated packages and module paths
- **What**: imports of plausible but non-existent modules, or the wrong major
  version path (`github.com/x/y` vs `github.com/x/y/v2`).
- **Detect/fix**: `go build` fails on missing modules, but a typosquat that
  exists will build. Check the module on pkg.go.dev (publisher, imports count,
  license), and review every new `require` line in `go.mod`.

## Core language and stdlib traps

### 7. Nil map writes and nil interfaces
- **Wrong**: `var m map[string]int; m["a"] = 1` panics (reading a nil map is
  fine, writing is not). Returning a typed nil pointer as an `error` produces a
  non-nil interface: `var e *MyErr; return e` makes `err != nil` true.
- **Fix**: `make(map[K]V)` or a composite literal; return a literal `nil` for
  the error interface.

### 8. Data races on shared state
- **Wrong**: maps written from several goroutines (maps are not safe for
  concurrent writes; the runtime may crash with "concurrent map writes"), counters
  without sync, copying a struct that contains a `sync.Mutex`.
- **Fix**: guard with a mutex owned by the type, use `sync/atomic` types, or
  confine the state to one goroutine. Run tests with `-race` in CI. vet's
  `copylocks` catches copied locks.

### 9. Slices sharing backing arrays
- **Wrong**: `b := a[:2]; b = append(b, x)` overwrites `a[2]`; returning a
  sub-slice of a large buffer keeps the whole buffer alive.
- **Fix**: full slice expression `a[:2:2]` before appending, or `slices.Clone`.

### 10. `defer` in loops and resource leaks
- **Wrong**: `for _, f := range files { fh, _ := os.Open(f); defer fh.Close() }`
  holds every file open until the function returns; `resp.Body` never closed.
- **Fix**: move the loop body into a function; always `defer resp.Body.Close()`
  after checking the error. Since Go 1.25 the compiler correctly panics when code
  uses an `os.Open` result before checking `err`, so that latent bug now crashes.

### 11. HTTP clients and servers without timeouts
- **Wrong**: `http.Get(url)` / `http.DefaultClient` (a `Client.Timeout` of zero
  means no timeout), `&http.Client{}` per request (no connection reuse), an
  `http.Server` with no `ReadHeaderTimeout` (slowloris).
- **Fix**: one shared `http.Client{Timeout: ...}` per dependency, plus a context
  deadline per request; set `ReadHeaderTimeout`, `ReadTimeout`, `WriteTimeout`
  and `IdleTimeout` on servers. Check `resp.StatusCode`; non-2xx is not an error.
  gosec flags a server without `ReadHeaderTimeout`; `bodyclose` flags unclosed
  bodies.

### 12. Injection and unsafe input handling
- **Wrong**: `fmt.Sprintf` into SQL, `exec.Command("sh", "-c", userInput)`,
  `filepath.Join(root, userPath)` without containment, `text/template` for HTML.
- **Fix**: placeholders (`db.QueryContext(ctx, "... WHERE id = $1", id)`), pass
  arguments as a slice to `exec.Command`, `os.Root` (Go 1.24+) or a prefix check
  for paths, `html/template` for HTML. `gosec` covers these.

### 13. Panics as control flow and `init()` side effects
- **Wrong**: `panic` on bad user input; `log.Fatal` inside library code (skips
  deferred cleanup); network or DB calls in `init()`.
- **Fix**: return errors; only `main` decides to exit; initialize dependencies
  explicitly in `main` and inject them.

## Versions and modules (as of October 2026)
- Go 1.27 (August 2026) and 1.26 are supported; each release is supported until
  two newer majors exist, so 1.25 and older get no security fixes.
- `go mod init` on Go 1.26+ writes the previous version (`go 1.25.0`) by default;
  check that the `go` line is what the team intends.
- Go 1.27 `encoding/json` is backed by the v2 implementation (error text may
  differ; opt out with `GOEXPERIMENT=nojsonv2`), and `go mod tidy` merges
  duplicate `require` blocks for modules on `go 1.27`. Expect unrelated diffs.

## Toolchain (let the tools catch the mechanical errors)
- `gofmt`/`goimports` and `go vet ./...` on every change; `go test -race ./...`.
- **staticcheck** (also bundled in golangci-lint; v2 merged `gosimple` and
  `stylecheck` into it).
- **golangci-lint v2**: config needs `version: "2"`; `linters.default:
  standard` enables errcheck, govet, ineffassign, staticcheck and unused;
  formatters moved to a `formatters` section; `golangci-lint migrate` converts v1
  configs. Add `gosec`, `bodyclose`, `errorlint`, `contextcheck`,
  `noctx` as the project warrants.
- **govulncheck ./...**: checks dependencies against the Go vulnerability
  database and reports only vulnerabilities your code actually reaches, with call
  stacks. Run it in CI.
- **`go mod tidy -diff`** (Go 1.23+): prints the needed changes without writing
  them and exits non-zero if `go.mod`/`go.sum` are not tidy. Use it as a CI gate.
- `go mod verify` to confirm downloaded modules match `go.sum`.

## How to review Go here
Read `go.mod` first: the `go` line decides loop semantics and which stdlib APIs
are allowed. Then trace every error (checked, wrapped with `%w`, not swallowed),
every goroutine (owner, exit path, cancellation), and every I/O call (takes
`ctx`, has a deadline, closes its body). Look for nil-map writes, shared maps
without locks, slice aliasing, and `defer` in loops. Make sure CI runs `go vet`,
`-race`, staticcheck or golangci-lint v2, govulncheck and `go mod tidy -diff`.
Record the project's decisions in cortex: error wrapping style, logging (`slog`
or other), the HTTP client and server timeout defaults, the concurrency helper
of choice (errgroup, WaitGroup.Go, worker pool), and the minimum Go version, so
the next edit doesn't drift back to pre-1.22 habits or unbounded goroutines.
