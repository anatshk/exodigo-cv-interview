# Exodigo CV interview: manhole detection from Street View

Preparation for the technical question of the Exodigo Computer Vision interview.

## The task

Design a system that uses Google Street View panoramas (multiple years per location) to:

1. Detect manholes on the road surface.
2. Classify detected manholes by cover type (for example sewer, water, communication),
   using a small set of regional examples that illustrate local conventions, not a fixed
   label set.
3. Output geospatial detections (a GIS layer or map overlay) that can be compared with
   other sensor-based underground utility estimations. US only.

No code is required. The interview expects reasoning for each decision: problem
definition, data and preparation, models and learning paradigms, parameter selection,
and evaluation. Full brief: [`Interview_Preparation.pdf`](Interview_Preparation.pdf).

## Write-up

The design is in [`WRITEUP.md`](WRITEUP.md): the final system, labeling and training,
evaluation, challenges, assumptions and open questions, with figures.

## Repository layout

| Path | Contents |
|---|---|
| `Interview_Preparation.pdf` | The task brief, as received. |
| `WRITEUP.md` | The design write-up for the interview. |
| `images/` | Sample panorama strips (`.png`, 4:1) with metadata (`.json`: `panoId`, `lat`, `lng`, `heading`, `tilt`, `roll`, `date`, image size). |
| `docs/` | Work log, plan, brainstorm. `docs/figures/`: write-up figures. |
| `ai-chats/` | Transcripts of the AI-assisted working sessions. |
| `scripts/`, `tests/` | Session-transcript tooling (converts Claude Code session logs to Markdown). `scripts/make_figures.py` regenerates the raster figures. |
