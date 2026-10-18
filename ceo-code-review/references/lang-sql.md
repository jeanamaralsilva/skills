# SQL & Postgres/Supabase — common mistakes

The errors that bite hardest in SQL are silent: wrong results, data leaks, and
queries that work on 100 rows and collapse on 100k. Below: the ones to check
first, with the Supabase/Postgres specifics that matter for a SaaS like FloraCRM.

## SQL (any database)

### 1. SQL injection via string-built queries  *(blocking)*
- **Wrong**: concatenating user input into SQL (`"... WHERE name = '" + name + "'"`).
- **Fix**: always parameterize (`?` / `$1` placeholders, prepared statements).
  This also handles escaping and types. No exceptions, even for internal tools.

### 2. N+1 queries
- **Wrong**: a query in a loop (load list, then one query per row for its detail).
- **Fix**: a single `JOIN`, or `WHERE id IN (...)`, or a batched fetch. One round
  trip beats N. (See the ORM-specific version in `lang-java.md` and the client
  side in `lang-react.md`.)

### 3. Missing indexes on filter/join/sort columns
- **Wrong**: `WHERE email = ?` or `JOIN ON user_id` with no index → full scans.
- **Fix**: index columns used in `WHERE`, `JOIN`, and `ORDER BY`. Verify with
  `EXPLAIN (ANALYZE)`; watch for `Seq Scan` on big tables. Don't over-index
  either - each index slows writes.

### 4. NULL semantics
- **Wrong**: `x = NULL` (never true); `NOT IN (subquery with NULLs)` (drops rows);
  `COUNT(col)` silently skipping NULLs; `=` comparisons that ignore NULL rows.
- **Fix**: `IS NULL` / `IS NOT NULL`; `COALESCE` for defaults; prefer `NOT EXISTS`
  over `NOT IN` when NULLs are possible.

### 5. Reads/writes without a transaction
- **Wrong**: multi-statement money/stock/booking changes run separately - a crash
  between them leaves half-applied state.
- **Fix**: wrap related writes in one transaction; keep transactions short.

### 6. SELECT * and unbounded queries
- **Wrong**: `SELECT *` (breaks on schema change, ships unused columns) and
  queries with no `LIMIT` on user-facing lists.
- **Fix**: name the columns you need; paginate (keyset pagination beats `OFFSET`
  on large tables).

### 7. Floating point for money
- **Wrong**: `float`/`double` for currency → rounding errors.
- **Fix**: `numeric`/`decimal` (Postgres `numeric`), or integer cents.

## Postgres / Supabase specifics

### 8. RLS disabled = your database is public  *(blocking - the #1 Supabase issue)*
Supabase auto-generates a REST API from your schema, and the anon key is embedded
in client code by design. That is only safe **if Row Level Security is on**. Tables
created via raw SQL or the SQL editor have **RLS off by default**; any such table
is readable/writable by anyone with the anon key. This is exactly the class of bug
behind CVE-2025-48757 (170+ apps leaking through the anon key).
- **Fix**: `ALTER TABLE <t> ENABLE ROW LEVEL SECURITY;` on every table in an
  exposed schema, then write explicit policies. Turn on the project toggle
  "Enable RLS on new tables". Run the Supabase Security Advisor before shipping.

### 9. RLS enabled but no policy = every query returns empty  *(silent)*
Enabling RLS with no policy denies everything. The app looks broken but throws no
error (empty results are valid). If a table "mysteriously" returns nothing after
you locked it down, you're missing a policy for that role/operation. Policies are
**ANDed** and per-operation (`SELECT`/`INSERT`/`UPDATE`/`DELETE`) - cover each.

### 10. The auth.uid() performance trap
- **Wrong**: `USING (user_id = auth.uid())` re-evaluates `auth.uid()` **per row**.
- **Fix**: `USING (user_id = (select auth.uid()))` - wrapping in a `select` lets
  Postgres evaluate it once per query (documented ~10x speedups on big tables).
  Index the column the policy filters on.

### 11. service_role key on the client  *(blocking)*
The `service_role` key bypasses all RLS (admin). It belongs only on a trusted
server. Never ship it to the browser/app or commit it. (And never store any key
in cortex.)

### 12. Over-complex policies
Deeply nested JOINs/subqueries inside policies become unmaintainable and slow
(they run on every query). Keep policies simple; push complex authorization into a
`security definer` helper function with a stable, indexed lookup.

## How to review SQL here
Trace each query for: injection (parameterized?), result correctness (NULLs,
joins), and scale (indexes, `EXPLAIN`, pagination). For Supabase, the first
question is always **"is RLS on, and is there a policy for this exact operation
and role?"** - then the `(select auth.uid())` check. Record the tenancy/RLS
decision in cortex so later changes don't silently reopen the hole.
