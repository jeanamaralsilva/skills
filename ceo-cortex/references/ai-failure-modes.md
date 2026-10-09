# AI Failure Modes in Code

What AI-written code gets wrong, why, and how to catch it. Grounded in
large-scale 2025-2026 studies (CodeRabbit's AI-vs-human report, the ISSRE 2025
defect study, GitClear's clone analysis). The recurring theme: AI output is
*plausible* - it compiles, it reads smoothly - which masks design and correctness
problems that surface-level review misses. Surface plausibility is the enemy.
Review the substance, not the polish.

Root cause for most of these: a model cannot hold a large codebase in its context
window, so it re-derives solutions locally instead of reusing what exists and
following established conventions. The countermeasures are: see the whole context
first (`context_map`, read full files), check mechanically for clones
(`dup_scan`), and persist conventions/decisions so they survive the window
(`cortex`).

Each entry: **what it is → why AI does it → how to detect → the fix.**

## 1. Duplication / copy-paste clones  *(~4x human rate; the #1 issue)*
- **What**: the same logic appears in multiple places (exact, or "copy then tweak
  two lines"); or a new helper/dependency re-implements something that already
  exists in the codebase or stdlib.
- **Why**: the model can't see that an equivalent already exists, so it writes a
  fresh one. Copy/paste has overtaken reuse in AI-assisted code.
- **Detect**: run `dup_scan <path>`. For the "reinvents existing code" variant,
  `context_map` + searching cortex for prior art catches it.
- **Fix**: extract one shared function/module; reuse the existing utility or
  library call; delete the duplicate. Then record the canonical helper in cortex
  so it's reused next time.

## 2. Convention drift / local-pattern violations  *(readability issues ~3x)*
- **What**: code that "looks consistent" on its own but ignores the project's
  naming, layering, error-handling, logging, or import conventions.
- **Why**: the model defaults to a generic style instead of the repo's actual one.
- **Detect**: compare against neighboring files; `cortex search "<area>
  convention"` for recorded rules.
- **Fix**: conform to the local pattern. If a convention isn't written down yet,
  capture it: `cortex remember "<rule>" --kind convention`.

## 3. Missing error handling  *(~2x more gaps than human code)*
- **What**: missing null checks, absent early returns/guard clauses, no timeouts
  on I/O, swallowed exceptions (`except: pass`, empty `catch {}`), no handling of
  partial failure. Tightly correlated with real outages.
- **Why**: the model optimizes the happy path it was asked about.
- **Detect**: trace each external call and risky input; ask "what happens when
  this is null / times out / returns an error?".
- **Fix**: add guards, handle or propagate (never silently swallow), set timeouts,
  define failure behavior.

## 4. Dead / unused code & leftover debugging  *("codigos soltos")*
- **What**: functions, parameters, imports, or variables that are never used;
  hardcoded debugging (`print`, `console.log`, `debugger`); commented-out blocks.
  AI code is measurably more prone to unused constructs than human code.
- **Why**: the model generates scaffolding "just in case" and doesn't prune it,
  and can't see that a symbol is never referenced.
- **Detect**: `context_map` shows symbols with **0 references** - prime suspects.
  Grep for `print(`/`console.log`/`debugger`. Language linters flag unused names.
- **Fix**: delete anything not used. Unreferenced ≠ automatically dead (it may be
  a public API or an entry point) - confirm, then remove. Code that isn't called
  is liability, not safety.

## 5. Over-engineering & needless abstraction
- **What**: layers, config flags, generic frameworks, and indirection for a
  problem that didn't ask for them; shallow wrappers that only forward calls.
- **Why**: models pattern-match to "enterprise-looking" code and add structure
  that signals sophistication without earning it.
- **Detect**: ask "what does this abstraction buy us *today*?". One caller behind
  a generic interface is a yellow flag.
- **Fix**: inline until a second real use case appears. Prefer the simplest design
  that solves the actual requirement.

## 6. Inefficient resource use  *(excessive I/O ~8x more common)*
- **What**: N+1 queries, I/O or recomputation inside loops, unbounded
  queries/loops, O(n²) in hot paths - because AI favors simple, clear patterns
  over efficient ones.
- **Why**: the clear-looking solution is often the inefficient one, and the model
  rarely reasons about scale unless prompted.
- **Detect**: look for queries/calls inside loops; check whether input size is
  bounded; reason about complexity on hot paths.
- **Fix**: batch/join, cache, paginate, bound the work, pick the right algorithm.

## 7. Hallucinated APIs & dependencies
- **What**: calls to functions, methods, flags, or packages that don't exist or
  don't behave as written; importing a plausible-but-wrong library.
- **Why**: the model predicts a likely-looking name; plausibility is not existence.
- **Detect**: verify every unfamiliar symbol against real docs/source; run it.
  Beware "slopsquatting" - hallucinated package names that attackers may register.
- **Fix**: replace with the real API; pin and verify dependencies; never add a
  package without confirming it exists and is the right one.

## 8. Silent / subtle logic errors  *(harder in newer models)*
- **What**: code that runs and looks right but is subtly wrong - inverted
  condition, wrong default, off-by-one, mishandled edge, incorrect business rule.
  Logic/correctness errors run ~1.75x the human rate and are the costliest to fix.
- **Why**: fluent output hides flawed reasoning; the failure is no longer a loud
  syntax error but a quiet wrong answer.
- **Detect**: don't trust that it looks right - trace the logic against the
  requirement and the edge cases; write a test that would fail if it's wrong.
- **Fix**: correct the logic and lock it with a behavior test.

## 9. Security degradation under iteration
- **What**: each "make it work / add a feature" round can quietly remove a check
  or widen exposure; improper password handling and insecure object references
  are the most common AI security patterns.
- **Why**: local edits optimize the immediate ask and lose sight of invariants.
- **Detect**: on every iteration, re-check the security pillar on the touched
  path - especially auth and data access.
- **Fix**: restore the invariant; record the security decision in cortex so later
  edits (by you or another agent) don't undo it.

## How to use this catalog in review
Don't recite all nine. Sweep, then go deep where the change lives. Always run the
mechanical checks first (`dup_scan`, `context_map`) so your attention is free for
the judgment calls - logic, design, scaling - that tools can't make.
