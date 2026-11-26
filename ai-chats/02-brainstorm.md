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
