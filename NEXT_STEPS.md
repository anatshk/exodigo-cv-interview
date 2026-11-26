# NEXT_STEPS

Resume pointer. Read this first.

## Where we are (2026-11-26)

Brainstorm (phase 1) is done: reviewed against `Interview_Preparation.pdf`, final pipeline
chosen (the full 7-module system). Design (phase 2) is in progress: `WRITEUP.md` draft is
done (final system, building the models, parameter selection, evaluation, challenges,
assumptions, open questions), with figures in `docs/figures/` (`scripts/make_figures.py`
regenerates the three JPGs; needs Pillow and pdftoppm). Unverified claims are marked
"(to verify)". All work is committed and pushed to main (this repo has no PRs).
Session log: `ai-chats/03-pdf-review.md`.

Finding: all 5 sample panoramas are the same Detroit intersection, 2007 to 2025. The PNGs
are 4:1 strips (about +/-45 deg around the horizon) but the metadata says 13312x6656 (2:1),
so the vertical angle per pixel must come from the real image.

Working split: Anat edits the write-up text; Claude does visual changes.

## Pick up here

1. Fact checking: go through every "(to verify)" in `WRITEUP.md` and the open todos in
   `docs/BRAINSTORM.md`: Street View projection and vertical FOV of API images (4:1 vs 2:1),
   camera height, meaning of heading/tilt/roll, camera lat/lng accuracy, GIS output format,
   Ultralytics license, open-vocabulary detectors (Grounding DINO, OWLv2, YOLO-World,
   moondream2, Qwen-VL), zero-shot classifiers (OpenCLIP, SigLIP 2), cut-out augmentation
   name, texture filter family, the tool Anat named "JEV", line fitting method, US manhole
   standards. Then remove the "(to verify)" marks and update the brainstorm.
2. Continue Anat's review of the `WRITEUP.md` visuals as notes come in.
3. Phase 3: presentation material.

## Open questions

- Presentation format: slides, the write-up, or both.
- Questions for Exodigo in `WRITEUP.md` section 7 (maybe send before the interview).

## Non-git state

- Untracked `claude_logs/` (handover logs): origin predates this session, do not commit.
- `.venv/` local (dev tools only).
