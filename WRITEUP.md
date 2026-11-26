# Manhole detection and classification from Street View

**Goal:** add confidence to underground utility estimations. Detect manhole covers in
Google Street View panoramas, classify them by type, and output them as a geospatial
layer that can be compared with sensor-based estimations (US only).

Items marked *(to verify)* are not checked yet.

**Contents**

1. [The final system](#1-the-final-system)
2. [Building the models: labeling and training](#2-building-the-models-labeling-and-training)
3. [Parameter selection](#3-parameter-selection)
4. [Evaluation](#4-evaluation)
5. [Challenges and failure modes](#5-challenges-and-failure-modes)
6. [Assumptions](#6-assumptions)
7. [Open questions](#7-open-questions)

## 1. The final system

![System pipeline](docs/figures/system_pipeline.svg)

| # | Module | Input | Output |
|---|---|---|---|
| 1 | Preprocessing | Image path, undistortion parameters (optional) | Road ROI tiles, each with its source (image, position) |
| 2 | Detector | Batches of tiles (mixed across images for speed) | Boxes + confidence, in tile coordinates |
| 3 | Pixel to lat/lng | Detections, tile-to-image map, metadata | Lat/lng per detection + confidence |
| 4 | Deduplication | Lat/lng list, known objects database | Same list, one entry per physical cover |
| 5 | Confidence reviewer | Deduplicated list, known objects database | Same list + line and years-seen scores |
| 6 | Classifier | Undistorted crop per detection | Same list + type label (or "unknown") |
| 7 | Output | Full list | GIS layer / map overlay, final confidence |

### 1.1 Preprocessing

The road is below the horizon, so we keep only that part of the image. This gives fewer
false positives and a shorter runtime. If the ROI is too large for the detector, we tile it
instead of resizing, so that small, distant covers are not lost.

![Road ROI on a sample panorama](docs/figures/panorama_roi.jpg)
*Sample panorama, Detroit 2025. Red boxes: covers marked by hand for illustration.*

Undistortion of the ROI is optional. Compare detection on distorted and undistorted ROIs;
YOLO perspective and shear augmentations may make it unnecessary.

### 1.2 Detector

One class: manhole cover. Ultralytics YOLO fine-tuned on our labels: fast, easy to
fine-tune, and familiar. License for production use *(to verify)*.

### 1.3 Pixel to lat/lng

![Pixel to ground geometry](docs/figures/pixel_to_ground.svg)

- The panorama is equirectangular *(to verify)*, so each pixel maps directly to an angle.
  Caution: the metadata says 13312 x 6656 (2:1), but the sample files are 4:1 strips
  (about ±45° around the horizon). The vertical angle per pixel must come from the real
  image, not the metadata size, or every distance is wrong.
- Vertical angle below the horizon + camera height + flat ground → distance `d`.
- Horizontal angle + `heading` → bearing.
- Camera lat/lng moved `d` meters along the bearing → cover lat/lng.
- **Sanity check:** a silent alert (the run continues) when a cover lands outside the US.
  It points to a bug in the calculation or bad raw data.
- **Improvement step:** triangulation. A cover seen in several nearby panoramas can be
  located more exactly by combining the views, instead of one view plus a flat-ground
  assumption.

### 1.4 Deduplication and known objects database

The same cover appears in nearby panoramas and in panoramas of the same place from
different years.

![Same location over the years](docs/figures/same_location_over_years.jpg)
*All five samples are the same intersection, 2007 to 2025: different cameras, headings,
seasons, and the road was repaved by 2020.*

- Covers can't overlap and have a minimum distance between them, so detections closer
  than a radius are one cover. Keep the highest confidence one.
- Search per region with a KD-tree (SciPy `cKDTree`), so parallel streets are never
  compared.
- A **known objects database** (per region, to stay small) stores each cover with its
  location, type and confidence. New detections are matched against it.
- A cover seen in several years gets a higher confidence. A cover seen once may be a
  false positive, or it was removed or paved over.

### 1.5 Confidence reviewer

Adds two confidence scores to each cover:

- **Straight lines:** utility lines mostly run straight. Fit lines through the covers of
  a small area (RANSAC or a newer method *(to verify)*). A cover on a line with others
  gets a higher score. This is the weakest assumption in the system: it may add noise
  instead of clarity.
- **Years seen:** from the known objects database. A cover seen at the same place in
  several years gets a higher score.

### 1.6 Classifier

![Cover type examples](docs/figures/cover_examples.jpg)
*Examples given for one region. They show local conventions, not a fixed label set.*

- **Problem type:** semi-supervised, open-set classification. A few labeled examples
  per region, the label set may grow, and "unknown" is a valid output.
- **Method:**
  1. Embed each crop with a pretrained image encoder (for example ResNet without its
     last layer). Run OCR in parallel: text such as "WATER" or "SEWER" is a strong
     signal.
  2. Assign the label of the nearest given examples (kNN or class prototypes).
  3. Crops far from all examples and clusters are outliers: label "unknown" and send to
     review.
- Regions: one classifier for all regions, or one per region. Decide after seeing the
  data.

### 1.7 Output

- Format: a GIS layer or map overlay *(format to verify)*.
- A final confidence per cover (detector, years seen, line score, classifier), shown on
  the map, for example as color.
- A provider dictionary converts the label to what users want to see: type only, or type
  plus provider.

### 1.8 Active learning loop

```mermaid
flowchart LR
    C[Detector:<br/>low confidence] -.-> L[Labeling queue<br/>human or VLM]
    G[Classifier:<br/>unknown] -.-> L
    L -.-> R[Retrain detector<br/>and classifier]
```

The only training part inside the running system. Low confidence detections and
"unknown" covers go to a labeling queue (human or VLM). New labels retrain the detector
and the classifier.

## 2. Building the models: labeling and training

### 2.1 Dataset setup

- **Splits by location** (street, neighborhood or city), never by image: the same place
  appears in many panoramas and years. Same `panoId` never in two splits.
- **Test set** from places not seen in train or validation (other cities or states).
- **Balance** seasons (`date`) and locations (`lat`/`lng`).
- **Daylight only:** not a real-time system, so night images are not needed. `date` has
  no time of day, so sample along each capture sequence to cover different hours.

### 2.2 Detector labels

| Case | Approach |
|---|---|
| Labels exist | Train directly. Choose what to label next by model uncertainty (active learning). |
| No labels | Bootstrap: an open-vocabulary detector (Grounding DINO, OWLv2, YOLO-World *(to verify)*) proposes boxes; a VLM answers "Is this a manhole cover? yes / no / unsure" on each crop; humans check samples per cluster and outliers. Then train our own detector. |

Why not keep the bootstrap as the final system: open-vocabulary detectors and VLMs are
slow and costly per image, and hand-written filter logic breaks on edge cases as the data
grows. Classical shape detection (Hough circles, edge detection) is a fallback, not the
main path.

### 2.3 Augmentations

- Distortion: covers at different positions in the panorama look different.
- Mirroring: yes. Rotation: only small, so images still look real.
- Lighting: brightness and color, for weather and time of day.
- Occlusion: cut out patches (cars and people cover manholes) *(method name to verify)*.

### 2.4 Classifier labels

- Cluster the crop embeddings, see where the given examples land, label each cluster
  from a few samples (human or VLM).
- Later, with enough labels: one YOLO model with a class per cover type, which replaces
  the separate classifier.

## 3. Parameter selection

Done per module, after the first iteration on real data. Not in the current scope.

- **Detector confidence threshold:** sets the FP / FN balance. A class that is more
  sensitive to FPs can get a higher threshold.
- **NMS IoU:** default, unless a problem shows up. Covers are far apart.
- **Tile size and input resolution:** depend on the data.
- **Deduplication radius, line tolerance:** may follow construction standards.
- **Outlier threshold:** start with defaults.

## 4. Evaluation

| Level | What |
|---|---|
| Models | Validation and test sets per model. One confusion matrix for detector + classifier, with "missed" and "false detection" rows next to the type confusions. |
| Logic | Unit tests, one per edge case found. |
| System | Compare with real-world truth, if available: a known utility line and its covers, or covers mapped by walking a street. |

Recall or precision first? If covers are a proxy for the utility line, missing a few is
fine as long as the line is right. If covers are the goal, recall matters more.

Sensor estimations can be weak labels only if the system is not meant to add confidence
to them. Otherwise using them is leakage.

## 5. Challenges and failure modes

**Detection and location**

- Panorama distortion; different cameras and setups across years.
- No ground truth for the final goal (the utility line).
- Small angle or height errors grow into meters on the ground, more with distance.
- The straight line assumption may be wrong.

**Classification**

- Dirty, worn or partly covered covers.
- Covers with no visible marking.
- Different utility types with similar covers in the same region.
- Rare providers with very few examples.

## 6. Assumptions

| Assumption | Reason |
|---|---|
| US only | Stated in the task. |
| Daylight images are enough | Not real time; we choose which images to use. |
| The road is below the horizon line, at about the same height in all panoramas | Seen in the samples. |
| Panoramas are equirectangular; `tilt` is in degrees, about 90 = level | Metadata is 2:1 (13312 x 6656) and tilt values are near 90 *(to verify)*. |
| The sample PNGs are a 4:1 strip of the full panorama | Sample files are 4096 x 1024 or 3328 x 832, while metadata says 2:1 *(to verify)*. |
| Camera height is known, ground near the camera is flat | Needed for distance from one view. |
| Utility lines mostly run straight | Basis of the line checker. |
| Covers don't overlap and have a minimum spacing | Basis of deduplication. |
| Too few labeled cover examples per region to train a classifier | Stated in the task. |

## 7. Open questions

**For Exodigo**

- Are the covers the goal, or a proxy for the utility line? This sets recall vs
  precision.
- Is any real-world ground truth available?
- Are the classes utility types only, or also providers?
- Will this system be used to confirm the sensor estimations?
- The sample files are 4:1 strips, while the metadata says 2:1. Which vertical field of
  view do the API images cover, and can we get the full panorama?

**To verify (fact finding)**

- Street View projection, camera height, and the meaning of `heading` / `tilt` / `roll`.
- Is the camera lat/lng accurate enough?
- US manhole size and shape standards.
- GIS output format.
- Ultralytics license; open-vocabulary detectors; zero-shot classifiers (OpenCLIP,
  SigLIP 2).
- Line fitting method.
