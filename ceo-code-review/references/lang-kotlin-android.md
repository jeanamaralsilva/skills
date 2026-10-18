# Kotlin & Android (Jetpack Compose) — common mistakes

Android is where AI output ages fastest. The platform, Jetpack libraries, the
Android Gradle Plugin (AGP) and Play policy all change every year, and models
blend eras: `AsyncTask` next to coroutines, `LiveData` next to `StateFlow`,
Room 2 APIs in a Room 3 project, a `kotlin-android` plugin AGP 9 no longer needs.
Compose adds its own trap: code that renders correctly can still recompose on
every frame or lose state on rotation. So "plausible is not correct" here means:
**read the version catalog and AGP version first, test a release (R8) build on
a device, and check lifecycle behavior, not just the first render.**

## The mental model (get this right and most bugs disappear)
- **Structured concurrency.** Every coroutine runs in a scope that owns it:
  `viewModelScope` (cancelled when the ViewModel is cleared), `lifecycleScope`,
  or a scope injected for app-wide work. If nobody owns it, nobody cancels it.
- **Main-safe suspend functions.** A suspend function should be safe to call
  from the main thread; the function that does blocking I/O switches with
  `withContext(Dispatchers.IO)` itself, not every caller.
- **Unidirectional data flow.** The ViewModel exposes immutable state
  (`StateFlow<UiState>`), the UI renders it and sends events up. The UI never
  mutates the ViewModel's state holder directly.
- **Compose is a function of state.** Composables can run many times, in any
  order, and be skipped. Side effects belong in effect APIs
  (`LaunchedEffect`, `DisposableEffect`) or the ViewModel, never in the body.

## AI-specific Kotlin/Android mistakes (check these first)

### 1. Coroutines without an owner, on the wrong dispatcher
- **What**: `GlobalScope.launch` (a delicate API: nothing cancels it),
  `CoroutineScope(Dispatchers.IO).launch` created ad hoc in a repository,
  `runBlocking` on the main thread, network or DB calls on `Dispatchers.Main`,
  `Dispatchers.IO` hardcoded everywhere (untestable).
- **Detect/fix**: launch UI work in `viewModelScope`; for work that must outlive
  a screen, inject an application `CoroutineScope` or use WorkManager. Inject
  dispatchers so tests can substitute a `TestDispatcher`.

### 2. Swallowing cancellation
- **What**: `try { ... } catch (e: Exception) { ... }` or `runCatching { }`
  around suspend calls. Both catch `CancellationException`, so a cancelled
  coroutine keeps running and reports a fake error.
- **Detect/fix**: rethrow `CancellationException` (catch it first and rethrow),
  or catch only the specific exceptions you expect. Avoid `runCatching` around
  suspend calls unless the cancellation case is handled.

### 3. Flow collection that ignores the lifecycle
- **What**: `lifecycleScope.launch { flow.collect { ... } }` in a Fragment, or
  `collectAsState()` in Compose. Android's docs warn never to collect a flow that
  updates UI directly from `launch`/`launchIn`, since it keeps processing while
  the view is not visible, which can crash. Unlike `LiveData.observe`, flow
  collection does not stop on `STOPPED`.
- **Detect/fix**: in Compose use `collectAsStateWithLifecycle()` (collects from
  `STARTED`, stops at `STOPPED`). In Views use `repeatOnLifecycle(Lifecycle.State.
  STARTED) { ... }`. Expose state with `stateIn(viewModelScope,
  SharingStarted.WhileSubscribed(5_000), initial)` so upstream work stops when no
  one is looking but survives a rotation.

### 4. `LiveData` and `StateFlow` mixed, or one-off events as state
- **What**: new code using `MutableLiveData` in a Flow-based codebase (or the
  reverse), exposing `MutableStateFlow` publicly, modeling navigation or toasts as
  a `StateFlow<Event?>` that replays on rotation.
- **Detect/fix**: follow the codebase's choice (new Android guidance favors
  `StateFlow`; note `StateFlow` requires an initial value). Expose
  `asStateFlow()`. Model one-off outcomes as part of UI state that the UI
  acknowledges, or follow the project's recorded event pattern.

### 5. Version-era mixing (Room 3, AGP 9, deprecated APIs)
- **What**: Room 3.0 (stable July 2026) moved to the `androidx.room3` package,
  is KSP-only, requires a `SQLiteDriver`, drops `SupportSQLite`/`Cursor` types,
  makes DAO functions `suspend` (unless they return `Flow` or similar), and
  replaces `runInTransaction` with `withWriteTransaction`. AGP 9 builds Kotlin in
  (remove the `org.jetbrains.kotlin.android` plugin) and requires the
  `com.android.kotlin.multiplatform.library` plugin for KMP modules. Models still
  write Room 2 migrations with `SupportSQLiteDatabase`, KAPT setups, and
  `AsyncTask`/`onActivityResult`.
- **Detect/fix**: read `gradle/libs.versions.toml` and the AGP version before
  judging code; check the matching AndroidX release notes for any API you don't
  recognize. Don't let a diff mix Room 2 and Room 3 imports unless it is a
  planned migration.

### 6. Hallucinated dependencies and coordinates
- **What**: invented artifact names, wrong group IDs, versions that don't exist,
  versions hardcoded in a module while the project uses a version catalog.
- **Detect/fix**: confirm coordinates on Google Maven / Maven Central; add them
  to `libs.versions.toml` and reference `libs.xxx`; use the Compose BOM for
  Compose artifacts instead of per-artifact versions.

## Compose traps

### 7. State lost or recreated
- **Wrong**: `var x by mutableStateOf(...)` without `remember` (reset every
  recomposition); `remember` where the value must survive rotation or process
  death; expensive objects built in the composable body each recomposition.
- **Fix**: `remember { }` for recomposition, `rememberSaveable` for
  configuration change and process death (small, saveable values only), the
  ViewModel for screen state. Key `remember(key)` on inputs that should reset it.

### 8. Needless recomposition and unstable parameters
- **Wrong**: passing `List`/`Map` from a mutable source, reading a fast-changing
  state high in the tree, computing derived values on every frame, `LazyColumn`
  items without stable keys.
- **Fix**: since Kotlin 2.0.20 strong skipping is on by default, so composables
  with unstable parameters can skip, but unstable ones compare by instance
  (`===`); a new list instance with the same content still recomposes. Prefer
  immutable models, `derivedStateOf` for values derived from fast state, lambdas
  or `Modifier` reads to defer state reads, and `items(list, key = { it.id })`.
  Measure with Layout Inspector recomposition counts or compiler stability
  reports before "optimizing".

### 9. Side effects in composition
- **Wrong**: launching a coroutine, logging analytics, or calling the ViewModel
  directly in the composable body; `LaunchedEffect(Unit)` that should restart when
  an input changes.
- **Fix**: `LaunchedEffect(key)` with the right keys, `DisposableEffect` for
  register/unregister, `rememberCoroutineScope` for event handlers. Android's docs
  note `LaunchedEffect` is tied to composition, not the Activity lifecycle (it
  runs for off-screen pager pages); use `LifecycleEventEffect` for "user actually
  sees this" effects.

## Data, release and Play traps

### 10. Room migrations missing or destructive
- **Wrong**: bumping `version` without a migration (Room throws
  `IllegalStateException` on devices with the old schema), adding
  `fallbackToDestructiveMigration()` to make the crash go away (deletes user
  data), `exportSchema = false` (automated migrations then cannot work).
- **Fix**: export schemas and commit them; use `@AutoMigration` (with an
  `AutoMigrationSpec` for renames/deletes) or a manual `Migration`; test with
  `MigrationTestHelper`, including a full path from the oldest shipped version.
  Write migration SQL inline, not via constants that may change later.

### 11. R8 breaks what reflection needs
- **Wrong**: debug works, release crashes: a JSON model, a Retrofit interface or
  a class loaded by name was renamed or removed. R8 full mode has been the
  default since AGP 8.0 and makes stricter assumptions about reflection. Broad
  `-keep class com.example.** { *; }` rules added as a fix disable optimization.
- **Fix**: prefer libraries with codegen and bundled consumer rules (kotlinx.
  serialization, Moshi codegen); write narrow keep rules; use
  `proguard-android-optimize.txt` (AGP 9 dropped `proguard-android.txt`). Always
  test the minified release build on a device before shipping.

### 12. Main-thread and leak hazards
- **Wrong**: disk/DB/network on the main thread, holding an `Activity` or `View`
  in a ViewModel or singleton, registering listeners without unregistering.
- **Fix**: StrictMode in debug builds; pass `applicationContext` where a context
  must be retained; LeakCanary in debug.

### 13. Play policy deadlines
- **Wrong**: leaving `targetSdk` behind. From August 31, 2026, new apps and
  updates must target Android 16 (API 36) for phones and tablets (API 35 for
  Wear OS and Automotive, API 34 for TV and XR); an extension to November 1, 2026
  could be requested. Existing apps below API 35 become invisible to new users on
  newer devices.
- **Fix**: raise `targetSdk` deliberately and test the behavior changes of each
  level. Apps with native code (NDK or native SDKs) targeting API 35+ must also
  support 16 KB memory pages; per Android's page, updates without it are blocked
  from February 1, 2027. AGP 8.5.1+ with NDK r28+ makes this the default.

## Toolchain (let the tools catch the mechanical errors)
- **Version catalog** (`gradle/libs.versions.toml`) as the single source of
  versions; the Compose BOM for Compose.
- **Dependency Analysis Gradle Plugin** (`com.autonomousapps.build-health` in
  settings): `./gradlew buildHealth` reports unused dependencies, used transitive
  dependencies, and wrong configurations (`api` vs `implementation`);
  `./gradlew fixDependencies` applies the fixes.
- **Android Lint** (`./gradlew lint`) with warnings reviewed, plus detekt or
  ktlint as the repo uses. Compose lint checks catch many state and modifier
  mistakes.
- Compose compiler metrics/stability reports when performance is in question.
- Unit tests with `kotlinx-coroutines-test` (`runTest`, injected dispatchers);
  Room `MigrationTestHelper`; a release-build smoke test.

## How to review Kotlin/Android here
Open the version catalog and AGP version first; most AI mistakes on Android are
era mistakes (Room 2 vs 3, KAPT vs KSP, `kotlin-android` plugin on AGP 9,
`LiveData` in a Flow codebase). Then check every coroutine has an owner and a
dispatcher choice, cancellation is not swallowed, and UI flows are collected with
the lifecycle. In Compose, look for state without `remember`, side effects in
the body, missing `LazyColumn` keys, and new collection instances per frame. For
data, demand a migration and a migration test for every schema version bump. For
release, ask whether the R8 build was tested and whether `targetSdk` meets the
current Play deadline. Record the project's conventions in cortex: state holder
type, event pattern, DI scope for app-wide work, Room major, and keep-rule
policy, so later edits stay in the same era as the codebase.
