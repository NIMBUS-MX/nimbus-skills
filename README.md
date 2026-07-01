# nimbus-skills

Shared Claude Code skills for the Nimbus / CIDCA engineering team.

## What's here

| Skill | Trigger | Purpose |
|---|---|---|
| `context-brief` | `/context-brief`, "generate context brief", "handoff", "backup context" | Sweep a folder tree, distill CLAUDE.md files + in-flight docs + git state into a versioned `.claude/CONTEXT.md`. Keeps a single Claude-readable, git-committable brief per repo (or across a workspace) so a fresh Claude session picks up prior context without re-reading everything. |

Add more skills over time — each skill is a self-contained directory under `skills/`.

## Install

```bash
git clone https://github.com/NIMBUS-MX/nimbus-skills.git ~/Development/nimbus-skills
cd ~/Development/nimbus-skills
./install_skills.sh
```

Restart Claude Code. Skills auto-load on session start.

The install script:
- Copies each skill under `skills/` into `~/.claude/skills/` (user-scope, available in every session).
- Idempotent — re-running overwrites, no duplication.
- Prints one line per skill installed.

## Uninstall

```bash
./install_skills.sh --uninstall
```

Removes any skill this repo installed (matched by name).

## Layout convention

```
nimbus-skills/
├── README.md
├── install_skills.sh
├── skills/
│   └── <skill-name>/
│       ├── SKILL.md           # frontmatter with `name` + `description` + prose body
│       ├── templates/         # optional — assets the skill references
│       └── scripts/           # optional — helper scripts the skill shells out to
└── docs/                      # optional — deeper docs per skill
```

## Adding a new skill

1. `mkdir skills/<skill-name>`.
2. Create `skills/<skill-name>/SKILL.md` with frontmatter:
   ```markdown
   ---
   name: <skill-name>
   description: >
     One-paragraph description Claude sees to decide when to invoke. Include
     trigger phrases + slash commands.
   ---

   ## Prose body
   ...
   ```
3. Add row in the table at the top of this README.
4. Commit + open PR.

## Skill discoverability

Once installed, Claude Code auto-loads skills at session start. In-session, they appear via:
- `/help` — lists user-invocable slash commands (only skills whose SKILL.md declares a command name will show here).
- The `Skill` tool — Claude uses this to invoke a skill by name when a trigger matches.

## Contact

Owner: Nimbus / CIDCA engineering.
