---
name: ticket-brief
description: >
  Fetch a ClickUp/Linear/GitHub ticket URL, summarize into a
  work-brief: goal, acceptance criteria, blast radius, suggested branch name,
  suggested commit prefix, related repos.

  Trigger this skill when:
  - User pastes a `*.clickup.com/t/…` URL.
  - User pastes a `linear.app/…/issue/…` URL.
  - User pastes a `github.com/*/issues/…` or `pull/…` URL.
  - User says "brief this ticket", "summarize this issue", or invokes
    `/ticket-brief`.
---

## Prerequisite

- **ClickUp**: `mcp__clickup__*` tools available via ClickUp MCP.
- **GitHub**: `gh` CLI authenticated.
- **Linear**: Linear MCP if configured (fall back to WebFetch if not).

Check with `ToolSearch`. If the source is unreachable, tell the user which
MCP/tool needs setup.

## Behavior

1. **Detect source** from URL pattern.
2. **Fetch**:
   - ClickUp: `mcp__clickup__clickup_get_task(task_id=…, include=["description"])`.
   - GitHub: `gh issue view <url> --json title,body,labels,assignees,state`.
   - Linear: Linear MCP fetch.
3. **Distill** into a brief with these sections:
   - **Goal** (one sentence, imperative).
   - **Why** (business/technical reason if stated).
   - **Owner** + deadline if stated.
   - **Acceptance criteria** (checklist, pulled from ticket body).
   - **Blast radius**: which repos, which subprojects, which files.
   - **Suggested branch name**: `<prefix>/<slug>` where prefix follows the
     Nimbus commit convention (feat/fix/chore).
   - **Suggested commit prefix**: `<type>(<scope>): …`.
   - **Dependencies / blockers** if any.
   - **Ticket URL** at the end.
4. **Format** as a compact Markdown brief, ≤ 30 lines.

## Nimbus-specific inferences

- Ticket mentions `ecg-ui/…` or React component → frontend PR in cidca-platform.
- Ticket mentions `ecg-*-lambda` → cidca-services repo, specific lambda dir.
- Ticket titled `[FERIA] …` → part of the July 8 event sprint (ClickUp list `Sprint 36`).
- Ticket mentions `Reporte v1 CIDCore` → touches `HTMLReportTemplate` row seed
  + `ecg-gw-parsescp-lambda/view_ecg.py` (see samples in cidca-platform if
  present).

## Do not

- Assume you can auto-implement from the brief — always confirm scope with user first.
- Include the full ticket body — you're distilling, not copying.
- Include secrets that appear in the ticket body (Vercel URLs with tokens, etc.).
- Modify the ticket (add comments, change status) unless user asks.

## Follow-up

After presenting the brief, ask the user: `Start on this? (branch name / next
step)`. Let them choose whether to proceed or defer.
