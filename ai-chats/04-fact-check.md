## User

i want you to go over @WRITEUP.md and @docs/BRAINSTORM.md and do fact checking - if a concept or a method are mentioned (hough transform or yolo detector for example, but there are many others) - make sure i did not confuse the name. description of what it does shuold win over exact name, but show me the conflicts and ask me what i meant before changing anything. also look for "to verify" or other signs of things that need t be checked and do that with web search.

## Assistant

I checked both files against web sources and the sample data in `images/`. I have not changed anything yet. Findings are in three groups, and the questions for you are at the end.

### A. Possible name or description conflicts (I need your answer)

| # | Where | What you wrote | Issue |
|---|---|---|---|
| A1 | WRITEUP 1.1, 1.6; BRAINSTORM "Panorama input" | "Undistortion" of the panorama | "Undistortion" usually means correcting lens distortion. For an equirectangular panorama the usual term is **reprojection** to a perspective (rectilinear) view. If you meant a view looking down on the road, the term is **inverse perspective mapping (IPM)** or a bird's-eye view. In that view round covers look round again. |
| A2 | BRAINSTORM "Classical method" | Hough transform for round covers | The name is correct. But a round cover on the ground looks like an **ellipse** in the image, so a Hough *circle* transform will miss it. You would need ellipse detection (for example `skimage.transform.hough_ellipse`) or IPM first. |
| A3 | WRITEUP 1.1 | "YOLO perspective and shear augmentations may make undistortion unnecessary" | The names are correct: Ultralytics has `perspective` and `shear`, both 0 by default. But they are flat (planar) transforms. They do not reproduce the curved equirectangular distortion, so the claim is weaker than it reads. |
| A4 | WRITEUP 1.6, 2.4 | "semi-supervised, open-set classification" | The common term is **few-shot open-set recognition**. "Semi-supervised" is also correct, but only because the clustering step uses unlabeled crops. Which one do you mean? |
| A5 | WRITEUP 1.4 | cKDTree on lat/lng | The name is correct. But in lat/lng degrees, distances are not meters (1° of longitude ≠ 1° of latitude). Convert to a local metric system (UTM or local ENU) first, or use `sklearn` BallTree with the haversine metric. A radius search already skips points that are far away, so "per region" mainly keeps the database small. It does not change the parallel-streets result. |
| A6 | WRITEUP 1.5 | "RANSAC or a newer method" | Plain RANSAC fits **one** model. Several lines in one area is **multi-model fitting**: sequential RANSAC, J-Linkage / T-Linkage, or Progressive-X (2019, and the newer Progressive-X+). MAGSAC++ is a better single-model RANSAC, so it does not solve the multi-line case alone. |
| A7 | BRAINSTORM "VLM description route" | "word2vec-like embedding space" | word2vec embeds single words. For short structured answers the matching tool is **sentence embeddings** (for example sentence-transformers) or the CLIP text encoder. Is that what you meant? |
| A8 | BRAINSTORM "Clustering and labeling" | "PCA first, to see if some signals are more relevant" | PCA shows where the variance is, not which features matter for the labels. Feature importance or ablation measures relevance. Did you mean variance or relevance? |
| A9 | BRAINSTORM, Task 2 | "JEV" | Search found a **Jev** decision model by TypeSafe AI. It takes images and asks structured questions with fixed answer options. It is commercial (API only), and an open-weight version exists: **Jev-Omni** (12B, Gemma-based, Apache 2.0). I only saw search snippets. Is this the tool you meant? |

### B. "To verify" items, results

| Item | Result |
|---|---|
| `tilt` / `heading` / `roll` | **Confirmed** (Street View Tiles API docs). `tilt` is in degrees, range 0-180, and 90 means level. `heading` is the compass direction, clockwise from north. `roll` is the clockwise correction applied to level the horizon. Not found: which image column `heading` maps to (center or left edge). Check it on one sample against the known street direction. |
| Equirectangular | **Mostly confirmed**: full panorama at 2:1 made of 512-pixel tiles, and tile-stitching libraries output equirectangular images. Google gives no explicit statement. |
| 4:1 strip | **New finding.** `AIKDeNPSCxU2Ckvxnvom-w.json` says **16384 x 8192**, not 13312 x 6656. In both cases the PNG width is full width / 4 and the height is full height / 8. So the strip covers 360° horizontally and **90° vertically**. The image sizes alone cannot show that the strip is centered on the horizon (±45°): find the horizon row in the image. The write-up should list both metadata sizes. |
| Camera height | About **2.5 m** (secondary source, not official, may differ between camera generations). |
| Camera lat/lng accuracy | **No official figure found.** Research shows meter-level errors in systems built on Street View. Still open. One search summary said "accurate to 50 m", but that is probably the API's default search radius, so I did not count it. |
| Ultralytics license | **Confirmed: AGPL-3.0, and models you train with it are AGPL too.** Closed-source commercial use needs the Enterprise license (Roboflow also resells it). Permissive alternative: RF-DETR (Apache 2.0) *(from my own knowledge, not checked in this session)*. |
| Pretrained class with manhole | COCO, Objects365 and Open Images V7: **no** manhole class. **LVIS has "manhole" (class 667)**, so YOLOE or YOLO-World with an LVIS vocabulary may detect covers with no training. This is a strong point for Case B. |
| Open-vocabulary detectors | Grounding DINO, OWLv2 and YOLO-World are correct names. moondream2 and Qwen-VL are VLMs that can return boxes, not detectors. Newer options: **YOLOE** (2025, AGPL), **SAM 3** (Meta, Nov 2025, text prompt to masks, custom license), Florence-2. One study found YOLO-World weak on small objects, which matters here. |
| Zero-shot classifiers | OpenCLIP and SigLIP 2 are correct names. |
| Cut-out augmentation name | **Cutout** (DeVries and Taylor 2017) or **Random Erasing** (Zhong et al. 2017). Ultralytics `erasing` is for classification only. For detection use Albumentations `CoarseDropout`. |
| Texture filter family | Gabor filters, Local Binary Patterns (LBP), GLCM / Haralick features. |
| US manhole standards | There is **no single national size**. AASHTO M306 covers casting load, not size. Common diameters are 22-36 in (about 0.55-0.9 m), set per agency in its standard drawings. This is still useful as a size range for filtering detections. |
| GIS output format | **GeoJSON** (RFC 7946): WGS84, coordinate order **[lng, lat]**. GIS tools and web maps both read it, so the brainstorm question about "map overlay vs GIS" mostly goes away. GeoPackage is the choice for large layers. |

### C. Questions

1. A1: reprojection to a perspective view, or a top-down (IPM) view?
2. A2: add the ellipse point, or leave it? The classical method is only a fallback.
3. A4: "few-shot open-set" or "semi-supervised open-set"?
4. A7, A8, A9: did I read your intent correctly?
5. A3, A5, A6 and section B: should I apply these to both files and remove the matching "(to verify)" marks? Your memory note says you edit the write-up text, so I can also give you the exact wording to paste in.

Sources:
- [Street View Tiles API](https://developers.google.com/maps/documentation/tile/streetview)
- [Photo Sphere XMP metadata](https://developers.google.com/streetview/spherical-metadata)
- [Phys.org, Street View camera height](https://phys.org/tags/street+view)
- [Ultralytics licensing](https://www.ultralytics.com/license)
- [Roboflow on the YOLO26 license](https://roboflow.com/model-licenses/yolo26)
- [Ultralytics augmentation guide](https://docs.ultralytics.com/guides/yolo-data-augmentation)
- [Ultralytics dataset configs on GitHub](https://github.com/ultralytics/ultralytics/tree/main/ultralytics/cfg/datasets)
- [Open-vocabulary detectors in unusual street scenes](https://arxiv.org/pdf/2408.11221)
- [YOLOE-26](https://arxiv.org/html/2602.00168)
- [Roboflow, SAM 3 vs YOLOE](https://playground.roboflow.com/models/compare/seg-preview-vs-yoloe)
- [Progressive-X](https://arxiv.org/pdf/1906.02290)
- [MAGSAC++](https://arxiv.org/pdf/1912.05909)
- [RFC 7946 (GeoJSON)](https://datatracker.ietf.org/doc/html/rfc7946)
- [Oregon DOT drawing RD356](https://www.oregon.gov/ODOT/Engineering/202601/RD356.pdf)
- [WSSC standard drawing](https://www.wsscwater.com/sites/default/files/2021-09/28%20-%20PM%206.2.pdf)
- [How Jev makes decisions about images](https://towardsdatascience.com/how-jev-makes-decisions-about-images-with-4-python-examples/)
- [Jev-Omni](https://sourceforge.net/projects/jev-omni/)
- [Releasing the Inner Jev](https://arxiv.org/pdf/2610.17205)
- [Street View localization accuracy study](https://arxiv.org/pdf/2411.08231v2)

## User

A1 - replace "undostortion" with IPM, but make sure to definethe term (full name + panorama to bird's eye view). you can make a small section of terms at the end and ass it there. A2 - replace "hough transform" with "circle/ellipse detection", mention (Hough transform, for example) the first time it's mentioned. A3 add a note: (NOTE: fact-checking revealed that yolo transformation cannot simulate panoramic distortion, so augmentations need to be re-examined). A4 - i want to mention the semisupervised clustering part make sure it's there. A5 add "convert to meters if needed". A6 - use "multi model fitting - sequential RANSAC for example". A7 - replace with CLIP text encoder. A8 - i'm using PCA to see which features matter for detrminig which points belong to which cluster - it is easier to visualize after PCA, "feature importance" is not related here i think.  A9 - yes, add the short dscription you provided (it takes... ... options". now let's go over the "to verify" items and suggest changes one at a time.

## Assistant

Applying the edits to `WRITEUP.md` first.

Now `docs/BRAINSTORM.md`.

I applied A1 to A9 in both files (not committed). Notes:
- **A1 IPM:** a new section `## 8. Terms` at the end of `WRITEUP.md` (also added to Contents) defines it. In `BRAINSTORM.md` I wrote the full name at the first mention.
- **A2:** "Hough transform, for example" appears only at the first mention in each file. Later mentions say "circle/ellipse detection".
- **A3:** I put the note in `WRITEUP.md` 1.1 and in both brainstorm places where the YOLO augmentations are mentioned.
- **A6:** this also removed one "(to verify)" in `WRITEUP.md` 1.5.
- **A8:** I rewrote the PCA line in `BRAINSTORM.md` with your meaning. One caution: PCA shows the directions of largest variance. These usually separate the clusters, but not always, so check it on the plot.
- **A9:** I kept the original JEV line and added the description under it as a "Fact check" bullet.

### "To verify" 1 of 7: Ultralytics license (`WRITEUP.md` 1.2)

Current:
> License for production use *(to verify)*.

Suggested:
> License: AGPL-3.0, and models trained with it are AGPL too. Closed commercial use needs a paid Enterprise license. Fallback with a permissive license: RF-DETR (Apache 2.0).

I have not checked the RF-DETR license in this session. I can check it before we use it, or we drop that sentence. In `BRAINSTORM.md` I would mark the matching todo (line ~29 and the Todos list) as checked, with the same fact.

Apply as is, change it, or drop the RF-DETR part?

## User

apply ultalytics license as is , check RE-DETR.

## Assistant

The Ultralytics license is now in both files, with the RF-DETR limit. I also marked the brainstorm todo as done.

### "To verify" 2 of 7: projection and image size (`WRITEUP.md` 1.3, plus 2 rows in section 6)

Facts: Google's docs confirm a 2:1 panorama made of 512-pixel tiles. Equirectangular is not stated in words, but the tile-stitching tools use it. A new finding from the samples: one metadata file says 16384 x 8192, not 13312 x 6656. In all 5 samples the PNG is full width / 4 and full height / 8, so the strip covers 360° x 90°. The sizes alone do not show that the strip is centered on the horizon.

**1.3, first bullet**, suggested:
> - The panorama is equirectangular (2:1 tiles in the Street View Tiles API), so each pixel maps directly to an angle. Caution: the metadata says 13312 x 6656 or 16384 x 8192 (2:1). The sample files are 4:1 strips at 1/4 of the width and 1/8 of the height, so they cover 360° x 90° (about ±45° around the horizon, to check on the image). The vertical angle per pixel must come from the real image, not the metadata size, or every distance is wrong.

**Section 6, row "Panoramas are equirectangular..."**, reason column:
> Metadata is 2:1 (13312 x 6656 or 16384 x 8192), as in the Street View Tiles API.

The `tilt` part of this row goes to item 3.

**Section 6, row "The sample PNGs are a 4:1 strip..."**, reason column:
> Sample files are full width / 4 and full height / 8 (4096 x 1024 or 3328 x 832), so 360° x 90°. The horizon row is still to check on the image.

Two questions:
1. Should I check the horizon row on the 5 samples now? It is a quick script: find the row where the road meets the buildings. If it is at the middle of the strip, the ±45° claim is confirmed and the "to check" goes away.
2. Apply the text as written, or change it?

Source: [Street View Tiles API](https://developers.google.com/maps/documentation/tile/streetview)

## User

check the horizon. if the known paramerters do not provide enough scertainty, add moreweight to triangulation from sequential images to find exact location

## Assistant

Fixing two error numbers to match the calculation (1.5 m at 20 m, 3.5 m at 30 m).

**Horizon check:** I drew the middle row on 3 samples (2007, 2011, 2020). The far ends of the streets sit on that row in all of them. So the strips are 360° x 90°, ±45° around the horizon, and the panoramas are already leveled.

**Certainty is not enough for one view.** The camera height (about 2.5 m) is not an official figure, Google does not publish the GPS accuracy, and with a 2.5 m camera a 0.5° angle error moves a cover about 0.4 m at 10 m, 1.5 m at 20 m and 3.5 m at 30 m. So I made triangulation the main location method:
- **1.3:** the new "Single view is not exact enough" and "Triangulation (main location method)" bullets replace the old "Improvement step". Panoramas are about 10 to 20 m apart, so most covers are seen several times. The single-view estimate is still used to match the views of one cover, and to locate covers seen only once (with lower confidence).
- **Pipeline table:** module 4 is now "Deduplication + triangulation".
- **Section 6:** I updated the projection, strip and camera-height rows.
- **`BRAINSTORM.md`:** I added a fact-check note under "Location improvement step".

### "To verify" 3 of 7: `tilt` / `heading` / `roll` (section 6, plus section 7 "To verify")

Facts from the Street View Tiles API docs:
- `tilt` is in degrees, range 0 to 180, and 90 means level. `roll` is the clockwise correction that levels the horizon. Both describe a correction that is already applied, which matches the horizon check.
- `heading` is the compass direction, clockwise from north.
- Not documented: which image column `heading` maps to (center or left edge). I can check this on the samples. The 5 panoramas show the same intersection with different `heading` values, so if `heading` is the center column, the same building should shift by exactly the heading difference.

Suggested text for the section 6 row, reason column:
> Metadata is 2:1 (13312 x 6656 or 16384 x 8192), as in the Street View Tiles API. Tiles API: `tilt` in degrees, 90 = level; `heading` is the compass direction, clockwise from north; `tilt` and `roll` are corrections already applied (the horizon is on the middle row in the samples).

In section 7 "To verify", I would change the line to "camera height" only. The camera lat/lng line stays open, since there is no published figure.

Should I run the heading-column check first, then apply?

Source: [Street View Tiles API](https://developers.google.com/maps/documentation/tile/streetview)

## User

i think we can summarize this section with "the configuration with which the images was taken are unclear, what we know is" then details what we know, and add that conbining information from several images can lwer the uncertainty.

## Assistant

Done. In `WRITEUP.md` 1.3 the "Single view is not exact enough" bullet is now **"Camera configuration"**. It says the configuration is unclear, lists what we know (height, GPS, `heading`, `tilt`/`roll`, how the error grows with distance), and ends with "Combining information from several images lowers this uncertainty (triangulation, next)". I also removed the "(to verify)" in the section 6 row. In section 7, the open items are now camera height, lat/lng accuracy and the `heading` column. In `BRAINSTORM.md` I marked the three matching open questions as checked.

### "To verify" 4 of 7: output format (`WRITEUP.md` 1.7)

Current:
> - Format: a GIS layer or map overlay *(format to verify)*.

Suggested:
> - Format: GeoJSON (RFC 7946): one point per cover, WGS84, coordinates in [lng, lat] order, with type, provider and confidence as properties. GIS tools (QGIS, ArcGIS) and web maps both read it, so one file serves both. For very large layers: GeoPackage.

In `BRAINSTORM.md` this answers the open question "How to convert lat/lng to GIS coordinates? What is the difference between lng/lat for a map overlay and a GIS format?" and the todo "Read more on GIS formats". I would mark both as checked, with the same short answer.

Apply?

Source: [RFC 7946](https://datatracker.ietf.org/doc/html/rfc7946)

## User

apply

## Assistant

I applied it to both files.

### "To verify" 5 of 7: open-vocabulary detectors (`WRITEUP.md` 2.2, "No labels" row)

Facts:
- Grounding DINO, OWLv2 and YOLO-World are correct names. moondream2 and Qwen-VL are VLMs that can return boxes, not detectors.
- Newer options: **YOLOE** (2025, AGPL) and **SAM 3** (Meta, Nov 2025, text prompt to masks, custom license).
- One street-scene study found YOLO-World weak on small objects, and distant covers are small.
- **The strongest finding:** COCO, Objects365 and Open Images have no manhole class, but **LVIS has "manhole" (class 667)**. So YOLOE or YOLO-World with an LVIS vocabulary may detect covers with no training.

Suggested text for the "No labels" row:
> Bootstrap: an open-vocabulary detector (Grounding DINO, OWLv2, YOLO-World, YOLOE; "manhole" is already an LVIS class, so the LVIS-trained ones may detect covers directly) proposes boxes; a VLM answers ... (rest unchanged)

Changes in `BRAINSTORM.md`:
- **Line 32**, "check if the pre-trained model already detects manhole covers as one of its default classes": add "Checked: not in COCO, Objects365 or Open Images; yes in LVIS (class 667)."
- **Line 281**, todo "Check the open-vocabulary detectors": mark as done, adding the YOLOE and SAM 3 names and the YOLO-World small-object weakness.

Should SAM 3 go into the write-up too? It gives masks, which give a more exact cover center, but its license is custom. My recommendation: keep it out of the write-up and only note it in the brainstorm.

Apply?

Sources:
- [Ultralytics LVIS config](https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/datasets/lvis.yaml)
- [Open-vocabulary models in unusual street scenes](https://arxiv.org/pdf/2408.11221)
- [Roboflow, SAM 3 vs YOLOE](https://playground.roboflow.com/models/compare/seg-preview-vs-yoloe)

## User

drop OWLv2, drop sam3

## Assistant

I applied it without OWLv2 and SAM 3. In `BRAINSTORM.md` I left your original lists as they were. The "done" note on the todo records the result: keep Grounding DINO and YOLO-World, add YOLOE, drop OWLv2.

### "To verify" 6 of 7: cut-out augmentation name (`WRITEUP.md` 2.3)

Facts:
- The method is **Cutout** (DeVries and Taylor 2017). A close variant is **Random Erasing** (Zhong et al. 2017).
- Ultralytics `erasing` works only for classification, not detection.
- For detection, Albumentations `CoarseDropout` does it.

Suggested text for `WRITEUP.md` 2.3:
> - Occlusion: Cutout / Random Erasing (cut out patches; cars and people cover manholes). Ultralytics `erasing` is for classification only, so for the detector use Albumentations `CoarseDropout`.

Changes in `BRAINSTORM.md`:
- **Line 500**: replace "(name of the method to find)" with "(Cutout / Random Erasing)".
- **Line 287**, todo "Find the name of the augmentation...": mark as done, with the same names.

Apply?

## User

yes

## Assistant

I applied it to both files.

### "To verify" 7 of 7: US manhole standards, and cleanup of section 7

**Facts:**
- There is no single national size standard. AASHTO M306 covers casting load, not size.
- Common cover diameters are 22 to 36 in (about 0.55 to 0.9 m). Each agency sets its own in its standard drawings.

**Suggested use in `WRITEUP.md` 1.3**, a new bullet after "Sanity check":
> - **Size check:** US covers are about 0.55 to 0.9 m across (22 to 36 in; no national standard, each agency sets its own). A detection whose box size, at its computed distance, is far outside this range is suspect: lower its confidence.

This also cross-checks the distance: if many real covers come out "too big", the distance or the camera height is wrong.

**Section 7 "To verify" cleanup.** Remove the resolved items: GIS format, Ultralytics license, open-vocabulary detectors, line fitting, US standards. What stays:
- Camera height and camera lat/lng accuracy (not published, see 1.3).
- Which image column `heading` maps to (center or left edge).
- Zero-shot classifiers (OpenCLIP, SigLIP 2): only the names are checked. How well they classify covers needs a test on real crops.

**Line 7.** No "(to verify)" marks are left in the text, so remove "Items marked *(to verify)* are not checked yet."

**`BRAINSTORM.md`:**
- Mark the standards idea and open question as checked, with the same facts.
- Lines 142, 148 and 647 still say "(to verify)" about the projection and strip assumptions. Replace them with "(checked: strips are 360° x 90°, horizon on the middle row)".
- I would leave the remaining "to check" items as they are. They need experiments, not web search: OCR on dirty covers, the rotation augmentation, and moondream2/Qwen as label generators.

Apply?

## User

yes

## Assistant

Rewrapping the long lines I introduced.

All 7 "to verify" items are done. There are no "(to verify)" marks left in either file, and the line "Items marked *(to verify)* are not checked yet" is removed.

Changes in this last step:
- **`WRITEUP.md` 1.3:** new **Size check** bullet. US covers are about 0.55 to 0.9 m across, and a detection far outside that range at its computed distance gets lower confidence.
- **`WRITEUP.md` section 7:** "To verify" now keeps only three items: camera height and lat/lng accuracy, which image column `heading` maps to, and a test of the zero-shot classifiers on real crops.
- **`BRAINSTORM.md`:** the standards idea and open question are marked as checked. The three projection lines now say "checked: strips are 360° x 90°, horizon on the middle row". I rewrapped the paragraphs I had edited to the file's line width.

Still open in `BRAINSTORM.md`, because they need experiments and not a web search: OCR on dirty covers, the rotation augmentation, and moondream2 or Qwen as label generators.

Nothing is committed yet: about 140 changed lines in both files. Should I commit to main and run `handover`? The next step in `NEXT_STEPS.md` is the visual review, then phase 3 (presentation).

## User

i think we're done, you can commit, i already did a visual review on the writeup file and it looks good, and i'll use it for the presentation.

## Assistant

Committed and pushed as `b2532d8`. Running `handover` now so `NEXT_STEPS.md` shows that fact checking is done.

I committed and pushed the fact-check changes as `b2532d8`. The handover agent is still updating `NEXT_STEPS.md` and the work log in the background. I'll report its docs commit when it finishes.

The handover is committed and pushed to main as `d4bad39` ("docs: handover - write-up final, phase 3 dropped").

- **This session:** fact checking of `WRITEUP.md` and `docs/BRAINSTORM.md` is finished and pushed as `b2532d8`.
- **Docs updated:**
  - `NEXT_STEPS.md` now says the project is effectively done.
  - `docs/WORKLOG.md` has a new entry for the fact checking and its decisions.
  - `docs/PLAN.md` marks phase 2 as done and phase 3 (presentation) as dropped.
- **Fixed in the docs:** they still listed fact checking and phase 3 as pending and described the strips as "about ±45°" without the check. They now give the checked 360° x 90° finding.
- **Uncommitted:** only `claude_logs/`, which stays out of git as before.

**Pick up here** (both optional):
1. Send the "For Exodigo" questions in `WRITEUP.md` section 7 before the interview.
2. If there is time, check which image column `heading` maps to on the 5 samples.

I'd suggest `/clear`, since this phase is finished.

Handover written, safe to `/clear` now.

## User

one more thing - does this repo has an explanation of how i work with claude, similar to the psistar repo?

## Assistant

Yes. This repo has the same setup as psistar:

- **`ai-chats/work-style/`** has the same four files as psistar. The README explains how you work with Claude, plus snapshots of your global `CLAUDE.md` (`house-rules.txt`), the `handover` skill and the `handover-writer` agent. The snapshots still match the current files in `~/.claude`. The README text differs from psistar's only in two dashes that were changed to fit the no-dash rule.
- **`ai-chats/README.md`** explains the session transcripts. It has the same length as psistar's, with small differences.
- The main `README.md` points to `ai-chats/`.

One gap: this session's transcript is not saved. `ai-chats/` ends at `03-pdf-review.md`, and the project `CLAUDE.md` asks to keep a curated file current each turn, which I did not do. Should I run `/save-chat` to create `04-fact-check.md` and commit it?

## User

yes, save the chat and commit, push
