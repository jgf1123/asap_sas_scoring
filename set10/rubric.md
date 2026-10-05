# Scoring Codebook: ASAP-SAS Set 10 ("Doghouse")

*A rater-facing codebook. A rater (human or LLM) first records **codes**: what the response contains. The **scoring rules** then turn codes into a score. Every rule has an ID and a tier, so the scoring prompt can be assembled from a chosen subset (ablation). `score_from_codes.py` implements §4–§5 exactly.*

**Tiers**
- **O (official):** from the ASAP Set 10 rubric, item scoring guide, and anchor set.
- **C (consensus):** how the two human raters scored when they agreed (dev set). Where a C rule departs from the literal official text, it says so.
- **B (boundary):** cases where raters were inconsistent. Each has two variants: `.a` (closer to the official text) and `.b` (closer to observed rater behavior). A configuration picks one.
- **S (Score1-specific):** candidate tendencies of the official score's rater in splits. Evidence is thin.
- **R (reading notes):** how to read the data, not how to score.

**Assembly:** §1–§7 can go into the scoring prompt. §8 (evidence) is documentation only.

---

## 1. The task students saw

Brandi and Jerry ran a controlled experiment on how lid color affects the air temperature inside a glass jar under a lamp. Four lids were tested (black, dark gray, light gray, white), three trials each, 10 minutes, starting at 24 °C:

| Lid color  | Trial 1 | Trial 2 | Trial 3 | **Average** |
|------------|---------|---------|---------|-------------|
| Black      | 54      | 52      | 54      | **53 °C**   |
| Dark gray  | 48      | 48      | 48      | **48 °C**   |
| Light gray | 44      | 45      | 46      | **45 °C**   |
| White      | 42      | 43      | 41      | **42 °C**   |

Hypothesis stated in the task: *"The darker the lid color, the greater the increase in air temperature in the glass jar, because darker colors absorb more energy."*

Prompt: *Brandi and Jerry were designing a doghouse. Use the results from the experiment to describe the best paint color for the doghouse. In your description, be sure to: (1) choose a paint color; (2) describe how that color might affect the inside of the doghouse; (3) use results from the experiment to support your description.*

## 2. Reading notes (R)

- **[R1]** Each response begins with the color the student selected from a menu, followed by `::`. The *chosen color* is the one the text argues for. Usually this is the menu color; see B5 when they differ.
- **[R2]** Spaces inside words (e.g., `dogho use`, `tempat ure`) are artifacts of digitizing handwritten lines, not student errors. `(DEG)` is a transcribed degree sign.
- **[R3]** Spelling and grammar errors are the student's own (transcribed as written) but are never scored. Judge meaning only.
- **[R4]** Length is not evidence. Code what is present, not the effort.

## 3. Codes: what to look for

Record each code as 1 (present) or 0 (absent), plus any flags. **All codes concern temperature or heat.** A statement about some other quantity ("it got less", "more energy for the dog") does not earn a code.

| Code | Present when the response… | Examples | Not this code |
|---|---|---|---|
| **E** effect | states that the chosen color makes the **doghouse interior, or the dog inside it**, warmer or cooler, including one-sided "won't get too hot" | "the inside will stay cooler"; "it won't get too hot in the doghouse" | no direction ("it will affect the temperature inside"); the dog *outside* the doghouse; a two-sided claim (that is J) |
| **J** just right | claims the temperature will be moderate on **both** sides | "not too hot or too cold"; "just right"; "a medium temperature" | "comfortable" without temperature terms; one-sided (that is E) |
| **D** direction | compares the **temperature** of colors: a comparison, superlative, or trend | "not as hot as black"; "white is the coolest"; "darker colors get hotter" | "absorbs less heat" with no other color named; "the darkest color" (not temperature) |
| **N** results | cites a **temperature result from the experiment**: a number, a lid's ranking, or the trend the experiment showed | "white averaged 42 °C"; "the black lid made the jar hottest" | general physics not attributed to the experiment ("dark colors absorb heat") |
| **P** placed | the experiment result places the **chosen color** relative to at least one other lid (requires N) | "light gray (45 °C) was cooler than black (53 °C)"; "white was the coolest lid" | a result for the chosen color alone ("light gray averaged 45 °C"); results only for *other* colors |
| **L** literal | treats a jar temperature as the doghouse's own temperature | "the doghouse will be about 48 degrees"; "45 °C is a perfect temperature" | relative statements ("11 °C cooler than black") |
| **U** misunderstanding | misunderstands the experiment or the science (see subtypes) | — | — |

**U subtypes:** (1) off-target, non-temperature reasoning (the dog's mood or energy, darkness for sleeping, airflow, dirt, preference); (2) a mechanism the experiment does not support (warmth **at night**, color "keeps heat in"); (3) the wrong direction for the color (white keeps the dog *warm*); (4) self-contradiction: opposite effects claimed under the **same** conditions (e.g., saying the color both blocks heat and warms the inside). Seasonal claims ("cooler in summer, warmer in winter") are **not** contradictions; code them as E or J; (5) nonsensical numbers (doubling a jar reading to "80 degrees inside").

**Flags** (note any that apply):

| Flag | When |
|---|---|
| `consistency` | the response reasons from a lid's readings being the same across trials ("dark gray stayed 48° every time") |
| `hyp` | the only "result" is the task's hypothesis restated ("they said darker colors absorb more energy") |
| `vague` | the only "result" is a contentless reference ("according to the data", "based off the results") |
| `mismatch` | the text argues for a different color than the menu choice |
| `physics` | the response's only content is a general claim about how colors absorb or reflect heat or light |

## 4. Scoring rules: official (O) and consensus (C)

Apply in order. The first rule that fires sets the score.

- **[O1] Full credit, 2 points:** the response gives the effect of its chosen color **and** supports it with experiment results. Operationally:
  - **[O4a] White or black:** N = 1 and (E = 1 or D = 1). The item guide accepts an absolute result for these colors ("the white lid only went up to 42 °C").
  - **[O4b] Gray:** P = 1 and (E = 1 or J = 1). The item guide's examples for gray are comparative ("8 °C cooler than black"). A gray choice also needs its goal stated, because "gray" alone does not imply warmer or cooler.
  - **[C2] Implied effect (white/black):** in O4a, D can substitute for E. "White was the coolest lid: 42 °C" earns 2 without an explicit doghouse statement. *Departs from the literal official text, which requires an explicit effect; agreeing raters consistently credited it as implied.*
- **[C1] U → 0.** A response that has not earned full credit and shows a misunderstanding (U = 1) earns 0. A misconception alongside a full-credit answer does not remove credit. *(Official O3: "little or no understanding".)*
- **Boundary rules B1–B2** (§5) apply next, if their conditions hold.
- **[O2] Partial credit, 1 point:** E = 1 or J = 1 (an effect without supporting results), **or** N = 1 (results without an effect).
- **[C3]** Within O2, a gray "not too hot, not too cold" claim (J) counts as an effect.
- **Boundary rule B6** (§5) applies next, if its condition holds.
- **[O3] 0 points:** none of the above.

Supporting rules:
- **[O5]** A trend the experiment showed counts as a result (N), and as a direction (D).
- **[C4]** General physics ("dark colors absorb more heat") stated as knowledge, not attributed to the experiment, is **not** N.
- **[C5]** L does not cost credit when the full-credit rule is met. A literal reading alongside a valid comparison still earns 2.
- **[C6]** Same-every-trial reasoning (`consistency`) never makes P = 1 on its own. It does not place the chosen color relative to another lid.

## 5. Boundary rules (B): pick one variant per rule

Each rule has the form *if [condition], then [action]*.

- **[B1] Consistency reasoning without placement.** *If* flag `consistency` and P = 0:
  - **[B1.a]** then score 0.
  - **[B1.b]** then score 1 if E = 1 or J = 1, otherwise 0.
- **[B2] Literal temperature claim without placement.** *If* L = 1, N = 1 and P = 0:
  - **[B2.a]** then score 0.
  - **[B2.b]** then score 1 if E = 1 or J = 1, otherwise 0.
- **[B3] Hypothesis restated as a result.** *If* flag `hyp`:
  - **[B3.a]** then set N = 0 (and P = 0) before applying §4.
  - **[B3.b]** then keep N as coded.
- **[B4] Vague reference to the data.** *If* flag `vague`:
  - **[B4.a]** then set N = 0 (and P = 0) before applying §4.
  - **[B4.b]** then keep N as coded.
- **[B5] Menu color differs from the argued color.** *If* flag `mismatch` and the response would earn 2:
  - **[B5.a]** then score 2 (score the argument as written).
  - **[B5.b]** then score 1.
- **[B6] General physics only.** *If* no other rule has fired and (flag `physics` or D = 1):
  - **[B6.a]** then score 0.
  - **[B6.b]** then score 1.

## 6. Score1-specific candidates (S)

- **[S1]** A bare effect with no reason or mechanism (e.g., "it will make it cooler") scores 0, not 1. *(In 4 white/black splits, Score1 gave 0 where Score2 gave 1.)*

## 7. Output

Report the codes (E, J, D, N, P, L, U), any flags, a score of 0–2, and a one-sentence rationale naming the codes that decided the score.

## 8. Evidence and provenance (documentation only: not part of the scoring prompt)

**Data:** dev = 300 random Set 10 train responses (seed 0). Codes for all 300 are in `eda/dev_codes.csv`, built by `eda/build_dev_codes.py`.

**How the codes were made:**
1. First pass, blind to scores (`eda/gray_codes.csv`, `eda/extreme_codes.csv`). The user spot-checked 6 gray codes and corrected one (26993: "energy" was the dog's energy, not heat; this led to the temperature-only requirement).
2. Second pass after seeing scores: sharpened E, J, D, N; added P, U and flags. Every change is an explicit override in `build_dev_codes.py`. **These codes are fitted to dev, not blind.**

**Fit check (`eda/step3f_rule_fit.py`, agreed dev cases, n = 267):**

| Configuration | Agreed exact match | Splits matched: Score1 / Score2 (n = 33) |
|---|---|---|
| First-pass codes, unified rule (before sharpening) | ≈ 0.86 | — |
| All `.a` | 0.895 | 18 / 13 |
| All `.b` | 0.918 | 13 / 18 |
| Best of 64 (B1.b, B2.a, B3.b, B4.a, B5.b, B6.b) | 0.929 | 16 / 16 |

**Key first-pass evidence for O/C rules (agreed cases):**

| Rule | Evidence |
|---|---|
| O4a / C2 | White/black: comparative data + effect → 2: 73/74. Comparative data, no explicit effect → 2: 10/13 |
| O4b | Gray: comparative data → 2: 15/20. Gray result without comparison → 2: 1/14 |
| O2 / C3 | Gray "not too hot/cold" only → 1: 20/21. White/black effect, no data → 1: 58/67 |
| C1 (U) | Off-target → 0: 17/17. Misapplied mechanism / wrong direction / contradiction → 0: all agreed cases in dev |
| C5 | Gray comparative + literal reading → 2: 6/6 |
| C6 | Gray consistency reasoning without comparison → 2: 0/6 |
| B6 | Physics-only claims: agreed scores split roughly evenly between 0 and 1 for near-identical texts (e.g. 26762 → 1, 27046 → 0) |

**Changelog:**
- **v1.0** (2026-10-04): code-based rubric; frozen for the blind remainder rule check (`eda/prereg_step2.md`).
- **v1.1** (2026-10-04): U subtype (4) reworded. The v1.0 example "cooler… and also warmer" matched ordinary seasonal answers; in the 20-response pilot the LLM coded U = 1 for 27508 ("slightly warmer in winter, slightly cooler in summer"), scoring 0 vs Score1 = 1. Now restricted to opposite effects under the same conditions, with seasonal claims excluded explicitly.
- **v1.2** (2026-10-04): C1 (U → 0) moved below the full-credit rules. In the two v1.1 dev runs, 4 responses scored 2/2 by both raters (e.g. full comparative results plus "black traps the heat" or "warm at night") were zeroed by C1. Raters did not remove credit for an incidental misconception. Dev what-if from v1.1 LLM codes: QWK 0.776 → 0.820 (all-a). Also paraphrased the subtype (4) example, which was near-verbatim from a dev response.

**Known limits:**
- Rules and codes were fit to the same 300 dev responses. The fit check above is optimistic by construction. Their value must be measured on the remainder set.
- The best-of-64 configuration was selected on dev. Differences between configurations are 2–6 responses.
- Retired rule: the earlier "bare effect for black" boundary was replaced by U (misapplied mechanism). Two of its seven cases fit U; the others look like rater noise (e.g., 27033).
