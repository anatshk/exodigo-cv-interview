# ai-chats

Verbatim transcripts of every AI working session on this project, tracked in git.
Same convention as in earlier take-home projects: every session is logged.

## Format

- **One markdown file per session.** Named `NN-slug.md` with a zero-padded, incrementing
  number and a short kebab-case topic slug, e.g. `01-setup.md`, `02-data-model.md`.
- Each turn is recorded as:

  ```markdown
  ## User

  <the user's prompt, verbatim>

  ## Assistant

  <the assistant's full reply, verbatim>
  ```

- **Turns are kept in order, newest appended at the bottom.** Never reorder.
- **Verbatim**: do not summarize, paraphrase, trim, or "clean up" prompts or replies.
- The `## Assistant` block records the assistant's visible reply prose. Tool calls and
  their raw output are not reply text and are omitted unless explicitly requested.

## Starting a new file

By default all turns in one working session go in that session's single file. **The user
can say "start a new file" at any point**: when they do, the current file is closed and a
new `NN-slug.md` (next number, new slug) begins from the following turn. Use this to split
long sessions or to give a distinct sub-task its own transcript.

## Two tracks: curated + auto backup

The risk with a hand-maintained transcript is a forgotten turn. Claude Code stores each
session as a JSONL transcript on disk (`~/.claude/projects/<project-slug>/<session-id>.jsonl`,
with `user`- and `assistant`-typed records), so the conversation can be reconstructed
independently. This project uses that to run two tracks:

- **Curated**: the `NN-slug.md` files above, authored by hand for readability. Primary,
  human-facing, may include things the raw transcript doesn't surface as prompts (e.g.
  `AskUserQuestion` answers).
- **Auto backup**: `_auto/<session-id>.md`, generated from the JSONL by
  `scripts/session_to_md.py`. Same prose-only format, a complete safety net.
  **Machine-generated: do not hand-edit, and gitignored** (a local recovery aid, not part
  of the tracked history). The curated `NN-slug.md` files are the tracked record.

The auto track is wired up so nothing is lost even if a turn is never curated:

- `Stop` hook (`scripts/save_session_hook.sh`) refreshes the current session's backup after
  every turn.
- `SessionStart` hook (`scripts/backfill_sessions_hook.sh`) back-fills any earlier session
  that has no backup yet. This is how a new session "reaches back" and saves previous ones.
- `/save-chat` skill regenerates the backup on demand and helps keep the curated file
  current, including "start a new file" splits.

Both hooks are registered in `.claude/settings.json` and fail open (never block a session).
The converter is standard-library only so the hooks run without an activated venv.
