# Snippet — paste into each repo's `CLAUDE.md`

The following block should live at (or near) the top of every repo's `CLAUDE.md`
so Claude Code sessions read the maintained context brief on load.

Copy verbatim:

```markdown
## Prior context (`.claude/CONTEXT.md`)

If `.claude/CONTEXT.md` exists in this repo, **read it before touching any
code**. It's a distilled brief of decisions, in-flight work, and gotchas
maintained by the `context-brief` skill (see the `nimbus-skills` repo).

- If it looks stale (>2 weeks), say so — the user can run
  `/context-brief update` to refresh.
- If it's missing and the repo has non-trivial history, offer to generate it.
- Never edit `.claude/CONTEXT.md` by hand from within a code change. If it's
  wrong, run the skill.
```

### Suggested `.gitignore` entries

The brief itself IS committed. But leave room for local caches around it:

```gitignore
# .claude/CONTEXT.md is committed on purpose — do NOT ignore it.
# But ignore local scratch and machine-state under .claude/
.claude/cache/
.claude/local/
```

### Onboarding checklist for a new repo

1. `mkdir -p .claude`
2. Run the `context-brief` skill: `/context-brief update`.
3. Paste the snippet above into the repo's `CLAUDE.md`.
4. Commit both.
