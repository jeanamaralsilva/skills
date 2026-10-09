# cortex — the memory network

`cortex` is a terminal-native, zero-dependency memory store (`scripts/cortex.py`,
launchable via `scripts/cortex.sh`). It exists so engineering knowledge survives
the context window: a model can't hold a large codebase in memory, so instead of
re-deriving the same decisions and conventions every session, you **compile a
fact once and recall it forever**. Knowledge compounds instead of evaporating
when the chat ends.

This is the "LLM-maintained wiki" idea (Karpathy's LLM Wiki pattern; agentmemory;
Aider's repo map for the *code* side) reduced to a single dependency-free CLI:
SQLite for storage, a typed link graph for relationships, ranked keyword search
for recall. Deliberately no embeddings/vector DB - at personal/project scale
(hundreds to low thousands of notes) index-and-keyword navigation is enough, and
it keeps the tool installable anywhere a terminal runs, with no daemon and no
reindex-on-restart to go wrong.

## Two backends: your Cortex MCP and this CLI
You may already run a dedicated **Cortex memory MCP server**. When it's connected,
treat it as the **primary** store - it's purpose-built, and a long-lived server
keeps memory consistent across tools. Use this bundled `cortex` CLI as the
**fallback and complement**: for terminal/offline work, for environments where the
MCP isn't available, or for quick shell-native captures. The *discipline* below
(what to remember, typed links, confidence, never storing secrets, recall before
acting) is identical on both - only the call surface differs. Pick one as the
source of truth per project so notes don't fragment; if you use both, keep the MCP
authoritative and periodically export the CLI store into it.

## Storage & invocation
Resolution order for the database file:
`--db PATH` → `$CORTEX_DB` → `$CORTEX_HOME/cortex.db` → `~/.cortex/cortex.db`.

A global store at `~/.cortex/cortex.db` ("remember everything across projects") is
the default. For project-scoped memory, set `CORTEX_HOME` to the repo (e.g.
`export CORTEX_HOME="$PWD/.cortex"`) so each project keeps its own brain. The
`scope` field on each memory also separates `global` knowledge from per-project
knowledge inside one store.

Call it directly (`python3 scripts/cortex.py ...` or `./scripts/cortex.sh ...`).
Add `--json` to any command for machine-readable output in agent pipelines.

## Data model
- **memory**: `uid` (e.g. `m_1a2b3c4d`), `kind`, `text`, `tags`, `scope`,
  `source` (provenance), `confidence` (0-1), `created_at`/`updated_at` (RFC 3339).
- **link**: a typed, directed edge `src -[rel]-> dst` between two memories. Links
  form the "network": related facts connect, so recall surfaces the neighborhood,
  not just one note.

**kinds**: `decision`, `convention`, `pattern`, `antipattern`, `bug`, `fact`,
`glossary`, `todo`, `note`.
**relations**: `relates`, `supports`, `contradicts`, `duplicates`, `depends-on`,
`supersedes`, `refines`.

## Command reference
```
cortex remember "<text>" --kind <kind> [--tags a,b] [--scope <s>]
                         [--source <ref>] [--confidence 0.0-1.0] [--force]
cortex search  "<query>" [--kind k] [--scope s] [--tags a,b] [--limit N]
cortex recall  <id>                      # one memory + its links
cortex list    [--kind k] [--scope s] [--limit N]
cortex link    <src> <dst> --rel <relation>
cortex unlink  <src> <dst> --rel <relation>
cortex neighbors <id> [--depth N]        # walk the network from a node
cortex update  <id> [--text ...] [--confidence ...] [--source ...] [--add-tags ...]
cortex forget  <id> [--hard]             # soft-delete by default
cortex stats                             # counts by kind/scope + link total
cortex export                            # full dump as JSON (backup / migrate)
```

## When to remember
Capture **durable, reusable** knowledge - the things you'd be annoyed to
re-discover. Always attach `--source` (PR, file:line, ticket) and a `--confidence`.
- **decision**: a choice that constrains future work. *"Tokens in HttpOnly
  cookies, never localStorage (PR#412)."*
- **convention**: a rule the code follows. *"Domain logic never imports the web
  layer."* *"snake_case in Python, camelCase in TS."*
- **pattern / antipattern**: an approach to repeat, or a recurring mistake to
  avoid - especially the AI failure modes (e.g. *"agents keep re-adding a second
  logging package; reuse src/log.ts"* as an `antipattern`).
- **bug**: a non-obvious defect + its root cause/fix, so it isn't reintroduced.
- **glossary**: a term in the project's own language (great for matching test and
  interface vocabulary).
- **fact**: a stable truth about the system that's expensive to re-learn.

Then **link** related notes so the graph is navigable: an antipattern `supports`
a convention; a new decision `supersedes` an old one; a bug `relates` to the
module fact. Use `contradicts` when two notes conflict - it's a flag to resolve,
not a bug.

## When NOT to remember
- **Secrets** - API keys, passwords, tokens, private keys. cortex is read back
  verbatim by agents; the secret guard blocks obvious ones, but don't lean on it.
- **Transient state** - "the build is red right now", today's branch name.
- **Raw chat or large blobs** - store the distilled conclusion, not the transcript.
- **Low-value trivia** - a junk drawer kills recall quality. If in doubt, set a
  low `--confidence` rather than overstuffing.

## Recall discipline
- **Before** writing or reviewing in an area, search first:
  `cortex search "auth token storage"` / `cortex search "<module> convention"`.
  Treat hits as binding context - follow recorded decisions and conventions.
- Prefer specific, multi-word queries; filter with `--tags`/`--kind`/`--scope`.
- From a relevant hit, run `cortex neighbors <id>` to pull in connected decisions.

## Keeping it healthy (lint)
The store degrades if it becomes a junk drawer. Periodically:
- `cortex stats` for a sense of size and shape.
- Resolve `contradicts` links - decide which note wins, `supersede` the loser, or
  lower its confidence.
- Demote/forget stale notes (`forget` is a soft-delete; `--hard` is permanent).
- New, single-source claims should carry lower confidence until corroborated.

## Multi-agent use
Multiple agents can share one store. Use `scope` to separate **shared** team
knowledge from an agent's **private** working notes, and `source` so every fact
is traceable to who/what produced it. Recall is read-only and safe to run
concurrently; writes commit atomically per command. A reviewer agent should
recall before judging and capture any new convention/decision it establishes so
the next agent inherits it.

## Further reading (prior art)
- Karpathy's **LLM Wiki** pattern - compile knowledge once, maintain with the LLM.
- **agentmemory** / LLM Wiki v2 - confidence scoring, supersession, typed graph.
- **Aider repo map** - tree-sitter + PageRank ranking for *code* context
  (the inspiration behind `context_map`).
