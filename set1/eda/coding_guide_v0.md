# Set 1 blind coding guide, v0 (dev, first pass)

Written 2026-10-05 before reading any dev responses for coding. Coder: Claude, blind to Score1/Score2
(exception: six dev responses whose scores were already seen in steps 1b/1c: 1141, 1276, 1589, 1561, 409, 753;
marked `seen=1`).

**Unit.** A code is 1 if the response identifies that piece of information as needed or missing for
replication: phrased as a need ("you would need to know…"), a question ("how much vinegar?"), a criticism
("they didn't say…"), or by supplying a value the procedure should state ("use 100 mL of vinegar").
Code what is identified, not whether it is phrased well. Spelling is never judged.

## Codes (0/1)

| Code | 1 when the response identifies… | Not this code |
|---|---|---|
| `VA` | the amount of vinegar (including "the same amount in each container") | vinegar type (VT) |
| `VT` | the type, brand, concentration, acidity or pH of the vinegar | amount (VA) |
| `MAT` | which samples or materials to use (the procedure does not name them) | sample size (SIZE) |
| `SIZE` | sample size, shape, surface area, or the mass/amount of each sample to use | measuring mass (other: tool) |
| `RT` | how long to rinse the samples | amount of rinse water (other) |
| `DRY` | how or where to dry the samples (method or conditions) | drying time, which is given (other) |
| `CS` | container size or volume | container type (CT) |
| `CT` | container type, material or shape | container size (CS) |

## `other`

Short labels, separated by `;`, for any other information named as needed. Use a consistent label for the
same idea (e.g. `rinse water amount`, `cover containers`, `mass tool`, `temperature`, `soak time (given)`,
`dry time (given)`). Information already stated in the procedure gets `(given)`. Labels are reviewed with
the user before any becomes a code.

## Flags (separated by `;`)

| Flag | When |
|---|---|
| `change` | suggests changing the experiment (other liquid, longer time, different samples) rather than naming missing information |
| `purpose` | asks for or supplies the purpose, hypothesis, conclusion, or what the vinegar should do / what should happen |
| `restate` | restates procedure steps as if they were the answer |
| `labelled` | uses numbered or labelled points, or `^p` breaks to separate items |
| `unfinished` | ends mid-sentence or mid-word |

`note`: optional, a few words on anything unusual (no long quotes).

## Clarifications made during coding (still blind to scores)

Decided while coding and applied to all 300; one earlier row changed as a result (53: `labelled` removed):
- **`labelled`** only for numbers, bullets, letters, or `^p` breaks that separate items. Ordinal words in prose
  ("first… second…") and `^p` breaks in mid-sentence do not count.
- **`MAT`** also when the response supplies the sample names as needed information ("you need marble,
  limestone…"), and when it asks for the specific kind of a material (type of wood or plastic).
- **`SIZE`** also for "the same / equal starting mass" or "how much of each sample".
- **Temperature:** while drying → `DRY`; during the 24 hours or of the vinegar/rinse water → `other: temperature`.
- **Control:** proposing one → `other: control` + flag `change`; only asking whether there is one → `other: control`.
- **Measuring mass:** `mass tool` (instrument), `mass method` (procedure, e.g. weigh the cup first, mass separately),
  `mass units` (grams etc.).
- **Ambiguous phrases are not coded** and are explained in `note` (e.g. "how long the samples": time or size?).
