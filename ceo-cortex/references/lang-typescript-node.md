# TypeScript & Node.js — common mistakes

TypeScript on Node is the stack where AI output looks most finished and is least
checked. The type system is unsound by design (`any`, `as`, non-null `!`), the
compiler only checks what you let it, and types vanish at runtime, so a
"type-safe" handler can still accept any JSON a client sends. Add a module
system split (ESM vs CommonJS), an async model where a forgotten `await` is not
an error, and a registry that has been the target of self-replicating malware,
and the rule "plausible is not correct" applies in full: **let `tsc` and
type-aware lint speak, validate every boundary at runtime, and treat every new
dependency as untrusted code.**

## The mental model (get this right and most bugs disappear)
- **Types are compile-time only.** Nothing in a type annotation runs. Data from
  HTTP, queues, files, env vars and `JSON.parse` is `unknown` until a runtime
  validator (Zod, Valibot, ArkType, a JSON Schema validator) has parsed it.
  `as User` is an assertion you made, not a check the program performed.
- **Every escape hatch disables the checker locally.** `any`, `as`, `!`,
  `// @ts-ignore` and `// @ts-expect-error` each say "trust me". A diff that adds
  them is a diff that removed type safety; ask what invariant justifies it.
- **A promise is a value, not an action you wait on.** An un-awaited promise
  keeps running, its rejection goes nowhere you handle it, and in current Node an
  unhandled rejection crashes the process by default. Errors only propagate
  through `await`/`return`.
- **Node is single-threaded for your JS.** CPU work or sync I/O (`readFileSync`,
  `crypto.pbkdf2Sync`, a huge `JSON.parse`) inside a request handler blocks every
  other request on that process.

## AI-specific TypeScript/Node mistakes (check these first)

### 1. Escape hatches to make the compiler quiet
- **What**: `as any`, `as unknown as T`, `x!`, `@ts-ignore`, or `Record<string,
  any>` added to get a build green; `catch (e: any)` and then `e.message`.
- **Detect/fix**: enable `strict` (plus `noUncheckedIndexedAccess` and
  `exactOptionalPropertyTypes` where the codebase can take it). typescript-eslint's
  `no-explicit-any`, `no-unsafe-*` and `no-non-null-assertion` rules flag these.
  Replace with a real type, a type guard, or a runtime parse. In `catch`, the
  value is `unknown`: narrow with `instanceof Error` before reading `.message`.

### 2. Trusting types at the boundary
- **What**: `const body = req.body as CreateUser`, `JSON.parse(raw) as Config`,
  `process.env.PORT!` used as a number. Compiles, then fails or misbehaves on the
  first malformed input, and is a mass-assignment vector if the object is spread
  into a DB write.
- **Detect/fix**: parse at every trust boundary (request body/query/params,
  webhook payloads, env, third-party API responses, queue messages) with a schema
  and derive the type from it (`type CreateUser = z.infer<typeof CreateUser>`).
  Use `safeParse` and return a 400 on failure. Parse env once at startup and fail
  fast.

### 3. Floating promises and async misuse
- **What**: calling an async function without `await` (`saveAudit(evt);`),
  `array.forEach(async ...)` (nothing awaits the callbacks), an async function
  passed where a sync callback is expected (`if (isAllowed())` on a promise is
  always truthy), sequential `await` in a loop over independent items.
- **Detect/fix**: turn on `@typescript-eslint/no-floating-promises` and
  `no-misused-promises` (both need type-aware linting; they are in
  `recommended-type-checked`). Use `await Promise.all(items.map(...))` (or a
  bounded-concurrency helper for large lists), `for...of` with `await` when order
  matters. Note `void promise` silences the rule but does not handle the
  rejection.

### 4. Zod version drift (v3 vs v4)
- **What**: Zod 4 changed the API and models still write Zod 3. Deprecated or
  removed in v4: `message:` (now `error:`), `required_error`/`invalid_type_error`,
  `z.string().email()` (now `z.email()`), `.strict()`/`.passthrough()` (now
  `z.strictObject()`/`z.looseObject()`), `.merge()` (use `.extend()`),
  single-argument `z.record(v)`, `err.errors`/`.formErrors` (use `.issues`),
  `.flatten()`/`.format()` (use `z.treeifyError()`). `.default()` semantics also
  changed (`.prefault()` keeps the old one).
- **Detect/fix**: check the installed major in `package.json`/lockfile before
  judging a schema, and verify against the Zod changelog for that version.

### 5. Hallucinated or outdated tsconfig and compiler behavior
- **What**: TypeScript 6.0 made `strict: true`, `module: esnext` and `types: []`
  the defaults, deprecated `target: es5`, `moduleResolution: node` (node10) and
  `baseUrl`, removed `moduleResolution: classic` and `outFile`, and no longer
  allows `esModuleInterop: false`. TypeScript 7.0 (the native Go compiler, out in
  2026) turns 6.0's deprecations into hard errors. AI configs routinely still use
  `"moduleResolution": "node"`, `baseUrl` path roots and `es5` targets.
- **Detect/fix**: read the project's TypeScript version first. For Node use
  `module`/`moduleResolution: nodenext`; for bundled apps `bundler`. If
  `types: []` is now the default, `@types/node` globals need `"types": ["node"]`.
  Note that tools built on the compiler API (typescript-eslint, some framework
  tooling) did not support 7.0 at its release; check before bumping.

### 6. ESM/CJS confusion
- **What**: `require` in an ESM file, `__dirname` in ESM, extensionless relative
  imports under `nodenext`, `"type": "module"` added without updating imports, a
  dual package published with mismatched `exports`.
- **Detect/fix**: know which one the package is (`"type"` in `package.json`,
  `.mjs`/`.cjs`). In ESM use `import.meta.dirname`/`import.meta.filename` and
  full relative paths with extensions. Modern Node can `require()` a synchronous
  ES module (unflagged since 20.19/22.12), but it throws
  `ERR_REQUIRE_ASYNC_MODULE` if the graph has top-level `await`; use `import()`
  there.

### 7. Running `.ts` directly and assuming it is type-checked
- **What**: Node strips TypeScript types natively (on by default since 22.18 and
  23.6, stable in 24.12/25.2), and AI treats `node app.ts` as "it compiles".
  Stripping does **no** type checking, ignores `tsconfig.json` (including
  `paths`), needs explicit `.ts` extensions and `import type`, and rejects enums,
  runtime namespaces and parameter properties.
- **Detect/fix**: CI must still run `tsc --noEmit`. If the project runs `.ts`
  directly, set `erasableSyntaxOnly` and `verbatimModuleSyntax` so the compiler
  flags what Node will reject.

## Ecosystem traps

### 8. `fetch` and outbound I/O without a deadline
- **Wrong**: `await fetch(url)` with no signal. Node's fetch (undici) waits up to
  300s for headers and 300s between body chunks by default, so a slow upstream
  ties up requests for minutes.
- **Fix**: `fetch(url, { signal: AbortSignal.timeout(5_000) })`; combine with a
  caller's cancellation via `AbortSignal.any([req.signal, AbortSignal.timeout(n)])`.
  Same for DB clients, Redis, queues: set connect and query timeouts explicitly.
  Check `res.ok`; fetch does not reject on 4xx/5xx.

### 9. Error handling that loses information or leaks it
- **Wrong**: empty `catch {}`, `catch (e) { throw new Error("failed") }` (cause
  lost), returning `err.stack` or DB errors to the client, no handler for
  `unhandledRejection`/`uncaughtException` at the process edge.
- **Fix**: rethrow with `new Error("msg", { cause: err })`; map known errors to
  responses in one middleware; log details server-side only; on an uncaught error
  log and exit so the supervisor restarts a clean process.

### 10. Injection and unsafe dynamic code
- **Wrong**: template-string SQL (`` `... WHERE id = ${id}` ``), `child_process.exec`
  with interpolated input, `eval`/`new Function`, `path.join(base, userInput)`
  without checking the result stays under `base`, object spread of user input
  into a merge (prototype pollution via `__proto__`).
- **Fix**: parameterized queries or the query builder's bindings; `execFile`/
  `spawn` with an argument array; resolve then verify the path prefix; validate
  input with a strict schema before merging. OWASP's Node.js and Injection cheat
  sheets are the references.

### 11. Blocking the event loop
- **Wrong**: `*Sync` fs/crypto calls in request paths, CPU-heavy loops, giant
  synchronous `JSON.parse`/`stringify` on hot paths.
- **Fix**: async APIs; move CPU work to `worker_threads` or a job queue; stream
  large payloads.

### 12. Supply chain: install scripts, lockfiles, fresh releases
- **Wrong**: `npm install` in CI (rewrites the lockfile), no lockfile committed,
  lifecycle scripts running for every transitive dependency, adding a package the
  model "remembers" without checking it exists, upgrading to a version published
  an hour ago. The 2025 Shai-Hulud worm compromised hundreds of npm packages by
  stealing maintainer tokens and republishing infected versions; CISA's guidance
  was to pin to known-good versions, rotate credentials and require
  phishing-resistant MFA.
- **Fix**: commit the lockfile; CI uses `npm ci` (fails if `package.json` and
  the lockfile disagree). Prefer `npm ci --ignore-scripts` and allow-list the few
  packages that genuinely need a build step. Use a release cooldown
  (`min-release-age=<days>` in `.npmrc` on npm 11.10+, or the equivalent in pnpm/
  Renovate/Dependabot). Restrict git dependencies (`allow-git`). Run `npm audit`
  and review new transitive deps in the lockfile diff.

## Runtime and version facts (as of October 2026)
- Node 24 and Node 22 are the LTS lines; Node 20 is end of life (its last release
  shipped in March 2026); Node 26 is Current. Production should run an LTS line; pin it in
  `engines` and `.nvmrc`/`.node-version` and match CI and the container image.
- From Node 27 the project moves to one major release per year, each becoming
  LTS. Don't assume odd versions are throwaway after that.
- `fetch`, `AbortSignal.timeout`, `AbortSignal.any`, `structuredClone` and the
  test runner (`node:test`) are built in; adding `node-fetch`, `abort-controller`
  or similar polyfills to a modern Node service is dead weight.

## Toolchain (let the tools catch the mechanical errors)
- `tsc --noEmit` (or `tsc -b` for project references) in CI, separate from the
  bundler or runner, which usually strips types without checking them.
- **typescript-eslint** with `recommended-type-checked` (or `strict-type-checked`)
  and `parserOptions.projectService: true`; the promise and `no-unsafe-*` rules
  only work with type information.
- **knip** for unused files, exports, dependencies, unlisted dependencies and
  unresolved imports (`knip --production` to check only shipped code). This is the
  JS/TS answer to the "dead code" failure mode.
- `npm ci --ignore-scripts`, `npm audit`, and a cooldown setting for supply
  chain; `npm ls <pkg>` / `npm explain <pkg>` to see why something is installed.
- Tests with `node:test`, Vitest or Jest; add a test that sends a malformed body
  to every validated endpoint.

## How to review TypeScript/Node here
Start with what the compiler and linter cannot see: is every external input
parsed at runtime, and does every outbound call have a timeout? Then grep the
diff for `any`, `as `, `!`, `@ts-ignore` and `eslint-disable` and demand a
reason for each. Check every async call is awaited, returned or deliberately
handled, and that loops over independent work use `Promise.all` with a bound.
Confirm the module system, the TypeScript major and the Zod major before judging
imports, tsconfig or schemas, because models mix versions. For any new
dependency, check that it exists, is maintained, is actually needed (knip), and
arrives through `npm ci` with scripts off. Record the project's choices in
cortex: Node LTS line, ESM vs CJS, validation library and version, the error
response shape, and the timeout defaults. Those are exactly what a later edit
silently drifts away from.
