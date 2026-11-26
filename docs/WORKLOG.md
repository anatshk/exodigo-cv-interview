# WORKLOG

Reverse-chronological, newest first. Concise highlights: what was done and the decisions
made, not a blow-by-blow.

## 2026-11-26: Fact checking and wrap-up

- All "(to verify)" items in `WRITEUP.md` and open todos in `docs/BRAINSTORM.md` resolved.
- Naming fixes agreed with Anat: "undistortion" became IPM (inverse perspective mapping,
  defined in new section 8 "Terms"); Hough became circle/ellipse detection (round covers
  look like ellipses); line fitting is multi-model fitting (sequential RANSAC); cKDTree works
  on coordinates converted to meters; CLIP text encoder replaces "word2vec-like"; JEV is the
  TypeSafe AI commercial decision model (open-weight Jev-Omni).
- Decision: triangulation is the main location method, because camera height (about 2.5 m,
  unofficial) and GPS accuracy are unpublished. Module 4 is "Deduplication + triangulation".
  Output is GeoJSON.
- Decision: Ultralytics is AGPL-3.0, so RF-DETR (Apache 2.0) is the fallback. LVIS has a
  "manhole" class, so YOLOE / YOLO-World may detect covers directly; OWLv2 and SAM 3 dropped.
- Note: YOLO perspective/shear augmentations cannot simulate panoramic distortion (to
  re-examine). Occlusion augmentation is Cutout / Random Erasing (CoarseDropout).
- Finding: sample PNG strips are 360 x 90 deg with the horizon on the middle row; one
  metadata file says 16384x8192.
- Decision: Anat reviewed `WRITEUP.md` and considers it final; she presents directly from
  it, so phase 3 (presentation material) is dropped.

## 2026-11-26: PDF review and write-up draft

- Brainstorm reviewed against the PDF. Added to `docs/BRAINSTORM.md`: parameter tuning
  (out of current scope), known objects database per region and duplicates over time,
  provider dictionary in output, metadata assumptions (equirectangular, tilt ~90 = level,
  camera height plus flat ground), triangulation from multiple images, Task 2 as
  unsupervised/semi-supervised. Sensor estimations are weak labels only if the system is
  not meant to add confidence to them (otherwise leakage).
- `WRITEUP.md` draft (README points to it): final system first, then labeling and training,
  parameter selection, evaluation, challenges, assumptions, open questions. Module 5 renamed
  "Confidence reviewer" (straight-line score plus years-seen score from the known objects
  database).
- Decision: write-up is `WRITEUP.md`, not README (Anat's choice). Draft first, fact
  finding after, unverified items marked "(to verify)".
- Decision: pipeline diagram is a hand-drawn SVG, not Mermaid: Mermaid drops the row layout
  when a node links across rows. SVGs have explicit width/height so they render large in
  Obsidian.
- Finding: all 5 sample panoramas are one Detroit intersection (2007 to 2025); PNGs are
  4:1 strips while the metadata says 2:1. Recorded as a question for Exodigo.
- Anat edits write-up text; Claude does visuals. No PRs in this repo.

## 2026-11-26: Points for consideration brainstormed

- New "Points for consideration" section in `docs/BRAINSTORM.md` covers all six PDF points:
  problem definition, data and preparation, models and learning paradigms (with gaps Claude
  found on request, each answered by Anat), system components (7, with inputs and outputs:
  tiling, detector, coordinate conversion with out-of-US alert, dedup by region with
  cKDTree, RANSAC straight line checker, classifier, output formatting with final
  confidence), success measurement, challenges and failure modes.
- Task 1 and Task 2 sections extended with the new items (open-vocabulary detectors, active
  learning, augmentations, panorama input, duplicate removal, output, challenges, kNN
  cluster labeling, outlier step, classifier scope, zero-shot option), plus new open
  questions, todos and assumptions.
- Decision: points are recorded in their own section and cross-referenced into the task
  sections, as Anat asked.
- Decision: Claude's factual answers were from memory, so they are listed as todos for
  fact finding.
- Anat plans to propose one final pipeline from all options at the end.

## 2026-11-26: Task 2 brainstormed

- `docs/BRAINSTORM.md` has a new Task 2 section (classify covers by type), scribe mode:
  problem understanding; deterministic approach (shape, OCR, texture, size, color features,
  PCA plus clustering, labeling by examples, human or VLM; image-encoder alternative with
  parallel OCR); non-deterministic approach (VLM structured descriptions, "unknown" per
  feature for human escalation); cost and latency note; open questions and todos.
- Decision: use LLMs/VLMs only to gather training data or for unexpected edge cases, not in
  the main path (cost and latency).
- Decision: tool name "JEV" kept exactly as Anat wrote it; verify in fact finding.
- Two Task 2 assumptions added to the global Assumptions list.
- Session log continued in `ai-chats/02-brainstorm.md` (no new 03 file).

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
