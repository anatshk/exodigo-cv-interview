# WORKLOG

Reverse-chronological, newest first. Concise highlights: what was done and the decisions
made, not a blow-by-blow.

## 2026-11-26: Brainstorm started (Task 1)

- Brainstorm runs in scribe mode: Claude records Anat's ideas, todos and questions one
  item at a time and adds no input of its own.
- `docs/BRAINSTORM.md` created. Task 1 is complete: available data, detection process
  (labeled case: YOLO fine-tune; unlabeled case: pretrained model plus FP logic plus VLM
  cleaning, classical Hough/edge detection and clustering as a label source), conversion
  to geospatial coordinates, dataset setup, validation (US only), open questions, todos,
  writeup notes.
- Decision: the doc is organized per task, each with its own open questions, todos and
  writeup notes; a global Assumptions list at the bottom is tagged by task.
- Session log: `ai-chats/02-brainstorm.md`.

## 2026-11-24: Repo setup

- Created the private GitHub repo and committed the task inputs as received
  (`Interview_Preparation.pdf`, `images/`).
- Session logging and tracking set up: `ai-chats/` transcripts (curated `NN-slug.md`
  plus an auto backup written by Stop and SessionStart hooks), `/save-chat` skill,
  `NEXT_STEPS.md`, this log, and `docs/PLAN.md`.
- Decision: the task is a design question with no code, so `CLAUDE.md` limits the Python
  and TDD rules to the transcript tooling and any analysis scripts we add later.
- No design work yet. Actual work starts Thursday 2026-11-26 with a brainstorming session.
