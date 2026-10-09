# Swift & iOS (SwiftUI) — common mistakes

Swift changed more between 2023 and 2026 than in the five years before: the
Observation framework replaced `ObservableObject` for new code, Swift 6 made
data-race safety a compile error, Swift 6.2 changed where `async` functions run
and let whole targets default to the main actor, and Xcode 26 turned that default
on for new projects. Training data is dominated by the old world, so AI code
mixes `@StateObject` with `@Observable`, sprinkles `@MainActor` and
`@unchecked Sendable` until the compiler goes quiet, and still reaches for
`NavigationView`. "Plausible is not correct" here means: **check the Swift
language mode, the deployment target and the default isolation setting before
judging any line, and treat every concurrency warning as a real bug report.**

## The mental model (get this right and most bugs disappear)
- **Isolation, not threads.** Swift concurrency reasons about which actor owns
  data. UI state lives on the `@MainActor`; values crossing between actors must
  be `Sendable`. The compiler checks this in Swift 6 mode, and its errors point at
  real races.
- **Where code runs depends on settings.** With Swift 6.2's
  `NonisolatedNonsendingByDefault`, a nonisolated `async` function runs on the
  caller's actor; `@concurrent` explicitly sends it to the thread pool. With
  default isolation set to `MainActor` (Xcode 26's default for new app
  projects), unannotated code is main-actor isolated. Read the target's build
  settings or `Package.swift` before reasoning about threads.
- **SwiftUI views are values; state lives elsewhere.** A `View` struct is
  recreated constantly. Ownership is declared with property wrappers
  (`@State`, `@Environment`, `@Binding`, `@Bindable`), and the wrong one either
  resets state or leaks updates.
- **Value types first, optionals honestly.** Prefer structs and enums; reference
  types when identity or shared mutation is the point. Optionals model absence;
  unwrapping them is a decision, not a formality.

## AI-specific Swift mistakes (check these first)

### 1. Mixing Observation and Combine-era property wrappers
- **What**: an `@Observable` class held with `@StateObject` or `@ObservedObject`,
  `@Published` inside an `@Observable` class, `.environmentObject()` with
  `@Environment(Model.self)`, or a new `ObservableObject` in an iOS 17+ codebase.
- **Detect/fix**: with `@Observable` (iOS 17+): own it with `@State`, pass it as
  a plain property, use `@Bindable` when you need `$model.field` bindings, inject
  with `.environment(model)` and read with `@Environment(Model.self)`; all stored
  properties are tracked (opt out with `@ObservationIgnored`). Keep
  `ObservableObject`/`@StateObject`/`@Published` only where the deployment target
  is below iOS 17 or the codebase hasn't migrated, and don't mix the two for one
  type.

### 2. Silencing strict concurrency instead of fixing it
- **What**: `@unchecked Sendable` on a class with mutable state,
  `nonisolated(unsafe)` on shared vars, `@preconcurrency import` everywhere,
  `@MainActor` slapped on a networking type, `DispatchQueue.main.async` inside
  `async` code, `Task.detached` to "get off the main thread".
- **Detect/fix**: each of these needs a comment naming the invariant that makes
  it safe (a lock, an immutable after-init, a framework guarantee); otherwise fix
  the design: make the type a value, an `actor`, or main-actor isolated on
  purpose. Use `@concurrent` (6.2) for work that must leave the caller's actor.
  `Task.detached` drops priority and task-locals; it is rarely the right tool.

### 3. Outdated SwiftUI navigation and APIs
- **What**: `NavigationView` (deprecated since iOS 16) and
  `NavigationLink(isActive:)`, `.onChange(of:perform:)` with the one-parameter
  closure (deprecated in iOS 17), `UIApplication.shared.windows`,
  `.foregroundColor` where the project uses `.foregroundStyle`.
- **Detect/fix**: `NavigationStack` with value-based `NavigationLink(value:)`
  and `.navigationDestination(for:)`, or `NavigationSplitView`; a `path` array (or
  `NavigationPath`) in state for programmatic navigation. Treat every deprecation
  warning as a finding; check the API's availability against the deployment
  target.

### 4. Retain cycles in closures and tasks
- **What**: an object stores a closure that captures `self` strongly
  (`onComplete = { self.reload() }`), Combine `sink { self... }` stored in
  `cancellables`, a `Timer` or `NotificationCenter` block observer holding the
  owner, a long-running `Task { }` in a class that loops forever with `self`.
- **Detect/fix**: `[weak self]` with `guard let self else { return }` for
  stored or long-lived closures; cancel stored `Task`s in `deinit` or tie them to
  view lifetime with `.task { }` (cancelled automatically when the view
  disappears). Non-escaping closures and SwiftUI view structs don't need
  `[weak self]`. Verify with the Memory Graph debugger or Instruments' Leaks.

### 5. Force unwraps and `try!`
- **What**: `URL(string: s)!` on dynamic strings, `as!` casts on decoded data,
  `try!` around decoding or file I/O, implicitly unwrapped optionals for
  properties that really can be nil.
- **Detect/fix**: `guard let`/`if let`, `try` with real error handling, typed
  decoding errors surfaced to the user. Force unwraps are acceptable only for
  programmer invariants (a literal URL, a bundled resource) and should read as
  such. SwiftLint's `force_cast` and `force_try` rules (on by default) and the
  opt-in `force_unwrapping` rule find them.

### 6. Hallucinated APIs and packages
- **What**: modifiers or initializers that don't exist, or that exist only on a
  newer OS than the deployment target; Swift packages with guessed URLs.
- **Detect/fix**: the compiler catches non-existent symbols, but not runtime
  availability on older devices; check `@available` and the deployment target.
  Confirm a package's repository, owner and tagged releases before adding it.

## Platform and release traps

### 7. Main-thread work and view body cost
- **Wrong**: decoding, image processing or sorting large arrays inside `body` or
  on the main actor; creating formatters per render.
- **Fix**: move heavy work into a `@concurrent` function or an actor and assign
  the result on the main actor; cache formatters; keep `body` cheap and
  side-effect free; use `.task(id:)` for async loads tied to an input.

### 8. Codable and networking without failure paths
- **Wrong**: `try? JSONDecoder().decode(...)` that turns every schema mismatch
  into a silent nil, no status code check on `URLSession` responses, default
  request timeout assumed acceptable.
- **Fix**: decode with `try` and log the `DecodingError`; check
  `(response as? HTTPURLResponse)?.statusCode`; set `timeoutInterval` on requests
  or the session configuration deliberately.

### 9. Secrets and storage
- **Wrong**: tokens in `UserDefaults` or a plist, API keys in the binary treated
  as secret, logging personal data.
- **Fix**: Keychain for credentials; server-side secrets for anything that must
  stay secret; `Logger` with privacy levels.

### 10. App Store requirements
- **Wrong**: assuming an older Xcode can still ship. Since April 28, 2026, App
  Store uploads must be built with Xcode 26 or later using the iOS 26 (and
  sibling) SDKs; Apple's page lists iOS 13 as the minimum target accepted from
  September 9, 2026. Xcode 27 (Swift 6.4, iOS 27 SDK) shipped in September 2026.
- **Fix**: pin the Xcode version in CI and bump it with the platform cycle.

### 11. Privacy manifests
- **Wrong**: using a required-reason API (UserDefaults, file timestamps, system
  boot time, disk space, active keyboards) without declaring it, or shipping a
  third-party SDK on Apple's "SDKs that require a privacy manifest and signature"
  list without its manifest. Uploads have required approved reasons since May 1,
  2024.
- **Fix**: a `PrivacyInfo.xcprivacy` in the app and in each SDK bundle,
  declaring `NSPrivacyAccessedAPITypes` with reasons, collected data types and
  tracking domains. Generate the Xcode privacy report before release and compare
  it with the App Store privacy answers.

### 12. Dependency managers: SwiftPM first, CocoaPods ending
- **Wrong**: adding new CocoaPods dependencies. The CocoaPods trunk becomes
  read-only on December 2, 2026 (test run November 1 to 7): existing builds keep
  working, but no new pods or versions will be published there.
- **Fix**: prefer Swift Package Manager; plan migration of remaining pods (or
  vendor them). Commit `Package.resolved` for apps, pin versions with
  `.upToNextMinor`/exact where stability matters, and review every new package's
  source and owner.

## Toolchain (let the tools catch the mechanical errors)
- Swift 6 language mode (or Swift 5 mode with complete strict concurrency
  checking as a step) with warnings treated as errors in CI.
- In `Package.swift` (tools 6.2): `.defaultIsolation(MainActor.self)` and
  `.enableUpcomingFeature("NonisolatedNonsendingByDefault")` /
  `"InferIsolatedConformances"` when the project adopts approachable
  concurrency; make sure app targets and packages agree.
- **SwiftLint** (and `swift-format` or SwiftFormat as the repo uses), with
  force-unwrap/cast/try rules on.
- Xcode's Thread Sanitizer and Main Thread Checker in test schemes; Instruments
  (Leaks, Time Profiler, SwiftUI) for leaks and slow bodies.
- Swift Testing (`@Test`, `#expect`) or XCTest for logic; UI tests for
  navigation flows.

## How to review Swift/iOS here
Before reading code, check the deployment target, Swift language mode, default
actor isolation and approachable-concurrency settings: they decide whether
`@Observable` is allowed and where every `async` function runs. Then scan for the
Combine-era wrappers mixed with Observation, `@unchecked Sendable`,
`nonisolated(unsafe)`, `Task.detached`, `DispatchQueue.main` in async code,
`NavigationView`, force unwraps, and closures stored with a strong `self`.
Check heavy work stays out of `body`, network errors are surfaced, credentials
live in the Keychain, the privacy manifest covers new APIs and SDKs, and new
dependencies come through SwiftPM. Record the project's conventions in cortex:
minimum iOS, state ownership pattern, isolation defaults, navigation approach,
and package policy, so the next edit doesn't reintroduce `ObservableObject` or
paper over a data race.
