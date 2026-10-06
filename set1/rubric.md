# Scoring Codebook: ASAP-SAS Set 1 ("Acid Rain")

*Draft v0.2 (2026-10-06; v0.1 2026-10-05), for review. A rater (human or LLM) records **codes**: what information a response
identifies as missing. Deterministic **scoring rules** then turn the codes into a score.*

**Assembly.** §1–§4 are the scoring prompt: the model records codes only and never sees the scoring rules.
§5 (scoring rules) is implemented by `score_from_codes.py`. §6 (evidence) is documentation only.

**Rule tiers** (§5)
- **O (official):** from the ASAP Set 1 rubric and anchor papers.
- **C (consensus):** what the two human raters did when they agreed (dev set).
- **D (documented default):** a choice where raters were inconsistent or cases were too rare to test; taken
  from the rubric's wording, applied as a single rule (no alternative variants).

---

## 1. The task students saw

A group of students wrote the following procedure for their investigation.

**Procedure:**
1. Determine the mass of four different samples.
2. Pour vinegar in each of four separate, but identical, containers.
3. Place a sample of one material into one container and label. Repeat with remaining samples, placing a single sample into a single container.
4. After 24 hours, remove the samples from the containers and rinse each sample with distilled water.
5. Allow the samples to sit and dry for 30 minutes.
6. Determine the mass of each sample.

The students' data are recorded in the table below.

| Sample | Starting Mass (g) | Ending Mass (g) | Difference in Mass (g) |
|---|---|---|---|
| Marble | 9.8 | 9.4 | –0.4 |
| Limestone | 10.4 | 9.1 | –1.3 |
| Wood | 11.2 | 11.2 | 0.0 |
| Plastic | 7.2 | 7.1 | –0.1 |

Prompt: *After reading the group's procedure, describe what additional information you would need in order to
replicate the experiment. Make sure to include at least three pieces of information.*

## 2. Reading notes

- **[R1]** Line breaks are the student's own. Line breaks, numbers, bullets or labels usually mark what the
  student meant as separate items.
- **[R2]** Spelling and grammar are the student's own (transcribed as written) and are never judged. Read for meaning.
- **[R3]** Length is not evidence. Record what is present, not effort.
- **[R4]** Some transcriptions are cut off mid-sentence. Record only what is written, and set the flag `unfinished`.
- **[R5]** The data table names the four samples, but the procedure does not. Judge the procedure as written.

## 3. What to record: the coding principle

Record a code only when the response presents that information as **missing or needed to replicate the
experiment**: by asking for it ("how much vinegar?"), saying it is needed ("you would need to know…"),
criticizing its absence ("they never said…"), or supplying a value the procedure should state ("use 100 mL").

Do **not** record a code for:
- items listed as **equipment to gather** ("I would need a scale, containers, paper towels…");
- **suggestions to change** the experiment, including replacing something ("use glass bottles instead",
  "leave them for 48 hours", "add a control");
- **catch-all phrases** that name no specific information ("the brands of all the products", "more details");
- information the procedure **already states** (soaking 24 hours, drying 30 minutes, distilled water, measuring mass);
- anything the student **did not say**. Do not fill in a missing referent: "how much water" is not vinegar,
  and "how much to put in each container" without saying what is not the amount of vinegar.

Record each code at most once, however many times it is mentioned.

## 4. Codes

| Code | Present when the response identifies as missing or needed… | Not this code |
|---|---|---|
| **VA** | the amount of vinegar (including "the same amount in each container") | the type of vinegar (VT) |
| **VT** | the type, brand, concentration, acidity or pH of the vinegar | the amount (VA) |
| **MAT** | which samples are tested: names them as needed information, asks what they are, or says the procedure should identify them | vague "materials" (MATV); the specific kind of a sample (MATK) |
| **MATV** | "materials" mentioned vaguely, with no reference to the tested samples, or samples named only in an equipment list or in a restated procedure | a request to identify the samples (MAT) |
| **MATK** | the specific kind of a sample (which wood, which plastic, what kind of marble) | which samples are tested (MAT) |
| **SIZE** | the size, shape, surface area or physical form of the samples | how much sample (AMT) |
| **AMT** | the quantity or mass of each sample to use ("how much of each sample", "equal starting masses") | size or shape (SIZE) |
| **RT** | how long to rinse the samples | the amount of rinse water (RINSE) |
| **RINSE** | other rinsing details: amount of rinse water, how to rinse, how many times | rinse time (RT) |
| **DRY** | how, where or at what temperature to dry the samples | drying time, which is given |
| **CS** | the size or volume of the containers | container type (CT) |
| **CT** | the type, material or shape of the containers | container size (CS) |
| **COVER** | whether the containers should be covered or closed | |
| **ENVT** | the temperature during the 24 hours (room, samples, vinegar or rinse water) | drying temperature (DRY) |
| **ENVL** | light or dark during the 24 hours | |
| **ENVP** | where the containers are kept during the 24 hours, or other surrounding conditions | |
| **MASS** | how to measure mass: the instrument, method or units | |
| **DESIGN** | a control, number of trials, or repetitions | |

**Flags** (record any that apply):

| Flag | When |
|---|---|
| `change` | the response suggests changing the experiment rather than naming missing information |
| `purpose` | the response asks for or supplies the purpose, hypothesis, conclusion, or what should happen |
| `restate` | the response restates the procedure or data as if that were the answer |
| `unfinished` | the response ends mid-sentence or mid-word |

**Other:** list any other information the response identifies as missing, in a few words each.

**Levels.** Record each code at one of three levels:

| Level | When |
|---|---|
| **2 present** | the response clearly identifies this information as missing or needed (§3) |
| **1 borderline** | the response may identify it, and one of the reasons below applies |
| **0 absent** | otherwise |

Borderline reasons (record the letter for every borderline code):
- **(a) vague:** the wording is general enough to mean this or something else.
- **(b) referent:** what the information refers to is unstated, unclear, or possibly the wrong word.
- **(c) garbled:** the text is scrambled, misspelled past recognition, or cut off at that point.
- **(d) framing:** unclear whether the response asks for this information or instead lists equipment, suggests a change,
  restates the procedure, asks only that something be kept the same, or asks why.
- **(e) two readings:** the phrase fits this code under one reading and another code (or none) under another.
- **(f) other:** another reason; state it in a few words.

If you cannot name a reason, the code is present or absent, not borderline. If a vague mention fits a code made
for it (vague "materials" is MATV; amount of sample is AMT), record that code as present instead of marking
another code borderline.

---

## 5. Scoring rules (applied to the codes by `score_from_codes.py`; not in the prompt)

The score is the number of distinct credited pieces of information, at most 3. A code counts only when it is
recorded **present (2)**; borderline (1) is not credited (crediting it is a secondary analysis, see §6).

- **[O1] Count:** 3 pieces → 3, 2 → 2, 1 → 1, none → 0.
- **[O2] Rubric pieces:** VA, VT, MAT, SIZE, RT and DRY each count as one piece.
- **[D1] Container:** CS or CT counts as one piece; both together still count as one, not two. *The rubric lists "size/type of container" as one item.*
- **[C1] Surroundings:** ENVT, ENVL or ENVP is credited as an "other acceptable response". *Agreed dev cases.*
- **[D2] Surroundings count once:** any of ENVT, ENVL or ENVP counts as one piece; two or three together still count as one. *Raters split on separate aspects; rare.*
- **[C2] Covering:** COVER counts as one piece. *Anchor 2a and agreed dev cases.*
- **[C3] Not credited:** AMT, MATV, RINSE, MASS, DESIGN and "other" items. *Agreed dev cases; MASS also anchor 1a.*
- **[D3] Specific kind:** MATK is not credited. *The rubric asks "what materials to test"; too few cases to test.*
- **[O3] Flags do not change the score.** `unfinished` is reported separately (see open questions).

## 6. Evidence and open questions (documentation only)

**Evidence.** Dev = 300 random Set 1 train responses (seed 0), coded blind to scores
(`eda/coding_guide_v0.md`, `eda/dev_codes.csv`), then refined after seeing scores with auditable overrides
(`eda/dev_overrides.csv`: SIZE/AMT and MAT/MATV/MATK splits). Leave-one-out residuals on agreed cases
(`eda/step2_codes_vs_scores.py`, section D): rubric pieces +0.85 to +1.12; AMT +0.22; MATV +0.21; surroundings
(temperature) +0.92; mass measurement −0.10; rinse-water amount −0.07. Rules fitted on dev: QWK 0.892, exact 0.837
(`eda/step3_baselines_vs_codes.py`), an optimistic estimate.

**Changes from the dev coding.** RINSE, COVER, ENVT/ENVL/ENVP, MASS and DESIGN are new codes for "other"
labels; the coding principle (§3) adds exclusions found in `eda/step3_baselines_vs_codes.py` (equipment lists,
substitutions, catch-alls, unstated referents).

**Truncated transcriptions.** Some transcriptions are cut off, so the raters scored text the model never sees
(`eda/step1b_truncation.py`, `eda/step1c_truncation_tagger.py`). Results will be reported with and without
responses flagged `unfinished` (a text-only flag, so it can be applied to the test set without its labels).
On dev (`eda/step3b_truncation_classifiers.py`), about half of `unfinished` responses were scored by both
raters above what their visible codes support (5 of 10, against 14 of 290 unflagged); cuts that end at a
full stop cannot be detected from the text.

**RINSE.** Rinse-water amount was not credited on agreed dev cases (n = 14). Rinse method or count appeared
twice (1247, 271), both rater disagreements in which only Score1 gave credit, so there is no consensus
evidence for it; it stays uncredited under C3.

**Levels (v0.2).** v0.1 recorded codes as 1/0. v0.2 adds a borderline level with stated reasons, because dev
showed repeated borderline cases (vague wording, unstated or mistaken referents, garbled or cut-off text,
framing, two readings). Primary rule: only present counts. Secondary analyses: crediting borderline, and
routing responses whose score depends on a borderline code to human review. Predictions about how often the
level is used and whether it tracks rater disagreement: `eda/prereg_levels.md`.
