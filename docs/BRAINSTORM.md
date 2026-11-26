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
  detection box center.
- Use the camera lat/lng plus distance and angle to calculate the lat/lng of the box
  center.

Verification step (after we have the covers' lat/lng):

- Assumption: infrastructure travels in straight lines most of the time.
- Fit straight lines through the detected covers in a given small area (town limits?).
- Covers on a straight line with others get a higher score.
- The detector score (how sure the detector is) can also be included in this score.

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

### Validation

- Assume the system operates in the US only.
- Validate geospatial coordinates against that, both in the raw input data and in the
  final output.

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

### Writeup notes

- Include one of the panoramas from `images/` in this section of the final writeup.
- Add a link to the Ultralytics YOLO framework.

## Task 2: Classify manhole covers by type

### Problem understanding

- Classes: from the given examples, the types are infrastructure types (sewer, water,
  communication). There may also be differences between providers.
- Data: a small set of representative examples per region. Not enough for model
  training.
- Input images: crops of the manhole covers with a bit of background, like the provided
  examples.

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
- Label each cluster from representative examples, by a human or a VLM.
- VLM prompt draft: "Describe the manhole cover in the image. What is its shape and
  color? Does it have any text on it? Which of the provided infrastructure types would
  you assign it and why?"
  - The prompt can be engineered further, for example split into yes / no / unsure
    questions to limit hallucinations.

Alternative feature extraction (image encoder):

- Run the crops through an image encoder (for example ResNet without the classification
  layer) and use the output vector for clustering.
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

### Open questions (to check)

- Are the classes infrastructure types only, or also providers?
- How well does OCR work on dirty or eroded covers?
- Which family of classical texture filters to use?
- Is the pixel-to-mm ratio known for the crops?
- Is a "word2vec"-like embedding space useful for the VLM structured answers?
- Can JEV (or a similar tool) be used here? Does it support an "unknown" option for
  images outside the provided examples? Does it work on images, or do we need to convert
  them to text first?

### Todos

- Find the family of classical texture filters.
- Build the keyword dictionary, expand it on real data.
- Read about JEV (or similar tools): fit for this task, "unknown" support, image or text
  input.

## Todos

## Open questions

## Assumptions

- The system operates in the US only (Task 1).
- Not real time: daylight photos only, no night detection needed (Task 1).
- We have access to the full Street View database and select representative images from
  it (Task 1).
- All Street View cameras are similarly calibrated, so a horizontal line at about the
  same place separates road and sidewalk from sky and buildings (Task 1).
- Camera information is available (focal length, sensor pixel-to-mm factor, etc.), and
  the camera position is known (Task 1).
- Infrastructure travels in straight lines most of the time (Task 1).
- Task 2 input images are crops of the manhole covers with a bit of background, like the
  provided examples (Task 2).
- The labeled examples per region are too few for model training (Task 2).
