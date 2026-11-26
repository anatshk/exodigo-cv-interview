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
