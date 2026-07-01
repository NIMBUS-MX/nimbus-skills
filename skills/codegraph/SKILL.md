---
name: codegraph
description: >
  Org policy — use CodeGraph (100% local MCP that pre-indexes each repo into a
  semantic graph) for cross-file understanding, "who calls X", "what depends on
  Y", and impact analysis. Cheaper than grep+read loops for anything spanning >2
  files.

  Trigger this skill when:
  - Session starts in any repo (verify CodeGraph is installed + indexed; propose
    init if not).
  - User asks "where is X used", "who calls Y", "what would break if I change
    Z", "map this module".
  - Before any refactor touching 3+ files.
  - User invokes `/codegraph`.
---

## Org policy

Every Nimbus repo should have CodeGraph indexed. It's local, zero-cloud, saves
Claude token budget by pre-computing the semantic graph so cross-file questions
resolve in one MCP call instead of many grep+read pairs.

Repo: https://github.com/colbymchenry/codegraph.

## On session start

Silently check:

1. `command -v codegraph` — is the CLI installed?
2. `test -d .codegraph` at repo root — is this repo indexed?

If **CLI missing** → tell the user once:

```
CodeGraph CLI not installed. Install:
  curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh
Then: `codegraph install` (wires MCP into Claude Code).
```

If **CLI installed but repo not indexed** → tell the user once:

```
CodeGraph not indexed in this repo. Run:
  codegraph init
Takes ~30s-2min depending on repo size. Indexes into `.codegraph/`.
```

Do not spam. State it once at session start and move on. Never block work on
this — CodeGraph is a booster, not a gate.

## When to prefer CodeGraph over grep/read

- **"Where is `foo` defined / used?"** → CodeGraph MCP query, not `grep -rn`.
- **"What calls this function?"** → CodeGraph reverse-callers.
- **"What are all subclasses of X?"** → CodeGraph type hierarchy.
- **"What imports this module?"** → CodeGraph import graph.
- **Refactor spanning 3+ files** → query CodeGraph for the blast radius before
  editing.
- **Onboarding to unfamiliar area** → ask CodeGraph "give me the entry points
  for the auth flow" instead of skimming folders.

## When grep/read still wins

- Single file / single symbol lookups.
- Pattern matches (regex, string literals in comments, TODO tags).
- Anything CodeGraph doesn't know about (config files, YAML, HTML template
  strings).

## Freshness

CodeGraph auto-syncs on file changes if the CLI daemon is running. If results
look stale after a big pull or rebase, suggest: `codegraph reindex`.

## Fallback

If the CodeGraph MCP is not connected in this session (`mcp__codegraph__*` tools
absent), degrade gracefully to grep+read without complaint. Just don't reach
for a 20-file audit that CodeGraph would have solved in one call.
