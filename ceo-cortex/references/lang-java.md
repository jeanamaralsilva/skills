# Java & Spring Boot — common mistakes

The Java errors worth catching cluster in two places: object/null semantics in
plain Java, and the "magic" of Spring proxies and JPA that fails silently when
misused. Below, with the Spring Data JPA traps that hit CRUD apps hardest.

## Plain Java

### 1. NullPointerException / Optional misuse
- **Wrong**: returning `null` from methods; calling `.get()` on an `Optional`
  without checking; using `Optional` for fields/parameters.
- **Fix**: return `Optional` from lookups and handle the empty case
  (`orElseThrow`, `map`, `ifPresent`); never `Optional.get()` blindly; keep
  `Optional` as a return type, not a field type.

### 2. equals()/hashCode() — especially on JPA entities
- **Wrong**: overriding one but not the other; including a generated `@Id` (which
  is null before persist) so the object "changes identity" inside a `HashSet`;
  using all mutable fields.
- **Fix**: implement both together; for entities, base equality on a stable
  business key (or be deliberate about identity). Don't put unsaved entities in
  hash-based collections expecting stable behavior.

### 3. == vs .equals for objects
- **Wrong**: `==` on `String`/boxed `Integer` compares references; works by luck
  with interned/cached values, then fails.
- **Fix**: `.equals()` for value comparison; `Objects.equals(a, b)` for null
  safety.

### 4. Resource leaks
- **Wrong**: streams, connections, files closed manually (or not at all on the
  error path).
- **Fix**: try-with-resources for anything `AutoCloseable`.

### 5. Swallowed exceptions
- **Wrong**: `catch (Exception e) {}` or catch-and-`printStackTrace` then continue.
- **Fix**: handle meaningfully or rethrow; never silence. Catch specific types.

### 6. Mutable shared state / non-thread-safe singletons
- **Wrong**: mutable fields on a singleton-scoped Spring bean, shared
  `SimpleDateFormat`, mutating static collections from multiple threads.
- **Fix**: keep beans stateless; use thread-safe types (`java.time`,
  `ConcurrentHashMap`); confine mutable state.

## Spring Boot / Spring Data JPA

### 7. @Transactional self-invocation  *(silent - transaction never starts)*
Spring's `@Transactional` works through an AOP proxy. Calling an annotated method
**from another method in the same bean** bypasses the proxy, so no transaction
starts. Also, only **public** methods are proxied - `private`/`protected`/`final`
annotations are ignored silently.
- **Fix**: move the transactional method to another bean and inject it; or
  self-inject with `@Lazy`; or use AspectJ. Keep the method public.

### 8. JPA N+1 queries  *(the most common JPA performance bug)*
- **Wrong**: iterating a list of entities and touching a lazy association in the
  loop → one query per element. Switching blindly to `EAGER` just moves the cost.
- **Fix**: `JOIN FETCH` in the query, an `@EntityGraph`, or `@BatchSize`. Verify
  by logging SQL (`spring.jpa.show-sql` / `hibernate.format_sql`) and counting
  queries.

### 9. LazyInitializationException
- **Wrong**: accessing a lazy association after the transaction/session closed
  (e.g. in the controller or view).
- **Fix**: fetch what you need inside the transactional boundary (fetch join /
  entity graph), or map to a DTO before returning. Don't enable
  open-session-in-view to paper over it.

### 10. Returning JPA entities from controllers
- **Wrong**: serializing entities directly - leaks the schema, drags in lazy
  proxies, risks infinite recursion on bidirectional relations.
- **Fix**: map to DTOs/records at the API boundary. (This is also the local
  convention to record in cortex for a CRUD codebase.)

### 11. Field injection
- **Wrong**: `@Autowired` on fields - hides dependencies, hard to unit-test,
  permits circular references to sneak in.
- **Fix**: constructor injection with `final` fields. Required dependencies become
  explicit and the class is testable without Spring.

### 12. Thin or missing error handling at the web layer
- **Wrong**: cryptic 500s; each controller handling errors differently.
- **Fix**: centralize with `@ControllerAdvice` / `@ExceptionHandler`; return
  consistent, non-leaky error responses.

## How to review Java/Spring here
Plain Java: null handling, equals/hashCode, resource closing, swallowed
exceptions. Spring: is the transaction boundary actually a boundary (proxy, public
method, no self-call)? Any lazy association touched outside its session? Are
entities escaping to the API instead of DTOs? Log and count SQL to catch N+1
before it ships. Record the project's DTO/transaction conventions in cortex.
