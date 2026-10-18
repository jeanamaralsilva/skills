# React — common mistakes

React errors are usually not crashes - they're stale values, extra renders, and
effects doing work that belongs in render. The unifying idea: **every render is a
snapshot**; functions close over the values from the render that created them. Most
hook bugs follow from forgetting that.

### 1. useEffect overuse  *(the most frequent misuse)*
`useEffect` is for synchronizing with an **external** system (network, DOM,
subscriptions), not for reacting to your own state. A good rule: useEffect should
be the exception, not the default.
- **Wrong**: deriving state in an effect - e.g. `useState(fullName)` +
  `useEffect(() => setFullName(first + ' ' + last), [first, last])`. This adds a
  render and a sync bug surface.
- **Fix**: compute during render: `const fullName = first + ' ' + last;`. If it's
  expensive, `useMemo`. Syncing a prop into state is the same anti-pattern - just
  read the prop.

### 2. Stale closures
- **Wrong**: `useEffect(() => { const id = setInterval(() => setCount(count + 1),
  1000); ... }, [])` - the callback captured `count` from the first render and
  reads `0` forever. Same bug with event listeners and async handlers.
- **Fix**: functional updater `setCount(c => c + 1)` (no dependency on `count`);
  or list the real dependencies; or use `useEffectEvent` (React 19.2) for
  non-reactive logic that needs the latest value.

### 3. Lying to the dependency array
- **Wrong**: omitting deps to "run once", or silencing the linter with
  `// eslint-disable-next-line react-hooks/exhaustive-deps`.
- **Fix**: `react-hooks/exhaustive-deps` is one of the highest-ROI rules - every
  warning is a potential stale closure. Fix the cause (functional updates, move
  values in/out, `useCallback`) rather than suppressing.

### 4. Array index as `key`
- **Wrong**: `key={index}` on a reorderable/filterable list → React reuses the
  wrong DOM/state, causing input and animation glitches.
- **Fix**: a stable, unique id from the data.

### 5. Premature / wrong useMemo & useCallback
- **Wrong**: wrapping everything "for performance"; memoizing a callback whose
  child isn't memoized (so nothing is saved); heavy deps that change every render.
- **Fix**: profile first (React DevTools Profiler). Reach for `useMemo`/
  `useCallback` only for genuinely expensive work or to keep a stable identity for
  a memoized child / effect dep. With React Compiler (React 19) much of this is
  automatic - don't hand-memoize what the compiler covers.

### 6. Fetching in useEffect without cleanup → race conditions
- **Wrong**: an async fetch in an effect with no guard; a slow earlier request
  resolves after a newer one and overwrites it.
- **Fix**: use `AbortController` (or an ignore flag) in the effect and abort in
  cleanup. Better: use a data library (TanStack Query / RTK Query) that handles
  caching, dedup, and cancellation.

### 7. Missing cleanup → leaks
- **Wrong**: subscriptions, intervals, listeners set up in an effect with no
  teardown.
- **Fix**: return a cleanup function from the effect. Don't leave unbounded
  in-memory caches growing.

### 8. Mutating state directly
- **Wrong**: `state.items.push(x); setItems(state.items)` - same reference, React
  may skip the render; subtle bugs.
- **Fix**: produce new objects/arrays (`[...items, x]`, spread for objects).

### 9. SSR hydration mismatches  *(if using SSR)*
- **Wrong**: rendering `Date.now()`, random values, or browser-only APIs during
  the initial render → server/client markup differ, React discards the server
  render.
- **Fix**: produce identical initial markup; move client-only differences into a
  `useEffect`/guard.

## How to review React here
Read each `useEffect` and ask "is this synchronizing with something external, or
should it be plain render logic / a functional update?". Check the dependency
arrays honestly. Look for index keys, direct mutation, and fetches without
cancellation. Only discuss memoization after profiling shows a real cost. For
React Native specifics (lists, Date/timezone, SQLite), see `lang-react-native.md`.
