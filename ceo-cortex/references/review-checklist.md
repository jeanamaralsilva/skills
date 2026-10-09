# Senior Review Checklist

The lens a senior engineer applies: not "does it run?" but "would I want to own
this in two years, and does it solve the *right* problem?". Work top-to-bottom -
intent first, polish last - because a beautifully formatted function that solves
the wrong problem is still wrong.

## Table of contents
1. [Review order](#review-order)
2. [Severity language](#severity-language)
3. [The eight pillars](#the-eight-pillars)
4. [The parameter & scalability lens](#the-parameter--scalability-lens)
5. [Critical paths deserve extra scrutiny](#critical-paths)
6. [Quick pass vs deep pass](#quick-pass-vs-deep-pass)

## Review order
Mirror how strong reviewers actually read a change:
1. **Intent** - what problem is this solving? Does the change match a real
   requirement, or is it solving an imagined one? If intent is unclear, stop and
   ask; everything downstream depends on it.
2. **Skim** - is the scope reasonable? Does the structure conceptually make sense?
3. **Deep dive** - correctness, scalability, coupling, edge cases. Look at what
   *matters*, not only at what changed (a one-line change can break invariants
   established elsewhere - which is why you read the surrounding code, not just
   the diff).
4. **Polish** - naming, readability, duplication, tests, docs.

## Severity language
Classify every finding so the author knows what blocks the merge. Vague reviews
that bury a security hole next to a nit are how real defects slip through.
- **Blocking (must-fix)** - security flaws, functional defects, data loss,
  requirement violations, anything that causes an incident.
- **Should-fix** - performance problems, missing error handling, duplication,
  weak abstractions, missing tests on risky paths.
- **Nice-to-have** - style and naming preferences outside an agreed standard.
  Mark these clearly as optional; phrase as questions, not commands.

## The eight pillars
Distilled from Google/Microsoft/AWS/OWASP review practice. Use it as a sweep,
not a recitation - skip what doesn't apply.

### 1. Logic & correctness  *(the most expensive class of defect)*
- Does it do what it claims for the normal case?
- **Edge cases**: empty input, null/None, zero, negative, very large, unicode,
  duplicate keys, concurrent callers, partial failure.
- Off-by-one, boundary conditions, integer/float overflow, timezone/locale.
- Are invariants preserved? Did the change weaken a guarantee elsewhere relies on?

### 2. Error handling & resilience  *(AI omits this ~2x more than humans)*
- Are failures caught at the right layer and either handled or propagated - never
  silently swallowed (`except: pass`, empty `catch {}`)?
- Null checks, early returns, and guard clauses present on risky inputs?
- Are external calls (network, disk, DB) wrapped with timeouts and sane failure
  behavior? What happens on partial write / retry?
- No bare `console.log` / `print` / debugger statements left behind.

### 3. Security  *(amplified, not unique, in AI code)*
- Injection: SQL/NoSQL, command, XSS, template, path traversal.
- AuthN/AuthZ: is every privileged action checked? Watch for **insecure direct
  object references** (acting on an id without verifying ownership).
- Secrets in code or logs? Credentials hardcoded? (Never store these in cortex.)
- Unsafe deserialization, SSRF, weak/!default crypto, improper password handling.
- Input validated and output encoded at trust boundaries.

### 4. Performance & resource use  *(AI favors clarity over efficiency; I/O ~8x)*
- N+1 queries; query inside a loop that should be a join/batch.
- Unbounded queries, loops, or recursion on user-controlled size.
- Algorithmic complexity in hot paths (O(n²) where O(n) exists).
- Repeated I/O or recomputation that should be batched/cached.
- Resource leaks: unclosed files/sockets/cursors; missing `with`/`defer`/`finally`.

### 5. Duplication (DRY)  *(AI clones ~4x the human rate)*
- Run `dup_scan` on the touched tree. For each block it flags, decide: extract a
  shared function/module, or accept with a reason.
- Watch the subtle form: a new dependency or helper that re-implements something
  the codebase already has (a second logging package, a second date util, a
  hand-rolled function that duplicates a stdlib/lib call).
- "Copy, then tweak two lines" is the most common AI duplication - look for
  near-identical blocks, not just identical ones.
- A diff that adds or bumps a dependency is a dependency change, not just code:
  check it with the `ceo-deps` skill (SDK alignment, CVEs, license, a second lib
  for a job an existing one already does, lockfile churn).

### 6. Maintainability & design
- **Single responsibility** - does each unit do one thing?
- **Deep modules** - simple interface over meaningful implementation; avoid
  shallow wrappers that just forward calls.
- Naming matches the codebase's existing vocabulary (see pillar 8).
- Reasonable function length and nesting depth; complex logic is commented with
  *why*, not *what*.
- SOLID / GRASP applied where natural - not cargo-culted.

### 7. Tests
- Do tests exist for the new behavior and for the risky edge cases?
- Do they test behavior through public interfaces, not implementation details?
- Would they actually fail if the behavior broke? (A test that always passes is
  worse than no test - it gives false confidence.)

### 8. Consistency with local conventions  *(AI's #1 readability failure)*
AI code "looks consistent but violates *local* patterns." Before approving:
- Naming, file layout, error style, logging style, import order - do they match
  the surrounding code, or just some generic default?
- Does it use the project's existing abstractions and utilities?
- Pull conventions from cortex first (`cortex search "<area> convention"`); if a
  new convention is established here, write it back.

## The parameter & scalability lens
For non-trivial functions, interrogate the signature - this is where "acts like a
senior" shows up most:
- **Every parameter must earn its place.** For each one ask: what does it do, why
  is it here, who passes it? A parameter that's always the same value, never read,
  or only threaded through to a deeper call is a smell.
- **Boolean/flag parameters** that switch behavior often signal two functions
  wearing one coat - consider splitting.
- **Would this signature survive 10x scale or a second caller?** Hardcoded limits,
  positional args that will grow, a function that secretly depends on global
  state, an interface that leaks implementation - all are scaling liabilities.
- Use `context_map` to see a symbol's reference count. **High-reference
  signatures are load-bearing**: changing them ripples across the codebase, so
  the bar for getting them right (and for not breaking them) is higher.

## Critical paths
Give auth, payments, data-mutation, APIs, and shared/core components
disproportionate attention - a defect there blasts far past the immediate change.
Routine, low-blast-radius edits can move faster.

## Quick pass vs deep pass
- **Quick pass** (small, low-risk change): intent + correctness + duplication +
  convention check. Minutes.
- **Deep pass** (core infra, new pattern, large or security-sensitive change):
  the full eight pillars + parameter/scaling lens, and read the whole affected
  module - not just the diff. For very large changes, build a `context_map`
  first so you review with the whole structure in view rather than blind.
