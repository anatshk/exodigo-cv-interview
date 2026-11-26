# 02 - Brainstorm

## User

i want to start workon on the task defined in @Interview_Preparation.pdf . at this point, I want to start brainstorming without input from you, your role is to list my ideas, todos, etc. later on i'll ask you to make sure i addressed all the questions and tasks in the pdf, and help me in fact finding and preparation on visual aids for the interview. are you ready to collect my input (one at a time, until i say we're done) into a tracked md brainstorming file?

## Assistant

Ready. I created `docs/BRAINSTORM.md` with four sections: Ideas, Todos, Open questions, Assumptions. I will file each item as you give it, in your words, with no comments from me. If an item does not fit a section, I will add a new section. Not committed yet; I will commit when you ask.

Go ahead with the first item.

## User

task 1 - detect manholes in google streetview panoramas. available data is: panoramic images (in the final writeup, include one of the images from the images/ folder here) and json details per image - lat/lng (note: use for geospatial, check if heading is also a geospatial coordinate - where the camera faces?), image parameters (height and width in pixels, tilt and roll - check if in degrees. these can be used for conversion of pixels to geospatial coords). there are also date and panoId fields - to be used for dataset setup (date - make sure all seasons are represented, panoId to make sure no leakage, also use the lat/lng for that - separate dataset folds by street / neighborhood / city to avoid leakage). we may assume the system operates in the US only - use validation on geospatial coordinates, both in the raw data and the final output. perhaps there are also certain standards in the US / per state for object size / shape / etc we can use, note this. arrange and write up this infodump and wait for the following.

## Assistant

I added a "Task 1: Detect manholes in Google Street View panoramas" section to `docs/BRAINSTORM.md`. It has these subsections: Available data, Dataset setup, Validation, Ideas (US and state standards), Open questions (heading, tilt and roll units, standards), and Writeup notes (include a panorama from `images/`). I also put the US-only assumption in the global Assumptions list.

Ready for the next item.

## User

we're still on task 1, now i want to define the detection process. i want to make sure i address both a case where labeling is available and a case where there is no gt labeling. the labeled case is straightforward, we'll have images with detection boxes (xywh), we can train a detector model. I have experience with the Ultralytics YOLO framework (writeup: add link here) that should be pretty easy to fine-tune. however, before fine-tuning i would check if the pre-trained model (on natural images) already detects the manhole covers as one of its default classes. the data labeling requests here should take into consideration weather and lighting conditions (assumption: not running in real time so we can assume we can select daylight photos only for convenience and do not need to detect manhole covers at night - can we asssume google street view are daylight only?). we don't have hour-resolution timestamps, so no easy way to select based on time of day, but given we can track the image sequences (assuming we have the full street view database and we need to select representative images, if the dataset is small we can just use everything and exclude images if needed), we could sample throughout the "ride" and assume distribution of times of day (note: i'm thinkning that more research into the street view database is needed as i remember same street can have images taken months and even years apart, so mark "in-depth research into available data" as something i'd do depending on amount of data and time given to complete the task). time-of-day aside, we can use the date field in the json (YYYY-MM) to represent different seasons and the lon/lat to represent geographical locations, both to make sure the training data is representative and that there is not leakage between train / val. note that data balance needs to be checked, and ideally, a test set created as well, containing data from locations unseen in train/val (different states / cities / neighborhoods?). to check: what is considered leakage? same street - yes, neighborhood / town - perhaps, consider another layer of data organization (from lon/lat) based on infrastructure similarity/geographical lication/town size/etc. this section started with how to label and drifted into overall data considerations. next i'll discuss the unlabeled scenario.

## Assistant

I updated Task 1 in `docs/BRAINSTORM.md`. The new "Detection process" subsection has Case A (labels available), and Case B (no labels) is a placeholder for your next item. I moved the data points you raised into "Dataset setup". I also added a Task 1 todo (in-depth research into the Street View data), four open questions, the YOLO link as a writeup note, and two assumptions (daylight only, full database access).

Ready for the unlabeled case.

## User

in the unlabeled case, we need to either generate the gt labels ourselves and then resume the detector training above, use a pretrained model + some logic (note: expand on this later), or skip the model training and use classical methods for detection. the classical methods require less data, but they may not generalize well enough and miss different edge cases. let's start with a brute-force method - for round manhole covers, we can use a hough transform on the lower half of the image (assumption: all streetview images/cameras are similarly calibrated - in the examples provided it seems that we can separate the road/sidewalk from the sky/buildings by a horizontal line in about the same place) - this narrows the region of interest - less mistakes and shorter runtime. square/rectangular manhole covers can be found using classical edge detectors. why shape and not color - the covers can be metal which reflects sunlight and changes color, example in image Kk0_Hzv4bQc2ha7esbEDcw. note: can we use grayscale images? one channel is less memory than 3 for rgb, also perhaps grayscale is easier for shape detection? the classical method will require some iterations and human error analysis to develop FP exclusion logic, also iterations on the hough/edge detection parameters as the panorama can distort shapes, so some tolerance is needed. to reduce human involvement we can compare the unlabeled candidates - extract a box around them (to include some background) and then extract features from the object and the background, both in rgb and grayscale, and cluster them in the feature space. look at a few samples per cluster and the outliers to see if this helps in defining what is/isn't a manhole cover. the logic here is fragile so perhaps we can use the first versions on the classical detector as data extractor for the DL detector - with error analysis on train/val data to fix "gt" errors.

## Assistant

I filled in Case B in `docs/BRAINSTORM.md`. It has the three options, the classical brute-force method (Hough for round covers, edge detectors for rectangular ones, why shape and not color, the iterations needed), the clustering step to reduce human work, and the link back to Case A. I also added the grayscale question, a todo to expand option 2, and the camera calibration assumption.

Ready for the next item.

## User

a bit of expansion on the "pretrained + logic" route - if we see a pretrained detector already detects manhole covers (no matter the given class label), we can use it either as is or with a layer of post-processing logic that excludes FPs for our task. this is an intermediate step in my opinion, to be used for label extraction to train our own model, again due to the fragility of any hard-coded logic. but i keep an open mind - perhaps as an off-the-shelf solution it is good enough for a given task. add a note: logic fragility - from my experience, given enough data, there are always edge cases and trying to fit a threshold based pipeline requires maintenance (note: classical rbc classification at scopio). add note: depending on cost, perhaps use a vlm to clean FPs, at least for a few iterations until we have enough labeled data. the prompt can be tailired to give yes/no/unsure on a simple question "is this a manhole cover?" on a crop of a detected object with a bit of background for context. this flow will need to be checked with different vlms and prompts. again mentioning cost. note about the YOLO detector - lisence issues. need to pay ultralytics if using this in production - another issue to be checked.

## Assistant

I added "Option 2 expanded" under Case B in `docs/BRAINSTORM.md`: the pretrained detector used as is or with FP post-processing, your view of it as an intermediate step for label extraction, the VLM FP-cleaning flow, and the note on logic fragility (Scopio RBC example). The YOLO license note is now next to the framework in Case A. The "expand option 2" todo is replaced by two todos: check the YOLO license, and check the VLM flow cost with different VLMs and prompts.

Ready for the next item.

## User

now i want to discuss conversion to geospatial coordinates. i don;t have much experience with this, so later on i'll ask you to do a search and to verify my ideas and assumptions. lets assume we have information about the camera taking the panoramic image, such as lens focus, sensor pix-to-mm factor, etc (note: check this in info of google streetview, i think i saw camera details fields somewhere while using it in the past), lets also assume we have the position of the camera (lon/lat in high enough resolution?), given the image size in pixels, the detection boxes of the manhole covers from the detector, we can probably calculate the distance and angle from the camera position to the detection box centers and use the camera position lon/lat to calculate the detection box center lon/lat. note a todo - check if we have all the parameters for this calculation, or if something is missing, what would we need to find / calculate. after we have the lon/lat of the detected manhole covers, we could do a verification step - under the assumption that infrastructure travels in straight lines most of the time (how correct is this assumption? are there standard bend/corner angles?), we could try and fit straight lines on the detected covers in a given small area (town limits? are there other indicators a line is broken? powestation / pump / etc?). covers on a straight line with others can be given a higher score (the detector score can also be included in this score - how sure is the detector).

## Assistant

I added a "Conversion to geospatial coordinates" subsection to Task 1 in `docs/BRAINSTORM.md`. It covers the assumed inputs, the distance-and-angle calculation, and the straight-line verification step with its combined score. I also added four open questions (camera details in Street View, lat/lng resolution, the straight-line assumption and bend angles, the line-fitting area and break indicators), two todos (check that all calculation parameters exist, and my search and verification later), and two assumptions (camera info and position known, infrastructure mostly straight).

Ready for the next item.

## User

we'll review task 1 later on, commit, push (no pr needed) and we'll clear and jump into task 2.

## Assistant

Committed and pushed to `main`. I ran the handover first, so `NEXT_STEPS.md` points to Task 2 brainstorming and to the Task 1 review later. You can `/clear` now.

## User

reminder, i'm working on a take home interview task, you're here to read my infodumps and arrange them in @docs/BRAINSTORM.md , and later on help me review, fact-find, make sure i addressed everything written in @Interview_Preparation.pdf and help me in creating visuals. ready to read my ideas on task 2?

## Assistant

Ready. I'll take your Task 2 ideas one item at a time and add them under a new `## Task 2` section in `docs/BRAINSTORM.md`, in the same structure as Task 1, with no input of my own until you say the brainstorm is done.

## User

task 2 is classification of manhole covers into different types (from the given exampes i assume the types are infrastructure - images show sewer/water/communication, but i assume there can be difference in providers as well). a small set of representative examples for a given region is provided, but as i understand, not on a scale enough for model training. i'm assuming all of the images are like the provided examples, crops of the manhole covers with a bit of background. the deterministic route here is feature extraction - shape using edge detector / hough transform, perhaps an OCR to extract text (need to check how well it works on dirty / eroded objects). texture can be extracted using classical methods (note: i can't remember the family or texture filters, find it later). if we know the pixel-to-mm ratio, we can also add actual size. maybe color can be extracted, not an exact rgb value, but a general black/gray/brown. then, given a feature vector of shape (one-hot on circle/square/rectangle), size (diameter, or max side), color (lets start with an rgb value, can change to one-hot if needed), and a vector of keywords (water/hot/sewer/storm - will need to build the dictionary and expand it on real data), we can cluster the images in the vector space (check PCA first to see if some signals are more relevant than the others), see where our provided examples land and if they can label each cluster and then use representative examples to label the clusters either human or vlm with a dedicated prompt ("describe the manhole cover in the image, what is its shape and color, does it have any text on it? which of the provided infrastructure types would you assign it and why?" - of course the prompt can be engineered, split into yes/no/unsure questions to limit hallucinations, for example). we can also run the manhole images throgh an image encoder such as a resnet without the classification layer to extract a feature vector and use that vector for clustering - easier way to extract shape/color/texture, but perhaps ocr as a parallel step, then continue from the cluster label step above. next i will discuss the non-deterministic approach.

## Assistant

I added a "Task 2: Classify manhole covers by type" section to `docs/BRAINSTORM.md` with problem understanding, the deterministic approach (feature extraction, feature vector, clustering and labeling with the VLM prompt draft, and the image encoder alternative), a placeholder for the non-deterministic approach, four open questions, two todos, and two assumptions.

Ready for the non-deterministic approach.

## User

the non-deterministic approach is using vlms and/or a tool like JEV for classification. vlms can be asked to describe each image in a prompt similar to the one mentioned in the cluster labeling step mentioned above, providing structured answers that can be encoded into feature vectors then clustered as above. we should add an "unknown" option to each feature to escalate to humans - the feacure vector encodings may change over a few iterations (adding keywords / colors / shapes, etc). perhaps a "word2vec"-like space can also be used, so that gray squares sit together, far from black circles, but i'm not sure about it. JEV is a tool that can be used for providing decisions, i know there are open source versions as well. todo: read if JEV (or similar) can be used here, if it supports "unknown" option for images that are out of the provided examples set and if it even works on images or if we need to convert to text to use it.

## Assistant

I filled in the Task 2 "Non-deterministic approach" subsection in `docs/BRAINSTORM.md` with the VLM description route (structured answers, an "unknown" option per feature, changing encodings, the word2vec-like idea marked as unsure) and JEV. I added two open questions (the word2vec-like space, and JEV's fit, "unknown" support, and image or text input) and a todo to read about JEV.

Ready for the next item.

## User

i want to add that any method using llms/vlms has a significant cost factor and latency as well, so i would perhaps use them only to gather enough data to train a model, or make sure they are limited to unexpected edge cases which require non-deterministic approaches that the standard DL models can't provide. next i'll go over the points for consideration and add notes if needed. you can commit and we'll clear and continue

## Assistant

I added a "Cost and latency note" to the Task 2 non-deterministic approach in `docs/BRAINSTORM.md`: LLMs / VLMs only to gather training data, or limited to unexpected edge cases. Then I ran the handover and committed. Next: the PDF's points for consideration.

## User

reminder, i'm working on a take home interview task, your role is to take notes, do not provide any input unless specifically requested. i finished going over task 1 and 2, now i'm going over points of consideration. i'll add notes for each point, if needed. you can add a section for "points for consideration" in the @docs/BRAINSTORM.md but i'll also require you to add to previous sections if needed. are you ready for the first point?

## Assistant

I added an empty "Points for consideration" section to `docs/BRAINSTORM.md`, after Task 2. Ready for the first point. I will also add to earlier sections when a note belongs there.

## User

the first point is "How would you define detection and classification problems in this context?" - i think i defined the problems well in task 1/2 sections above, so i'm skipping to the next point (note this statement for the first point).

## Assistant

I noted point 1 in `docs/BRAINSTORM.md` as covered by the Task 1 and Task 2 sections. Ready for the next point.

## User

"What data would you use, and how would you prepare it for this task?" - i went into detail for task 1 and a bit less for task 2. i think the main point that should be mentioned again is the calculation of relative positions of pixels in panorama images from the camera (taking into consideration camera parameters, panorama distortions, pix2mm conversions), then taking the lon/lat from json as the camera location and calculating the lon.lat of each detected manhole cover. there are still some open questions on what is needed and how to convert lon/lat to gis coordinates, but that's the main challenge in data preparation. additionally, some in-depth data understanding is required to prevent leakage, all detailed in task 1. this is my reply to point 2, is there anything that needs to be added to task 1/2?

## Assistant

I added point 2 to `docs/BRAINSTORM.md`. Two items were new, so I also added them to Task 1: panorama distortions in the conversion calculation, and an open question on converting lat/lng to GIS coordinates. Nothing new for Task 2.

## User

next point is "What type of models or learning paradigms would you consider, and why?". I think i detailed several options and the trade-offs, at the end i'd like to suggest a single pipeline rom all of the brainstorming options and trade-offs. is there anything missing? do not fill in anything, just tell me what's missing and i'll fill in if needed.

## Assistant

I recorded point 3 in `docs/BRAINSTORM.md` (options covered in Task 1 and 2, single pipeline at the end). Gaps listed for Anat (not written to the doc): detector alternatives and open-vocabulary detectors, boxes vs segmentation, panorama input handling, active learning, multi-view deduplication, few-shot / nearest-neighbor and zero-shot classification for Task 2, open-set "unknown" for the non-VLM route, one multi-class detector vs separate detector and classifier.

## User

i'll address these one at a time, note these under the current point. other detectors - YOLO is a quick option, I'm open to consider other detectors whether due to licensing, performance or other limitations. however, i don't think transformers are required in this case. transformers are costly to train, and their benefit is that they "see" the entire image, unlike CNNs that are more local. while there is an underground connection between manhole covers, i don't think it's enough to use a costrly transformer. I could check if a pre-trained transformer is better that a pretrained or finetuned CNN, but not re-train it. re: open-vocabulary detection, is moondream2 useful here, or one of the QWEN models?

## Assistant

I listed the gaps under point 3 in `docs/BRAINSTORM.md` and recorded Anat's notes on other detectors, with the moondream2 / Qwen question as an open question. Answer given in chat: both are VLMs that can return boxes from a text prompt (grounding), so both can work for open-vocabulary detection. Trade-offs: slower and more costly per image than a CNN detector, small covers in a large panorama likely need tiling, and output must be checked for hallucinated boxes. Fits best as a label generator (Case B options 1 and 2), not the production detector.

## User

list to check the open-vocabulary detectors you suggested. next is the "Boxes or masks" - boxes are enough at this point. Panorama input - this is a good point, i want to suggest the following flow - assuming we can easily cut the road/sidewalk as the lower half of the image, i would compare the detection on the undistorted lower halves to the still-distorted lower haves. theYOLO i mentioned has augmentations that allow for perspective and shear changes, so maybe the undistortion step is not required, but it's good to know that is an option. please list the undistortion as an option for task 1. Choosing what to label - i did not mention active learning, but this is a great way to decide what to label, i would probably get there from a leading question of "how would you select what to label". Duplicates across panoramas - important stage i had in my cell detector on tiled data project. after the manhole covers are detected and assigned real-world coordinates is a good stage for duplication removal, keep the higher-confidence examples, under the assumption that manhole covers can't overlap (and probably have a minimal distance definition as well) - any overlapping detection boxes are considered duplicated (check edge cases such as few-pixel overlap). Augmentation: if using the distorted panorama images, we can simulate different locations on the camera fov (different distortion). if undistorted - simulate any undistortion artifacts. other than that - mirroring is ok, rotation should be exhamined as we don't want to create images that don;t resemble the real world. lighting is definitely a requred augmentation - brightness for example, or any combination that allows for different weather/time-of-day apeparance. perhaps obstructions as well - manhole covers can be blocked by cars or pedestrians, so training with a section cut out (can't remember the name, mixoff?) can help. next is task 2, but first write the above under the current point and add mentions in the task 1 sections if needed.

## Assistant

I recorded the answers under point 3 in `docs/BRAINSTORM.md`. In Task 1 I added: open-vocabulary detector candidates (Case B option 2), active learning and augmentations (Case A), a new "Panorama input" subsection with undistortion as an option, duplicate removal after the geospatial conversion, two todos (check the open-vocabulary detectors, find the cut-out augmentation name), and two assumptions (lower half is road and sidewalk, covers don't overlap).

## User

Few-shot paradigms: i did not mention this explicitly, but for me it was implied that given unsupervised clustering with a few provided examples - the examples are used to label clusters based on distance such as knn. similarly, i'll use the outlier detection method i used in the similarweb takehome task to find which samples are not in any cluster and mark them for visual analysis (by human or vlm). Zero-shot classification: i did not mention it, what model would you suggest for this task? "Unknown" outside the VLM route: i think the outlier approach is good here. Encoder choice: resnet is an example, any other encoder can be used if there is time to do a comparison on this step as well, but for the scope of this task it's ok i think. One model or two: yes, definitely, if we have enough data, we could train another YOLO detector that has the specific labels, but this is something that depends on data availability, when working onm the cell detector at Scopio our first idea was to train the detector on ~60 labels, but some of these labels were very rare and data was very costly to label (hundreds of normal cells just to get one anomalous cell in the detection roi). the labeling cost in the detection task is lower, so this is defintely an option that then saves us from using an additional model.

## Assistant

I recorded the answers under point 3 in `docs/BRAINSTORM.md`, and added to Task 2: kNN cluster labeling and the outlier step (also the "unknown" option), the encoder note, a "Single model option" subsection, and an open question on the zero-shot model. Answer given in chat: CLIP-family models (OpenCLIP, SigLIP 2), with text prompts per cover type, possibly combined with the provided examples as image prototypes; risk that fine-grained or provider-specific types are weak in text form.

## User

add zero-shot models to the list to check. next point for consideration is "What are the main components of the system, and how do they interact?". the final system has a small image preproc module (cropping rois, optionally undistorting), a detector, a module for converting coordinates (given all the parameters i mentioned in task 1) of detected objects, then a dedup module based on real-world coordinates, and a "straight line checker" - which combines the detection score with a score representing if each detection is aligned with other detections - maybe ransac or a more modern alternative). next is a classifier (that can be incorporated into a detector+clasisifer model like yolo later on). finally a module that arranges the output into a format that is ingested by the next step - lets say lng/lat for map overlay or GIS (but i need to read more on GIS to understand the difference). the last model can also rearrange the data. btw, the classifier can be one-for-all that works for all regions, or a collection of several small classifiers, one per region. this either means one detector and classifier selected by area, or multiple yolo models (det+cls) selected by region, TBD after understanding the data and requirements.

## Assistant

I added point 4 to `docs/BRAINSTORM.md` (seven components in order, and the classifier scope). In Task 1 I added RANSAC to the line fitting, a new "Output" subsection, two open questions (map overlay vs GIS, line fitting method), and a todo to read on GIS. In Task 2 I added a "Classifier scope" subsection and a todo to check the zero-shot models.

## User

before the next point:  how the components interact, i'll mention the inputs and outputs of the final system, list them under each section. Image preprocessing - input is a path to image, so this module will also load the image and tile it after cropping if the crop is too lage as we don;t want to resize the input too much. if tiling, the detector should work in batches until all tiles are processed, and perhaps mix tiles from several images to optimize speed, and the source of each tile (image, coords in image) should be saved. output is an image (or a batch of images) for the detector. another input are the undistortion parameters (if requird). the detector output is a collection of detecttion per image in batch (local tile coordinates per image). the coordinate conversion module recieves all of the detections and the tile-to-image relationships and converts into real-world coordinates, if tiling, then its tile coords --> image coords --> real world coords, if no tile then just the last two steps. the output is a list of real-world coordinates of the detection boxes,  with the detector confidence. the dedup can be optimized and done by region rather than on all the detections (avoid comparing parallel street for example), kdtree is a good method for dedup, especially when using ckdtree method. the output is the same list of coordinates and conficence, just deduped. straight line checker returns the same list, just with an additional score column. the classifier gets only the detection crops (undistorted) and returns a label for each that is then added as a column to the detection list. the output formatting gets the detections list (with scores and labels) and arranges them in the required format, this is where we can calculate "final confidence" and use that to affect the way the detections are displayed in the final map - perhaps different color based on the score.

## Assistant

I added inputs and outputs under each of the seven components in point 4 of `docs/BRAINSTORM.md`. In Task 1 I added tiling to "Panorama input", per-region cKDTree deduplication, and the final confidence to "Output". In Task 2 I added the classifier input and output in the full system.

## User

"How would you measure whether the system is successful?" - there are several levels to that, validation and test sets for each of the component models, unitests for any logic (adding test per edge case encountered), but the final test (if at all possible) should be comparison to known real world data. if we have gt of an infrastructure line and its manhole covers, we can compare to that, or, if we can walk a specific street and mark the exact coordinates of the manhole covers, and compare to that. however, i'm not sure if this data is available at all. for the individual model evaluations, i would like to know if recall or precision is more important, and then understand what threshold is relevant for the task. i assume that if the manhole covers are just proxies to the actual infrastructure line, then missing one or two is ok, as long as the final line is located correctly, but if they are the actual goal, the threshold rises. the det+cls pipeline can be measured from a confusion matrix that represents both detection and classification mistakes.

## Assistant

I added point 5 to `docs/BRAINSTORM.md` (evaluation levels, and model evaluation). In Task 1 I added the evaluation levels to "Validation" and two open questions (real-world ground truth availability, recall vs precision and proxies vs goal). In Task 2 I added the combined confusion matrix.

## User

"What are the main challenges or failure modes you anticipate?" - i think data may be a challenge. distortions from panorama mode, multiple cameras and configurations, etc. lack of final GT (the infrastructure line). small mistakes or innacuracies in coordinates and calculations that add up to significant differences. the "straight line" module is also a question mark that can add confusion instead of clarity due to inherent assumptions that may be wrong. the classification - covers can be dirty or eroded, which affects image quality. covers can also be "anonymous" in a way that we won;t be able to classify them, or in a certain region, covers for different infrastructure can look the same. some providers can be significantly underrepresented.

## Assistant

I added point 6 to `docs/BRAINSTORM.md`, split into detection and classification challenges, and added a short "Challenges" subsection to Task 1 and to Task 2.

## User

that was the final point, but i want to add to the coordinate conversion module a comment on verification - it is said that i can assume the system operates in the US - ther should be a silent failure mode that alerts if the calculation places a detection outside of the stated region - it can indicate mistake in calculation or in the raw data that should be addressed.

## Assistant

I added the out-of-region alert to the coordinate conversion component (point 4) and to Task 1 "Validation" in `docs/BRAINSTORM.md`.
