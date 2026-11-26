## User

i want you to review @docs/BRAINSTORM.md and compare with @Interview_Preparation.pdf , lmk if there is anything i missed. you;re in scribe mode, you can suggest changes but don;t change anything without explicit approval

## Assistant

I compared the brainstorm with the PDF. You covered the two tasks, all six points for consideration, the US-only assumption, and the open label set. I changed nothing. These are the gaps I found, most important first:

### Missed or thin compared with the PDF

1. **How you select parameters and optimize the algorithm.** The PDF asks for this directly: "explain how you will select parameters and optimize your chosen algorithm." The brainstorm only touches it for the Hough and edge-detector parameters. It is missing for:
   - the detector confidence threshold and NMS IoU
   - tile size and input resolution
   - the distance radius for removing duplicates
   - the tolerance for the straight-line fit
   - the kNN `k` and the outlier threshold in Task 2

   Suggestion: add a short "Parameter selection" item under each module, saying which metric each parameter is tuned on and on which split.

2. **Images from several years.** The PDF stresses "images captured over multiple years for specific locations." The brainstorm uses `date` only for season balance and leakage. It does not use the extra years as evidence:
   - A cover seen at the same place in several years should get more confidence.
   - A cover seen only once may be a false positive, or it may have been removed or paved over.
   - Duplicate removal then also has to merge across years, not only across nearby panoramas.

3. **Comparison with sensor-based estimates.** The PDF says the output "can be compared with other sensor-based underground utility estimations." The Output section covers the format only. It is missing:
   - **A position error per detection** (for example, an error radius in meters). Without it, a sensor team cannot decide whether a cover matches their estimated line.
   - **How cover type maps to utility type**, so a cover can confirm or contradict a sensor line of the same type. This is the "increase confidence" goal stated at the top of the PDF.
   - The option to use the sensor estimates as weak validation where there is no ground truth. This links to your point 5.

4. **Point 1, problem definitions.** You wrote "covered, no additional notes." Point 1 is the first question in the PDF, so consider writing a two-line formal definition:
   - Detection: one class, from panorama to boxes plus confidence, then to lat/lng.
   - Classification: open-set, few-shot, per region, with "unknown" as a valid output.

### Worth adding (my suggestions, not from the PDF)

5. **The metadata may already answer some open questions.** Example: `images/9yDqTCL0Ck-INprOyghgfA.json`.
   - The images are 13312 x 6656 (2:1), which suggests an equirectangular projection. Each pixel would then map directly to a horizontal and vertical angle, so focal length and sensor size may not be needed.
   - `tilt` ≈ 90 likely means "level with the horizon", in degrees.
   - Distance would then come from the camera height plus a flat-ground assumption.

   This is from memory and is not verified. It belongs to the fact-finding step, but it may change the "Camera information is available" assumption.

6. **Triangulation from several views.** You treat a cover seen in several nearby panoramas only as a duplicate. Those views can also be combined to compute a more exact position than one view and a flat-ground assumption give.

7. **Ask Exodigo before the interview.** The PDF says "Please reach out if something is not clear." Some open questions, for example recall vs precision and whether the covers stand in for the utility line or are the actual goal, could be sent to them before the interview instead of being assumed.

### Structure

8. The top-level `## Todos` and `## Open questions` sections are empty. The real lists sit under each task. Either fill the top-level sections or remove them.

Tell me which of these you want added and I'll write them into the brainstorm.

## User

1. you're right, i had an implict assumption. i'll make it explicit - yolo detector allows for detection and classification threshold tweaking - we can use it to control fps/fns (i did this in the past with a higher confidence threshold for a specific class more sensitive to fps). nms iou i would'nt touch unless i see a problem, the objects are far enough apart. tile size and input resolution depend on the data- i would decide it after the first iteration. dist radius and line tolerance - can depend on building standards, so leave it for now. outliers - also, i'll start with defaults and change after first iteration when i know more. add a section in the document saying that parameter tuning should be done per module, but not is current scope. 2. this is a great point - i'll add a database of known objects (it can be per region to keep a small size), duplication over the years/months - great point, add it as well. 3. How cover type maps to utility type - these are the classifier labels. the output organization section can have access to a dictionary of providers to convert label to what users want to see (just type? type + provider?). if the goal of this task is not to add confidence to sensor measurements, w can use those measurements as weak labels, but otherwise, it's leakage. 4. agree, add "un/semi-supervised" for the classification section. 5. add these assumptions to the relevant section. 6. this is a great point! add a "consider tirangilation from multiple images as a lication improvement step". 8. remove.

## Assistant

I updated `docs/BRAINSTORM.md`:

1. Replaced the empty `## Todos` and `## Open questions` sections with a new `## Parameter tuning` section. It says tuning is done per module and is out of current scope, and lists your notes per parameter.
2. Task 1, "Duplicate removal": duplicates over months and years, plus a new "Known objects database" block (per region, confidence rises when a cover is seen across years).
3. Task 1, "Output": the provider dictionary that converts labels to what users see. Task 1, "Validation": sensor estimations as weak labels only if the goal is not to add confidence to them, otherwise leakage.
4. Task 2, "Problem understanding": problem type is unsupervised / semi-supervised classification.
5. Task 1, "Conversion to geospatial coordinates": the metadata assumptions (equirectangular, tilt in degrees, camera height plus flat ground), marked "to verify". Also added to the Assumptions list.
6. Same section: triangulation from multiple images as a location improvement step to consider.

Not added, since you did not mention them: the position error per detection (from point 3) and asking Exodigo questions before the interview (point 7). Tell me if you want either one.

## User

commit and we'll move to the next step - creating a write-up file as something i refer to in my presentation (including visuals). we can do it as a README.md in the repo.

## Assistant

Committed as `2908f17` on `main`. It contains `docs/BRAINSTORM.md` and the new session log. I left the untracked `claude_logs/` folder out because I don't know what it is.

Here is my plan for the write-up. I'll wait for your OK before writing anything.

### Where it goes
`README.md` already exists, with the task summary and the repo layout. I'll put the write-up first and move the repo layout to a short section at the bottom. Figures go in `docs/figures/`. The work goes on a branch `docs/writeup`, which we merge with a PR.

### Outline
The outline follows the PDF's six points, because the interviewers will likely go through them in that order.

1. **Goal and assumptions:** the task in three lines, then every assumption with its reason.
2. **Problem definition:**
   - Detection: one class, from panorama to boxes, then to lat/lng.
   - Classification: open-set, semi-supervised, per region, with "unknown" as a valid output.
3. **Data and preparation:** the metadata fields, dataset splits by location and season with no leakage, label selection, and augmentations.
4. **Models and approach:** the chosen pipeline, plus a short table of the alternatives we considered and why we didn't choose them.
5. **System components:** a pipeline diagram, plus a table with the input and output of each module.
6. **Pixel to lat/lng:** the geometry, the duplicate removal across views and years, the known objects database, and triangulation.
7. **Parameter selection:** per module, out of scope for now.
8. **Evaluation:** the three levels, and the combined confusion matrix.
9. **Challenges and failure modes.**
10. **Questions for Exodigo.**

### Visuals
- **Pipeline diagram:** Mermaid. GitHub renders it directly, so there is no image file to keep in sync.
- **Sample panorama:** downscaled. The originals are 13312 px wide. I'd annotate it with the lower-half region of interest and a visible cover (`Kk0_Hzv4bQc2ha7esbEDcw`).
- **The three cover examples from the PDF:** cropped from page 2.
- **Geometry sketch:** a camera at a known height, the angle down to a pixel, and the ground distance. A small hand-written SVG.
- **Optional:** a sketch of a location-based split (for example cities or neighborhoods in separate folds).

The panorama and PDF figures would come from a small script in `scripts/`, so they can be regenerated.

### Two things to settle first
1. **The final pipeline.** The brainstorm has several options, and `NEXT_STEPS.md` says you choose the single pipeline. The write-up needs that choice. Do you want to state it now, or should I draft section 4 from the options that seem to lead in your notes, so you can correct it?
2. **Fact finding.** The geospatial conversion, the Street View fields, the YOLO license and the open-vocabulary models are still unverified. My recommendation: draft now, mark unverified claims "(to verify)", and run the fact-finding pass afterwards to remove those marks. The other option is to do fact finding first, which is slower but gives a cleaner first draft.

## User

WRITEUP.md instead of readme, make the readme refer to it. 1. the pipeline i want to focus on is the full system i described in "What are the main components of the system, and how do they interact?" consideration point. we'll start with the final system and then dive into data labeling and model training (not part of final system, exept for the active learning loop). 2. start with draft, fact finding after. make sure to be concise, i want the document to be an easy read.

## User

Here is a note offered by a side agent:

> Heads up · The sample panorama files are 4:1 strips, not the 2:1 size their metadata states, so the committed pixel-to-angle assumption may be wrong.
>
> **Sample panoramas are not full 2:1 images**
> - The JSON metadata says each panorama is **13312 x 6656** (2:1). For a full 360° panorama, that ratio would let each pixel map directly to an angle.
> - The actual PNG files in `images/` are **4096 x 1024 or 3328 x 832** (4:1). They look like a horizontal strip around the horizon, about ±45° up and down. The top and bottom are cut off.
> - The brainstorm we committed says "the images are 2:1". The main agent mentioned the mismatch only briefly while making figures.
> - This matters for the pixel-to-lat/lng step. With the wrong vertical angle per pixel, distances to covers come out wrong.
> - **Check that the brainstorm and the write-up both say this**, and add it to the questions for Exodigo.

note this comment - wdyt?

## Assistant

The draft is ready on branch `docs/writeup` (not committed). `WRITEUP.md` starts with the final system (the seven modules from point 4), then covers labeling and training, with the active learning loop as the only training part inside the running system. Visuals: a Mermaid pipeline diagram, the road ROI on a sample panorama, a pixel-to-ground geometry sketch, the same intersection from 2007 to 2025, and the three cover examples from the PDF. `README.md` now points to it.

The side agent's note is correct. The write-up now has a caution in "Pixel to lat/lng" and a question for Exodigo. The brainstorm still says "The images are 2:1", which needs your OK to fix.

## User

yes, apply the brainstorm fix. commit, no pr needed in this repo. i'll have reviews on the writeup draft - i can change the text myself, but i'll refer you to visual changes

## Assistant

I applied the 4:1 strip fix in two places in `docs/BRAINSTORM.md` and committed the write-up, figures, figure script and brainstorm fix to `main` (no PR). Ready for your visual review notes.

## User

first, the diagram is way too small. perhaps split it into 2 rows, to is up to step 3 (incl), the bottom starts with dedup untile the end. the known db should be connected to the straight line checker as well, i'll renamge that module as "confidence reviewer" or simila,r it will add stright line confidence but also time-based confidence from th known object db

## Assistant

I split the main diagram into two rows (steps 1 to 3, then 4 to 7), connected the known objects database to module 5, and renamed module 5 in the diagram to "Confidence reviewer (straight lines, years seen)". I moved the active learning loop to its own small diagram in section 1.8. I could not render it locally (the npm download for the Mermaid renderer was blocked), so please check it on GitHub. Not committed.

## User

i'm currently reviewing iin obsidian md reader, is that ok?

## Assistant

Yes, Obsidian works for this. It draws Mermaid diagrams itself, so you'll see the two-row layout there. Two things that may look different from GitHub: images show only if the vault is the repo folder, and the table of contents links use GitHub-style anchors that Obsidian may not follow.

## User

i want an arrow from 3 to 4, is tan be s-shaped between the rows. placce the known obj db in row 3 with arrows to 4 and 5. change the shape of the input (step 0) to be a document

## Assistant

I replaced the Mermaid diagram with an SVG, `docs/figures/system_pipeline.svg`, because Mermaid drops the row layout when a node links across rows. It has the S-shaped arrow from 3 to 4, the known objects database in a third row with arrows to 4 (both ways) and 5, and step 0 as a document shape. Not committed.

## User

image is good, but needs to be larger, same for image in 1.3

## Assistant

I added explicit `width` and `height` to both SVGs (pipeline 1100 x 400, geometry 900 x 330). Without them the reader picks a small default size. If they are still small, the limit is Obsidian's "Readable line length" setting, which caps content width. Not committed.

## User

size is good, commit.

## Assistant

Committed to `main`.

## User

1.5 - replace "Straight line checker" with "Confidence reviewer", mention the known obj db

## Assistant

I renamed section 1.5 to "Confidence reviewer" with two scores: straight lines, and years seen from the known objects database. I also updated row 5 of the module table to match. Not committed.

## User

great, commit. push, we'll clear and start with the fact-checking phase

## Assistant

Committed and pushed to `main`, then ran the handover so the next session starts with fact checking.
