# work-style

Read-only copies of the global Claude Code configuration that shaped how this repo was
built. They live here so a reviewer can see the working conventions and tooling behind the
commit history and the `ai-chats/` transcripts: the "how", alongside the "what".

**These are copies, not active configuration.** The real files live in `~/.claude/` on the
author's machine. They are stored here with a `.txt` extension on purpose: a stray
`CLAUDE.md` or `SKILL.md` inside the repo could be auto-discovered and loaded as live
instructions, which would interfere with normal work. The `.txt` copies are inert.

## Contents

| File | Copy of | What it shows |
|---|---|---|
| `house-rules.txt` | `~/.claude/CLAUDE.md` | The global working agreement: plan-first, minimal diffs, TDD (red→green→refactor), Conventional Commits, PR-per-concern, handover discipline, and the `.secrets/` vs `local/` separation. |
| `handover-skill.txt` | `~/.claude/skills/handover/SKILL.md` | How a work phase is closed out for a clean `/clear`: the expensive model writes a decisions brief, then delegates the mechanics. |
| `handover-writer-agent.txt` | `~/.claude/agents/handover-writer.md` | The cheap subagent that turns that brief into committed `NEXT_STEPS.md` / `WORKLOG.md` / phase-tracker updates, the mechanics half of the split. |

The handover skill and its writer agent are a deliberate two-model design: keep reasoning on
the capable model, push repetitive git-and-docs mechanics onto a cheaper one working in a
fresh context.
