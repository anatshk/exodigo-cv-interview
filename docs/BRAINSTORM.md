# Brainstorm

Anat's ideas, todos, and questions for the Exodigo manhole detection design task
(`Interview_Preparation.pdf`). Collected as given, one item at a time, without Claude's
input. Review against the PDF comes later.

## Task 1: Detect manholes in Google Street View panoramas

### Available data

- Panoramic images.
- One JSON per image with:
  - `lat` / `lng`: use for geospatial output.
  - `heading`: possibly also geospatial (the direction the camera faces?).
  - Image parameters: height and width in pixels, tilt, roll. Can be used to convert
    pixels to geospatial coordinates.
  - `date` (YYYY-MM, no hour resolution): for dataset setup.
  - `panoId`: for dataset setup.

### Detection process

Cover two cases: labels available, and no ground truth labels.

#### Case A: labels available

- Images with detection boxes (xywh). Train a detector model.
- Framework: Ultralytics YOLO (Anat has experience with it; should be easy to fine-tune).
  License issue: production use requires paying Ultralytics (to be checked).
- Before fine-tuning: check if the pre-trained model (natural images) already detects
  manhole covers as one of its default classes.
- Choosing what to label: active learning, pick samples by model uncertainty (see Points
  for consideration, point 3).
- Augmentations (see point 3 for details): distortion or undistortion artifacts,
  mirroring, rotation (check), lighting, obstructions (cut-out sections).
- Labeling requests should consider weather and lighting conditions.
  - Not real time, so we can select daylight photos only for convenience and do not need
    to detect manhole covers at night.
  - No hour-resolution timestamps, so no easy way to select by time of day.
  - Instead: track the image sequences ("ride") and sample throughout it, assuming this
    gives a distribution of times of day. (Assumes we have the full Street View database
    and need to select representative images.)
  - If the dataset is small: use everything, and exclude images if needed.

#### Case B: no ground truth labels

Three options:

1. Generate the gt labels ourselves, then resume the detector training of Case A.
2. Use a pretrained model plus some logic (expand on this later).
3. Skip model training and use classical methods for detection.
   - Pro: requires less data.
   - Con: may not generalize well enough and may miss different edge cases.

Classical method (brute force):

- Round covers: Hough transform on the lower half of the image.
  - Narrows the region of interest: fewer mistakes and shorter runtime.
  - Relies on the assumption that all Street View cameras are similarly calibrated. In
    the examples, a horizontal line at about the same place separates road and sidewalk
    from sky and buildings.
- Square / rectangular covers: classical edge detectors.
- Why shape and not color: covers can be metal, which reflects sunlight and changes
  color. Example: image `Kk0_Hzv4bQc2ha7esbEDcw`.
- Needs iterations and human error analysis to develop false positive exclusion logic.
- Needs iterations on the Hough / edge detection parameters: the panorama can distort
  shapes, so some tolerance is needed.

Reducing human involvement:

- Extract a box around each unlabeled candidate (include some background).
- Extract features from the object and from the background, in both RGB and grayscale.
- Cluster the candidates in feature space.
- Look at a few samples per cluster and at the outliers, to help define what is and is
  not a manhole cover.

Option 2 expanded (pretrained model plus logic):

- If a pretrained detector already detects manhole covers (no matter the given class
  label), use it either as is or with a layer of post-processing logic that excludes FPs
  for our task.
- Anat sees this as an intermediate step: use it for label extraction to train our own
  model, again because hard-coded logic is fragile.
- Open mind: perhaps, as an off-the-shelf solution, it is good enough for a given task.
- Open-vocabulary detectors (boxes from a text prompt) as candidates: Grounding DINO,
  OWLv2, YOLO-World, moondream2, Qwen-VL. To check.
- VLM to clean FPs (depending on cost), at least for a few iterations until we have
  enough labeled data:
  - Input: a crop of a detected object with a bit of background for context.
  - Prompt tailored to a simple question, "Is this a manhole cover?", answered yes / no /
    unsure.
  - Check this flow with different VLMs and prompts.
  - Cost is a concern.

Note on logic fragility: from Anat's experience, given enough data there are always edge
cases, and a threshold-based pipeline requires maintenance (example: classical RBC
classification at Scopio).

Combining with Case A:

- The classical logic is fragile. Use its first versions as a data extractor for the DL
  detector (option 1), with error analysis on train/val data to fix "gt" errors.

### Panorama input

- Detection output: boxes are enough at this point (no masks).
- Option: undistort the panorama before detection.
  - Assume the road and sidewalk can easily be cut as the lower half of the image.
  - Compare detection on undistorted vs still distorted lower halves.
  - May not be required: YOLO perspective and shear augmentations may be enough.
- Tiling: if the crop is too large, tile it instead of resizing too much. Save the
  source of each tile (image, coordinates in the image). Run the detector in batches,
  perhaps mixing tiles from several images for speed. The coordinate conversion then
  goes tile, image, real world.

### Conversion to geospatial coordinates

Anat has little experience here. Later: Claude to search and verify these ideas and
assumptions.

Inputs (assumed):

- Camera information: lens focal length, sensor pixel-to-mm factor, etc.
- Camera position (lat/lng, in high enough resolution?).
- Image size in pixels.
- Detection boxes of the manhole covers, from the detector.

Calculation idea:

- From these, calculate the distance and angle from the camera position to each
  detection box center. Take panorama distortions into account.
- Use the camera lat/lng plus distance and angle to calculate the lat/lng of the box
  center.

Assumptions from the sample metadata (to verify):

- The metadata says 13312 x 6656 (2:1), so the projection is likely equirectangular:
  each pixel maps directly to a horizontal and vertical angle. Focal length and sensor
  size may not be needed.
- But the sample files are 4:1 strips (about ±45° around the horizon). Take the vertical
  angle per pixel from the real image, not the metadata size (to verify).
- `tilt` is in degrees, and about 90 means the camera is level with the horizon.
- Distance to a cover comes from the camera height plus a flat-ground assumption.

Location improvement step (to consider):

- Triangulation from multiple images: one cover seen in several nearby panoramas can
  be located more exactly by combining the views, instead of relying on a single view
  and the flat-ground assumption.

Verification step (after we have the covers' lat/lng):

- Assumption: infrastructure travels in straight lines most of the time.
- Fit straight lines through the detected covers in a given small area (town limits?).
- Covers on a straight line with others get a higher score.
- The detector score (how sure the detector is) can also be included in this score.
- Line fitting method: maybe RANSAC, or a more modern alternative.

Duplicate removal (after the covers have real-world coordinates):

- One cover can appear in several nearby panoramas.
- Keep the higher-confidence detection.
- Assumption: covers can't overlap, and probably have a minimal distance between them.
  Any overlapping detection boxes are duplicates.
- Check edge cases, such as an overlap of a few pixels.
- Do it per region, not on all detections (avoid comparing parallel streets). Method:
  KD-tree, especially SciPy's cKDTree.
- Duplicates also occur over time: the same location has panoramas from different
  months and years, so the same cover appears in each of them.

Known objects database:

- Keep a database of known covers (location, type, confidence), per region to keep it
  small.
- New detections are matched against it, across panoramas and across years.
- A cover seen at the same place in several years gets a higher confidence. A cover seen
  only once may be a false positive, or it may have been removed or paved over.

### Dataset setup

- Use `date` to represent different seasons; make sure all seasons are represented.
- Use `lat` / `lng` to represent different geographical locations.
- Both are used to make the training data representative and to avoid leakage between
  train and val.
- Use `panoId` to make sure there is no leakage between splits.
- Separate dataset folds by street, neighborhood, or city.
- Check data balance.
- Ideally, create a test set from locations unseen in train/val (different states,
  cities, neighborhoods?).
- Consider another layer of data organization (derived from lat/lng) based on
  infrastructure similarity, geographical location, town size, etc.

### Output

- Arrange the output in a format the next step ingests: lng/lat for a map overlay, or
  GIS. The output module can also rearrange the data.
- Calculate a "final confidence" here, and use it to affect how detections are
  displayed on the final map (for example, a different color by score).
- The classifier labels are the utility types. The output module can use a dictionary of
  providers to convert a label to what users want to see (type only, or type plus
  provider).

### Validation

- Assume the system operates in the US only.
- Validate geospatial coordinates against that, both in the raw input data and in the
  final output.
- In the coordinate conversion module: a silent failure mode (does not stop the run)
  that alerts if a detection is placed outside the stated region. It can indicate a
  mistake in the calculation or in the raw data.
- Evaluation levels (see point 5): validation and test sets per model, unit tests per
  logic edge case, and a final comparison to real-world data (known infrastructure line
  and covers, or covers marked by walking a street), if available.
- Recall vs precision priority and threshold depend on whether covers are proxies for
  the line or the actual goal.
- Sensor-based utility estimations: if the goal of the system is not to add confidence
  to those measurements, they can be used as weak labels. If the goal is to add
  confidence to them, using them as labels is leakage.

### Challenges (see point 6)

- Data: panorama distortions, multiple cameras and configurations.
- Lack of final ground truth (the infrastructure line).
- Small coordinate and calculation errors that add up to significant differences.
- The straight line assumptions may be wrong and add confusion instead of clarity.

### Ideas

- There may be US or per-state standards for manhole size, shape, etc. that the system
  can use.

### Open questions (to check)

- Is `heading` a geospatial quantity (where the camera faces)?
- Are tilt and roll in degrees?
- Which US / state standards exist for manhole size and shape?
- Does the pre-trained YOLO model already have a manhole cover class (or a close one)?
- Can we assume Google Street View images are daylight only?
- What is considered leakage? Same street: yes. Neighborhood / town: perhaps.
- Does Google Street View provide camera details fields? (Anat remembers seeing them
  somewhere while using it in the past.)
- Is the camera lat/lng resolution high enough for the conversion?
- How to convert lat/lng to GIS coordinates? What is the difference between lng/lat for
  a map overlay and a GIS format?
- Which line fitting method: RANSAC, or a more modern alternative?
- Is real-world ground truth available (known infrastructure lines and their covers, or
  covers marked on site)?
- Is recall or precision more important? Are the covers proxies for the infrastructure
  line, or the actual goal?
- How correct is the assumption that infrastructure travels in straight lines? Are there
  standard bend / corner angles?
- What area should the line fitting use (town limits?). Are there other indicators that
  a line is broken (power station, pump, etc.)?
- Can we use grayscale images? One channel uses less memory than three for RGB. Perhaps
  grayscale is also easier for shape detection.

### Todos (depends on amount of data and time given)

- In-depth research into the available data (Street View database). Anat remembers that
  the same street can have images taken months or even years apart.
- Check if we have all the parameters for the pixel-to-lat/lng calculation. If something
  is missing, what would we need to find or calculate?
- Claude: search and verify the geospatial conversion ideas and assumptions.
- Check the Ultralytics YOLO license: using it in production requires paying
  Ultralytics.
- Check the cost of the VLM FP-cleaning flow, and test it with different VLMs and
  prompts.
- Check the open-vocabulary detectors: Grounding DINO, OWLv2, YOLO-World, moondream2,
  Qwen-VL.
- Find the name of the augmentation that cuts out a section of the image.
- Read more on GIS formats.

### Writeup notes

- Include one of the panoramas from `images/` in this section of the final writeup.
- Add a link to the Ultralytics YOLO framework.

## Task 2: Classify manhole covers by type

### Problem understanding

- Classes: from the given examples, the types are infrastructure types (sewer, water,
  communication). There may also be differences between providers.
- Data: a small set of representative examples per region. Not enough for model
  training.
- Problem type: unsupervised / semi-supervised classification. Few labeled examples per
  region, an open label set, and "unknown" is a valid output.
- Input images: crops of the manhole covers with a bit of background, like the provided
  examples.
- In the full system: the classifier gets only the detection crops (undistorted) and
  returns a label per crop, added as a column to the detection list.
- Evaluation: one confusion matrix for the detector plus classifier pipeline, showing
  both detection and classification mistakes (see point 5).

### Deterministic approach

Feature extraction:

- Shape: edge detector / Hough transform.
- Text: OCR. Need to check how well it works on dirty or eroded covers.
- Texture: classical texture filters (family to find later).
- Size: actual size, if the pixel-to-mm ratio is known.
- Color: a general color (black / gray / brown), not an exact RGB value.

Feature vector:

- Shape: one-hot (circle / square / rectangle).
- Size: diameter, or max side.
- Color: start with an RGB value, change to one-hot if needed.
- Keywords: a vector of keywords (water / hot / sewer / storm). Build the dictionary and
  expand it on real data.

Clustering and labeling:

- Check PCA first, to see if some signals are more relevant than others.
- Cluster the images in the feature space.
- See where the provided examples land, and whether they can label each cluster.
  - Label clusters by distance to the provided examples, such as kNN.
- Outliers: use the outlier detection method from the Similarweb take-home task to find
  samples that are not in any cluster. Mark them for visual analysis (human or VLM).
  This is also the "unknown" option for this route.
- Label each cluster from representative examples, by a human or a VLM.
- VLM prompt draft: "Describe the manhole cover in the image. What is its shape and
  color? Does it have any text on it? Which of the provided infrastructure types would
  you assign it and why?"
  - The prompt can be engineered further, for example split into yes / no / unsure
    questions to limit hallucinations.

Alternative feature extraction (image encoder):

- Run the crops through an image encoder (for example ResNet without the classification
  layer) and use the output vector for clustering.
  - Any other encoder can be used, and compared if there is time. ResNet is ok for the
    scope of this task.
- Easier way to capture shape, color, and texture.
- Run OCR as a parallel step.
- Then continue from the cluster labeling step above.

### Non-deterministic approach

Use VLMs and/or a tool like JEV for classification.

VLM description route:

- Ask a VLM to describe each image, with a prompt similar to the one in the cluster
  labeling step above.
- Request structured answers, so they can be encoded into feature vectors and clustered
  as above.
- Add an "unknown" option to each feature, to escalate to humans.
- The feature vector encodings may change over a few iterations (adding keywords,
  colors, shapes, etc.).
- Possibly use a "word2vec"-like embedding space, so that gray squares sit together, far
  from black circles. Anat is not sure about this.

JEV:

- A tool for making decisions. Open source versions exist.

Cost and latency note:

- Any method that uses LLMs / VLMs has a significant cost and latency.
- So use them only to gather enough data to train a model, or limit them to unexpected
  edge cases that need a non-deterministic approach the standard DL models can't
  provide.

### Challenges (see point 6)

- Dirty or eroded covers affect image quality.
- "Anonymous" covers that can't be classified.
- In a given region, covers for different infrastructure types can look the same.
- Some providers can be significantly underrepresented.

### Single model option

- If there is enough data: train another YOLO detector (Task 1) with the cover type
  labels, instead of a separate classifier. Depends on data availability and labeling
  cost (see point 3, Scopio example).

### Classifier scope

- One classifier for all regions, or several small classifiers, one per region.
- So either one detector plus a classifier selected by area, or multiple YOLO models
  (detector plus classifier) selected by region.
- TBD after understanding the data and requirements.

### Open questions (to check)

- Are the classes infrastructure types only, or also providers?
- Which model to use for zero-shot classification?
- How well does OCR work on dirty or eroded covers?
- Which family of classical texture filters to use?
- Is the pixel-to-mm ratio known for the crops?
- Is a "word2vec"-like embedding space useful for the VLM structured answers?
- Can JEV (or a similar tool) be used here? Does it support an "unknown" option for
  images outside the provided examples? Does it work on images, or do we need to convert
  them to text first?

### Todos

- Find the family of classical texture filters.
- Check zero-shot classification models: OpenCLIP, SigLIP 2, alone and combined with
  the provided examples as image prototypes.
- Build the keyword dictionary, expand it on real data.
- Read about JEV (or similar tools): fit for this task, "unknown" support, image or text
  input.

## Points for consideration

### 1. How would you define detection and classification problems in this context?

- Covered by the problem definitions in the Task 1 and Task 2 sections above. No
  additional notes.

### 2. What data would you use, and how would you prepare it for this task?

- Covered in detail in Task 1, and less in Task 2.
- Main data preparation challenge: the geospatial conversion (Task 1, "Conversion to
  geospatial coordinates").
  - Calculate the position of panorama pixels relative to the camera, taking into
    account camera parameters, panorama distortions, and the pixel-to-mm conversion.
  - Use the JSON lat/lng as the camera location, and calculate the lat/lng of each
    detected manhole cover.
  - Open questions remain: what inputs are needed, and how to convert lat/lng to GIS
    coordinates.
- In-depth data understanding is needed to prevent leakage (Task 1, "Dataset setup").

### 3. What type of models or learning paradigms would you consider, and why?

- Several options and their trade-offs are detailed in Task 1 and Task 2.
- At the end: suggest a single pipeline chosen from all the brainstorm options and
  trade-offs.

Gaps found by Claude, to address one at a time:

- Task 1, other detectors and open-vocabulary detection:
  - YOLO is a quick option. Open to other detectors because of licensing, performance,
    or other limitations.
  - Transformers are not required here. They are costly to train. Their benefit is that
    they "see" the entire image, while CNNs are more local. There is an underground
    connection between manhole covers, but it is not enough to justify a costly
    transformer.
  - Possible check: is a pretrained transformer better than a pretrained or fine-tuned
    CNN? Do not re-train the transformer.
  - Open question: is moondream2, or one of the Qwen models, useful for open-vocabulary
    detection here? Claude's first answer: yes, both return boxes from a text prompt,
    but they are slower and more costly than a CNN detector, likely need tiling, and can
    hallucinate boxes. Best as a label generator for Case B. To check (see Todos).
- Task 1, boxes or masks: masks give a more exact center and shape for the geospatial
  conversion.
  - Boxes are enough at this point.
- Task 1, panorama input: full panorama, or undistorted tiles cut from it.
  - Assume the road and sidewalk can easily be cut as the lower half of the image.
  - Compare detection on the undistorted lower halves with detection on the still
    distorted lower halves.
  - The YOLO framework has perspective and shear augmentations, so the undistortion step
    may not be required. Still, it is good to know it is an option.
- Task 1, active learning: pick the samples to label by model uncertainty.
  - Not mentioned before, but a good way to decide what to label. Likely to come up from
    a leading question such as "how would you select what to label?".
- Task 1, duplicates across panoramas: one cover can appear in several nearby
  panoramas. How to merge these detections.
  - An important stage (also in Anat's cell detector project on tiled data).
  - Do it after the covers are detected and assigned real-world coordinates.
  - Keep the higher-confidence detection.
  - Assumption: manhole covers can't overlap, and probably have a minimal distance
    between them. Any overlapping detection boxes are duplicates.
  - Check edge cases, such as an overlap of a few pixels.
- Task 1, augmentation.
  - Distorted panoramas: simulate different locations in the camera FOV (different
    distortion).
  - Undistorted images: simulate the undistortion artifacts.
  - Mirroring is ok.
  - Rotation needs checking: don't create images that do not look like the real world.
  - Lighting is required: brightness, or any combination that gives different weather
    and time-of-day appearance.
  - Obstructions: covers can be blocked by cars or pedestrians. Train with a section of
    the image cut out (name of the method to find).
- Task 2, few-shot paradigms: classify directly by distance to the provided examples in
  embedding space (nearest neighbor, prototypes).
  - Implied in the clustering route: the provided examples label the clusters based on
    distance, such as kNN.
  - Use the outlier detection method from Anat's Similarweb take-home task to find
    samples that are not in any cluster, and mark them for visual analysis (human or
    VLM).
- Task 2, zero-shot classification: an image-text model compares the crop with text
  labels.
  - Not mentioned before. Open question: which model to use?
- Task 2, "unknown" outside the VLM route: how the clustering or encoder route rejects
  covers that match none of the provided examples.
  - The outlier approach above covers this.
- Task 2, encoder choice: compare other pretrained encoders with ResNet.
  - ResNet is an example. Any other encoder can be used, and compared if there is time.
    For the scope of this task, ResNet is ok.
- Both tasks, one model or two: a single detector with one class per cover type, or a
  separate detector and classifier.
  - Yes, if there is enough data: train another YOLO detector with the specific cover
    type labels. This saves the additional classification model.
  - Depends on data availability. Example from the Scopio cell detector: the first idea
    was a detector with about 60 labels, but some labels were very rare and labeling was
    very costly (hundreds of normal cells to get one anomalous cell in the detection
    ROI).
  - Labeling cost in this detection task is lower, so this is definitely an option.

### 4. What are the main components of the system, and how do they interact?

The final system, in order:

1. Image preprocessing (small module): crop ROIs, optionally undistort.
   - Input: a path to the image (the module also loads the image), and the
     undistortion parameters (if required).
   - If the crop is too large, tile it after cropping: we don't want to resize the
     input too much.
   - Save the source of each tile (image, coordinates in the image).
   - Output: an image, or a batch of images, for the detector.
2. Detector.
   - If tiling: work in batches until all tiles are processed. Perhaps mix tiles from
     several images to optimize speed.
   - Output: a collection of detections per image in the batch (local tile coordinates
     per image).
3. Coordinate conversion of the detected objects, given all the parameters listed in
   Task 1.
   - Input: all the detections, and the tile-to-image relationships.
   - With tiling: tile coordinates, then image coordinates, then real-world
     coordinates. Without tiling: only the last two steps.
   - Output: a list of real-world coordinates of the detection boxes, with the detector
     confidence.
   - Verification: the system is assumed to operate in the US. A silent failure mode
     (does not stop the run) alerts if the calculation places a detection outside the
     stated region. This can indicate a mistake in the calculation or in the raw data,
     to be addressed.
4. Deduplication based on real-world coordinates.
   - Optimize by doing it per region rather than on all detections (for example, avoid
     comparing parallel streets).
   - KD-tree is a good method, especially SciPy's cKDTree.
   - Output: the same list of coordinates and confidence, deduplicated.
5. "Straight line checker": combines the detection score with a score for how well each
   detection aligns with other detections. Maybe RANSAC, or a more modern alternative.
   - Output: the same list, with an additional score column.
6. Classifier. Can later be merged with the detector into one detector plus classifier
   model, like YOLO.
   - Input: only the detection crops (undistorted).
   - Output: a label per crop, added as a column to the detection list.
7. Output formatting: arranges the output in a format the next step ingests, for
   example lng/lat for a map overlay, or GIS (read more on GIS to understand the
   difference). This module can also rearrange the data.
   - Input: the detection list, with scores and labels.
   - Calculate a "final confidence" here, and use it to affect how detections are
     displayed on the final map, for example a different color by score.

### 5. How would you measure whether the system is successful?

Several levels:

- Validation and test sets for each component model.
- Unit tests for any logic, adding a test per edge case encountered.
- Final test (if at all possible): comparison to known real-world data.
  - Ground truth of an infrastructure line and its manhole covers, or
  - Walk a specific street, mark the exact coordinates of the manhole covers, and
    compare to that.
  - Not sure this data is available at all.

Individual model evaluation:

- Find out whether recall or precision is more important, then which threshold is
  relevant for the task.
- If the covers are only proxies for the actual infrastructure line, missing one or two
  is ok, as long as the final line is located correctly. If the covers are the actual
  goal, the threshold rises.
- The detector plus classifier pipeline can be measured with one confusion matrix that
  shows both detection and classification mistakes.

### 6. What are the main challenges or failure modes you anticipate?

Detection and geospatial output (Task 1):

- Data: distortions from panorama mode, multiple cameras and configurations, etc.
- Lack of final ground truth (the infrastructure line).
- Small mistakes or inaccuracies in coordinates and calculations that add up to
  significant differences.
- The "straight line" module is a question mark: its inherent assumptions may be wrong,
  so it can add confusion instead of clarity.

Classification (Task 2):

- Covers can be dirty or eroded, which affects image quality.
- Covers can be "anonymous", so we can't classify them.
- In a given region, covers for different infrastructure types can look the same.
- Some providers can be significantly underrepresented.

Classifier scope, TBD after understanding the data and requirements:

- One classifier for all regions, or several small classifiers, one per region.
- So either one detector plus a classifier selected by area, or multiple YOLO models
  (detector plus classifier) selected by region.

## Parameter tuning

Parameter tuning is done per module. It is not in the current scope.

- Detector confidence threshold: YOLO allows tuning the detection and classification
  thresholds, which controls the FP / FN balance. A class that is more sensitive to FPs
  can get a higher threshold (Anat did this in a past project).
- NMS IoU: keep the default unless a problem shows up. The objects are far enough apart.
- Tile size and input resolution: depend on the data. Decide after the first iteration.
- Duplicate removal radius and straight line tolerance: can depend on building
  standards. Leave for now.
- Outlier threshold (Task 2): start with defaults, change after the first iteration.

## Assumptions

- The system operates in the US only (Task 1).
- Not real time: daylight photos only, no night detection needed (Task 1).
- We have access to the full Street View database and select representative images from
  it (Task 1).
- All Street View cameras are similarly calibrated, so a horizontal line at about the
  same place separates road and sidewalk from sky and buildings (Task 1).
- Camera information is available (focal length, sensor pixel-to-mm factor, etc.), and
  the camera position is known (Task 1).
- The panoramas are equirectangular (metadata says 2:1), so each pixel maps to an angle;
  the sample files are 4:1 strips (about ±45° around the horizon), so the vertical angle
  per pixel comes from the real image; `tilt` is in degrees, with about 90 level with the
  horizon; distance comes from the camera height plus a flat ground (Task 1, to verify).
- Infrastructure travels in straight lines most of the time (Task 1).
- The road and sidewalk can easily be cut as the lower half of the panorama (Task 1).
- Manhole covers can't overlap, and probably have a minimal distance between them
  (Task 1).
- Task 2 input images are crops of the manhole covers with a bit of background, like the
  provided examples (Task 2).
- The labeled examples per region are too few for model training (Task 2).
