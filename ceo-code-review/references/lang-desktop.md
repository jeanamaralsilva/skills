# Desktop scripting (AutoHotkey v2 & Windows batch) — common mistakes

Automation scripts fail in their own ways: the interpreter takes something
literally that you meant as code, or a file-encoding detail silently breaks the
first line. Below, the traps that actually cost debugging time on Windows tooling.

## AutoHotkey v2

### 1. v1 syntax habits in v2 (= vs :=, unquoted strings)  *(the #1 migration trap)*
v2 is expression-based; v1's legacy command/assignment syntax is gone.
- **Wrong**: `x = value` (v1 literal assign), `MsgBox Hello` (unquoted text),
  `if x = 5` (legacy). In v2 `x = value` is a comparison, not an assignment.
- **Fix**: assign with `:=` and quote strings: `x := "value"`,
  `MsgBox("Hello")`, `if (x = 5)`. Strings are always quoted; functions use
  parentheses. (If a file mixes both, the launcher may even prompt for v1/v2 -
  a sign the syntax is ambiguous.)

### 2. #HotIf must be a real expression
v2 replaces v1's `#IfWin...` with `#HotIf`, which takes an **expression**.
- **Wrong**: `#IfWinActive ahk_class Notepad` (v1), or a complex multi-call
  expression in `#HotIf`.
- **Fix**: `#HotIf WinActive("ahk_class Notepad")`. For the fast path (evaluated by
  the hook, not the main thread) keep it to exactly one `WinActive`/`WinExist`
  call, each argument a single quoted string, optionally negated with `!`/`not` -
  nothing else. Heavier expressions run on the main thread and can lag or time out
  if the script is busy (e.g. mid-FileCopy). Always close a `#HotIf` block with a
  bare `#HotIf` to end its scope.

### 3. Brittle window identification
- **Wrong**: matching a window by title text alone - titles change with documents,
  locale, and state.
- **Fix**: identify by `ahk_exe` (the process) and/or `ahk_class` (the window
  class), found with Window Spy: `WinActivate("ahk_exe notepad.exe")`. Combine
  criteria when a process has several window classes.

### 4. Defining many hotkeys with the Hotkey() function
- **Wrong**: using `Hotkey(...)` for static hotkeys known at write time.
- **Fix**: prefer the `::` double-colon syntax - it's enabled as a batch at
  startup and performs better. Reserve `Hotkey()` for keys not known until runtime
  (e.g. read from an INI).

### 5. Sending keystrokes inside a #HotIf evaluation
Sending input from a function that `#HotIf` calls during evaluation can deadlock or
misfire. Keep `#HotIf` predicates pure (just window/state checks); do the sending
in the hotkey body.

## Windows batch (.bat / .cmd)

### 6. UTF-8 BOM breaks the first line  *(silent, infuriating)*
- **Wrong**: saving a `.bat` as "UTF-8" with a BOM. The 3 BOM bytes prefix the
  first command, so `@echo off` becomes garbage and cmd reports something like
  `'∩╗┐@echo' is not recognized`.
- **Fix**: save as **ANSI** or **UTF-8 without BOM**. If non-ASCII characters are
  needed, set the code page (`chcp 65001`) on a line that isn't the BOM-corrupted
  first one.

### 7. CRLF line endings
- **Wrong**: a `.bat` saved with Unix LF endings - labels and multi-line constructs
  misbehave because cmd expects CRLF.
- **Fix**: save batch files with Windows CRLF endings (configure the editor / Git
  `.gitattributes` so they aren't converted to LF).

### 8. Delayed expansion (the `%var%` vs `!var!` trap)
- **Wrong**: reading `%var%` after setting it **inside** a `for`/`if` block. `%var%`
  is expanded once when the whole block is parsed, so it shows the value from
  *before* the loop. Classic symptom: a counter that never changes.
- **Fix**: `setlocal enabledelayedexpansion` and read with `!var!` for values that
  change inside a block.

### 9. Unquoted paths and comparisons with spaces
- **Wrong**: `if %x%==y` or `cd %path%` when values contain spaces or are empty →
  syntax errors or wrong branch.
- **Fix**: quote both sides: `if "%x%"=="y"`, `cd /d "%path%"`. Quoting also guards
  against empty values blowing up the parser.

### 10. call :label with special characters / pipes in arguments
- **Wrong**: `call :do %arg%` where `%arg%` contains `|`, `&`, `>`, `(`, or spaces -
  cmd reparses the arguments and the label call breaks or the pipe is interpreted.
- **Fix**: quote the argument (`call :do "%arg%"`) and read it inside the label as
  `%~1`; escape literal special chars with `^` where needed; avoid building label
  arguments by piping. Use `goto :eof` to return and structure routines so user
  data never lands unquoted on a `call` line.

### 11. errorlevel handling
- **Wrong**: assuming `%errorlevel%` updates inside a parsed block, or comparing it
  the wrong way.
- **Fix**: check failures immediately (`if errorlevel 1 ...` means "≥ 1"), or use
  `if !errorlevel! ...` with delayed expansion inside blocks.

## How to review desktop scripts here
AHK v2: is it actually v2 syntax (`:=`, quoted strings, `MsgBox(...)`)? Are
`#HotIf` predicates simple expressions, and windows matched by `ahk_exe`/
`ahk_class` rather than title? Batch: check the file's **encoding (no BOM) and CRLF
endings first** - they cause the most baffling failures - then delayed expansion
for any variable changed inside a block, quoting around paths/comparisons, and safe
`call :label` arguments. Record reusable script conventions and the gotchas you've
already hit in cortex so they aren't rediscovered.
