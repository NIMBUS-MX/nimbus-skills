# nimbus-skills

Shared Claude Code skills for the Nimbus / CIDCA engineering team. Universal
dev workflow accelerators — code intelligence, safety, ceremony, cleanup —
usable across every Nimbus repo.

## Install

```bash
git clone https://github.com/NIMBUS-MX/nimbus-skills.git ~/Development/nimbus-skills
cd ~/Development/nimbus-skills
./install_skills.sh
```

Restart Claude Code. Skills auto-load on session start.

**Uninstall** any time: `./install_skills.sh --uninstall`.

## Skills

| Skill | Trigger | One-line |
|---|---|---|
| [`codegraph`](skills/codegraph/SKILL.md) | `/codegraph`, session start | **Org policy** — index each repo with [CodeGraph](https://github.com/colbymchenry/codegraph), prefer semantic queries over grep for cross-file work. |
| [`context-brief`](skills/context-brief/SKILL.md) | `/context-brief`, "handoff", "backup context" | Maintain a committable `.claude/CONTEXT.md` project brief so a fresh Claude session picks up prior decisions without re-reading every doc. |
| [`preflight`](skills/preflight/SKILL.md) | "commit", "ready to push", `/preflight` | Run the right lint/format/type/test gates for the repo's stack (poetry / yarn / pnpm / uv / go) before letting a commit through. |
| [`conventional-commit`](skills/conventional-commit/SKILL.md) | "write a commit", `/commit` | Enforce Conventional Commits + Nimbus footer. Suggest scope from staged files. |
| [`secrets-check`](skills/secrets-check/SKILL.md) | Pre-commit hook, `/secrets-check` | Grep staged diff for AWS keys, Stripe live keys, JWTs, PEMs, GH tokens. Block commit on hit. |
| [`never-auto-push`](skills/never-auto-push/SKILL.md) | Before any `git push` | Enforce the load-bearing rule: no push without explicit user authorization in the current turn. |
| [`sentry-triage`](skills/sentry-triage/SKILL.md) | Sentry URL pasted, `/sentry-triage` | Fetch via Sentry MCP, extract stack, grep repo, propose fix + PR title. |
| [`pr-review`](skills/pr-review/SKILL.md) | "review this PR", `/pr-review` | One line per finding, severity-tagged, no praise, no scope creep. Nimbus caveman format. |
| [`ticket-brief`](skills/ticket-brief/SKILL.md) | ClickUp/Linear/GitHub URL pasted | Fetch + distill into a work brief (goal, acceptance criteria, blast radius, branch name, commit prefix). |
| [`sprint-planning`](skills/sprint-planning/SKILL.md) | `/sprint-planning`, "plan the sprint" | Autonomously fill the current sprint from the backlog to team capacity, balance by dev skill + time constraints, write a sprint-goal ClickUp doc, and generate follow-up tickets. |
| [`worktree-cleanup`](skills/worktree-cleanup/SKILL.md) | "remove branch", `git branch -D` errors on worktree | Enforce `worktree remove --force` THEN `branch -D` ordering. |
| [`db-migration-safety`](skills/db-migration-safety/SKILL.md) | Edit any migration file, `/db-migration-safety` | Audit Alembic / Django / Drizzle migrations for prod-safe patterns. Nimbus cross-repo hot-spot rules baked in. |
| [`release-brief`](skills/release-brief/SKILL.md) | "cut a release", `/release-brief` | Detect release convention, draft changelog from recent commits, propose bump kind, show exact command. |
| [`stale-branch-audit`](skills/stale-branch-audit/SKILL.md) | "cleanup branches", `/stale-branch-audit` | List branches >30 days old grouped by cleanup safety. |
| [`claude-worktree-reap`](skills/claude-worktree-reap/SKILL.md) | "reap claude worktrees", `/claude-worktree-reap` | Scan Claude-created worktrees → approve a PLAN file (size + danger notes) → delete → RESULTS file (space saved) → clean up both files. Two confirmation gates. |
| [`honest-pushback`](skills/honest-pushback/SKILL.md) | Session start (silent) | Act as senior staff engineer. Push back **once** with a concrete alternative before executing an approach you have evidence is wrong. |
| [`eureka`](skills/eureka/SKILL.md) | Word "eureka" after finishing work | Post-implementation retrospective — surface concrete refactor opportunities on the just-completed diff. |
| [`verify-over-assume`](skills/verify-over-assume/SKILL.md) | About to state a verifiable fact; hedging ("probably"/"should be") | Don't guess what a tool/MCP/API/file can confirm. On the Max plan, quality beats token saving — spend the call to be certain. |

Snippet for repo-level integration (paste into each repo's `CLAUDE.md`): see
[`CLAUDE_MD_SNIPPET.md`](CLAUDE_MD_SNIPPET.md).

## Layout

```
nimbus-skills/
├── README.md
├── install_skills.sh          # idempotent, --uninstall + --dry-run
├── CLAUDE_MD_SNIPPET.md
└── skills/
    └── <skill-name>/
        ├── SKILL.md           # frontmatter + prose body
        ├── templates/         # optional
        └── scripts/           # optional
```

## Adding a new skill

1. `mkdir skills/<skill-name>`
2. Create `skills/<skill-name>/SKILL.md`:
   ```markdown
   ---
   name: <skill-name>
   description: >
     What the skill does + trigger phrases + slash commands.
   ---

   ## Prose body
   ...
   ```
3. Add a row in the skills table above.
4. Commit + PR.

## Skill discoverability

Once installed, Claude Code auto-loads skills at session start. In-session, they
appear via:

- `/help` — lists user-invocable slash commands (only skills whose SKILL.md
  declares a command name will show here).
- The `Skill` tool — Claude uses this to invoke a skill by name when a trigger
  phrase matches.

## Contact

Owner: Nimbus / CIDCA engineering.
