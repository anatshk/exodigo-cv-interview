# NEXT_STEPS

Resume pointer. Read this first.

## Where we are (2026-11-26)

The project is effectively done. `WRITEUP.md` is final (reviewed by Anat) and is the
material for the interview: she presents directly from it, so there is no separate
presentation. Fact checking is complete: no "(to verify)" items remain, and
`docs/BRAINSTORM.md` is updated. Everything is committed and pushed to main (this repo has
no PRs). Session log: `ai-chats/03-pdf-review.md`.

Key facts settled: triangulation is the main location method (camera configuration unclear);
output is GeoJSON; sample PNGs are 360 x 90 deg strips with the horizon on the middle row;
Ultralytics is AGPL-3.0 (RF-DETR is the Apache 2.0 fallback); LVIS has a "manhole" class, so
YOLOE / YOLO-World may detect covers directly.

## Pick up here

Nothing required. Optional:

1. Send the `WRITEUP.md` section 7 "For Exodigo" questions before the interview.
2. If time: check which image column `heading` maps to on the 5 sample panoramas (same
   intersection, different headings).

## Open questions

- Camera height and lat/lng accuracy (not published).
- Which image column `heading` maps to.
- Zero-shot classifier (OpenCLIP, SigLIP 2) on real crops: untested.
- For Exodigo: covers vs utility line goal, ground truth availability, types vs providers,
  confirming sensor estimations, vertical FOV of API images.

## Non-git state

- Untracked `claude_logs/` (handover logs): origin predates sessions, do not commit.
- `.venv/` local (dev tools only).
