## User

this is a folder of a take-home task for a job interview at exodigo. i want you to initialize a private github repo and upload the files. i'll come back later and we'll do a brainstorming session. i want to work here similarly to the work in the psistar repo - log my sessions with claude (including this one), use WORKLOG.md and other tracking files. this session is just a setup, i'll start actual work on Thursday, Nov 26th.

## Assistant

I set up the repo, committed everything, and pushed it to a new private GitHub repo: `anatshk/exodigo-cv-interview`.

**What I added, based on the psistar setup:**
- `ai-chats/`: `01-setup.md` (this session), `README.md` (the logging convention), and `work-style/` (current copies of your global CLAUDE.md, the handover skill, and the handover-writer agent).
- Session logging tooling: `scripts/session_to_md.py` with its test, the Stop and SessionStart hooks, `.claude/settings.json`, and the `/save-chat` skill. The auto backups go to `ai-chats/_auto/`, which is gitignored.
- Tracking docs: `NEXT_STEPS.md`, `docs/WORKLOG.md`, and `docs/PLAN.md` (phase 0 done, phases 1 to 3 not started).
- A thin `CLAUDE.md`, `README.md`, `.gitignore`, `local/README.md`, `pyproject.toml`, and `requirements-dev.txt`.
- The task inputs as you received them: `Interview_Preparation.pdf` and `images/`.

**Decisions:**
- The task is a design question with no code, so `CLAUDE.md` says the Python and TDD rules apply only to the tooling and to any analysis scripts we add later.
- In the copied docs I replaced the em dashes with other punctuation. The `work-style/*.txt` files are exact copies, so I did not change them.
- `.venv` was created and the 4 tooling tests pass.

**Note:** the hooks in `.claude/settings.json` start working in your next session (you may need to approve them once). For this session I created the auto backup by hand.

`NEXT_STEPS.md` lists what to do on Thursday: the brainstorm, open questions and assumptions, and splitting phases 2 and 3 into steps.
