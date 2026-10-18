# React Native & Expo — common mistakes

All the React hook rules in `lang-react.md` apply here - read that first. This
page adds the React Native/Expo-specific traps, weighted toward what matters for a
scheduling app like Calendary: lists, dates/timezones, and the move from in-memory
data to expo-sqlite.

### 1. Date & timezone bugs  *(the classic scheduling-app footgun)*
JavaScript `Date` is the single biggest source of off-by-one-day and wrong-time
bugs in calendar apps.
- **Wrong**: `new Date("2026-08-09")` parses as **UTC midnight**, so in a UTC-3
  zone (São Paulo) it displays as Aug 8, 21:00 - the day before. Doing date math
  with `getHours()`/`setDate()` mixes local and UTC and drifts. Comparing a
  date-only value to a timestamp.
- **Fix**: be explicit about whether a value is a calendar date or an instant.
  Store instants as UTC ISO strings; for date-only, construct with explicit local
  components (`new Date(y, m-1, d)`) or keep a `YYYY-MM-DD` string and never let
  it round-trip through UTC. Use a dedicated library (`date-fns` /
  `date-fns-tz`, Luxon, or Temporal) for arithmetic and zone conversion. Test on a
  device whose timezone is **not** the dev machine's, and around DST boundaries.

### 2. Lists: ScrollView for long data, or unoptimized FlatList
- **Wrong**: rendering a long list with `ScrollView` + `.map` (renders everything
  → memory blowup); `FlatList` with an inline `renderItem`/`keyExtractor`
  recreated each render and unmemoized rows.
- **Fix**: `FlatList` (or Shopify's `FlashList` for large/heavy lists) with a
  stable `keyExtractor`, a `React.memo`'d row, and a hoisted `renderItem`. Tune
  `initialNumToRender`, `maxToRenderPerBatch`, `windowSize`. Virtualization can't
  rescue an expensive row - make the row cheap first.

### 3. expo-sqlite: string-built queries
- **Wrong**: interpolating values into SQL (`\`...WHERE id=${id}\``) - injection
  and escaping bugs even locally.
- **Fix**: parameterize with `?`:
  `db.runAsync('INSERT INTO students (name) VALUES (?)', [name])`,
  `db.getAllAsync('SELECT * FROM lessons WHERE day = ?', [day])`.

### 4. expo-sqlite: no migration strategy  *(critical when leaving fake data)*
Moving from in-memory/fake data to SQLite, the schema **will** change after
release. Without versioning you'll corrupt or wipe a real teacher's data.
- **Fix**: version the schema with `PRAGMA user_version` in `onInit` /
  `migrateDbIfNeeded`, applying ordered migrations. Wrap multi-statement writes in
  `withTransactionAsync`. Keep migrations forward-only and tested against a copy of
  real data before shipping an update.

### 5. expo-sqlite: re-opening the DB / blocking the UI
- **Wrong**: opening the database in many components; running heavy synchronous
  queries on the JS thread.
- **Fix**: open once via `SQLiteProvider` + `useSQLiteContext`; use the async API
  (`getAllAsync`, `runAsync`); enable change listeners / `useLiveQuery` (or a data
  layer like Drizzle + TanStack Query) so the UI refreshes without manual reloads.

### 6. Async storage for the wrong job
- **Wrong**: stuffing relational/queryable data into AsyncStorage; expecting it to
  scale or to be transactional.
- **Fix**: AsyncStorage (or `expo-sqlite/kv-store`) for small key-value prefs;
  SQLite for anything you query, relate, or transact (students, lessons, payments).

### 7. Ignoring platform & device differences
- **Wrong**: assuming iOS behavior holds on Android; testing only on the Simulator
  / your own device.
- **Fix**: `Platform.select` where behavior differs; test on real iOS and Android,
  including a low-end Android. Mind safe-area insets and keyboard behavior.

### 8. Expo/EAS & native-module pitfalls
- **Wrong**: adding a library that needs native code and expecting it to work in
  Expo Go; config-plugin settings that require a rebuild changed at runtime;
  forgetting that the New Architecture (Fabric/TurboModules) may need updated deps.
- **Fix**: check Expo SDK compatibility before adding native deps; use a
  development build (EAS) when a module isn't in Expo Go; rebuild after config
  plugin changes. Pin SDK/library versions and verify they exist (don't trust a
  hallucinated package name).

## How to review RN/Expo here
First apply the React review (hooks, effects, keys, memoization). Then: hunt for
`Date` handling (is it a calendar date or an instant? tested off-zone and across
DST?); check lists are virtualized with cheap, memoized rows; confirm SQLite uses
parameterized queries, a versioned migration path, and a single provider. Record
the date/timezone convention and the schema-migration approach in cortex - those
are exactly the decisions a future edit (or another agent) must not silently break.

## Dependencies and Expo SDK alignment
- **`npx expo-doctor`** in CI: it exits 1 when any check fails. Checks include
  `AutolinkingDependencyDuplicatesCheck` (more than one version of a native
  module installed; a native build can only contain one),
  `InstalledDependencyVersionCheck`, `ReactNativeDirectoryCheck`, and
  `HermesV1VersionCheck`, which flags Hermes V1 on expo 55, 56, or 57 below
  57.0.9 (a known memory regression; fix with `npx expo install expo@^57.0.9
  --fix`).
- **`npx expo install --check`** reports packages that don't match the SDK;
  **`npx expo install --fix`** moves them to the expected versions. The source of
  truth is `bundledNativeModules.json` inside the installed `expo` package, not
  npm's `latest` tag.
- **Duplicate native modules**: `npm why <pkg>` (or `npm ls <pkg>`) to see who
  pulls each copy, `npm dedupe` to collapse compatible ranges, and an
  `overrides` entry in `package.json` pinning the SDK's version when a
  transitive dependency insists on another. Rerun `expo-doctor` afterwards.
- **React Native Directory** (checked by expo-doctor): treat packages marked
  unmaintained, or with New Architecture `untested`/`unsupported`, as a finding
  before adding them. Use `expo.doctor.reactNativeDirectoryCheck.exclude` in
  `package.json` only with a recorded reason.
- **Never `npm install <native-module>@latest` in an Expo app.** Use
  `npx expo install <pkg>` so the version matches the SDK; a mismatched native
  module builds fine in JS and fails at runtime or in the native build.
- For a full dependency audit (outdated, vulnerable, unused, duplicated,
  unmaintained) use the `ceo-deps` skill.
