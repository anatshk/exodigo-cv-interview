---
name: save-chat
description: Save the current conversation to the tracked ai-chats/ folder. Use when the user says "save chat", "save the conversation", "/save-chat", or asks to checkpoint the transcript now instead of waiting for the automatic Stop-hook backup. Also handles "start a new file" splits for the curated transcript.
---

# save-chat

This project requires every conversation to be saved under the tracked `ai-chats/`
folder. Two tracks keep that reliable (see `ai-chats/README.md`):

- **Curated** `ai-chats/NN-slug.md`: the readable, human-facing transcript you author by
  hand as the session goes: `## User` / `## Assistant`, in order, appended at the bottom,
  verbatim, prose only.
- **Auto backup** `ai-chats/_auto/<session-id>.md`: machine-generated from the session
  JSONL by `scripts/session_to_md.py`, refreshed automatically by the `Stop` hook and
  back-filled by the `SessionStart` hook. Never hand-edit these.

Invoking this skill does two things.

## 1. Refresh the auto backup now

Don't wait for the next `Stop`. Regenerate the current session's backup immediately:

```bash
TRANSCRIPT=$(find "$HOME/.claude/projects" -name "${CLAUDE_CODE_SESSION_ID}.jsonl" 2>/dev/null | head -1)
python3 scripts/session_to_md.py "$TRANSCRIPT" -o "ai-chats/_auto/${CLAUDE_CODE_SESSION_ID}.md"
```

If `CLAUDE_CODE_SESSION_ID` is unset, ask the user which session file, or fall back to the
newest `*.jsonl` under this project's transcript directory.

## 2. Bring the curated file up to date

Make sure the curated `NN-slug.md` for this session includes every turn so far, verbatim,
appended in order. The auto backup is a good cross-check for anything you missed, but the
curated file may legitimately hold more than the backup (e.g. `AskUserQuestion` answers,
which arrive as tool results and so never appear as typed prompts in the auto version).

### "Start a new file"

If the user says **start a new file** (optionally naming a topic), close the current
curated file and begin the next one: `NN-slug.md` with the next zero-padded number and a
short kebab-case slug. From that point on, new turns go in the new file. This split is a
curated-track concept only; the auto backup stays one file per session regardless.

## Report back

State which files you wrote or updated (curated path, auto path) and confirm the transcript
is current through the latest turn.
