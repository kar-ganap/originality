# Phase 2 · Experiment C (the disruption reconciliation) — retro

**Status: COMPLETE.** Final outcome (after three successive, more-careful tests): **the CD-index is
length-robust but observation-window-FRAGILE**, so it is *not* load-bearing for the paper. The
apparent CD-decline in our corpus is an **all-time-observation-window artifact** — under a fixed
forward-citation window (Park's own method) disruption is **flat-to-rising**, which *agrees* with
the atypicality-rise (WS2 2.4). The two-channel **decoupling stands on window-robust measures**:
`H`↑ (concentration, WS2 2.2) ⊥ atypicality↑ (fragmentation, WS2 2.4). CD is reported as a
methodological fragility finding + a consistency check that engages the Park debate, **not** as a
pillar. We neither confirm nor overturn Park (our within-population graph ≠ his full graph); we show
that *in our corpus* the naive decline is window-artifactual and our thesis does not need CD.

*(Superseded landings, kept for the honest record: C-2-full first read as "the decline is real,
decoupling confirmed on both channels incl CD↓" — until C-2c showed that decline was itself a
variable-window artifact. Each test refined the prior.)*

## The hypothesis, and how it evolved

C set out to reconcile **Park–Leahey–Funk 2023** (the CD "disruption is declining" result) with
WS2 2.4's atypicality-*rise*. The arc:

1. **C-1 (model, `cd_C.py`).** The CD index on the attachment channel (`channel.py`): under κ,
   CD **rises** (`+0.33→+0.38`) — a correct property of preferential attachment (a hub's citers
   cite the hub + *other* hubs, not its specific prereqs). The model reproduces canonical
   concentration as **Gini `H`↑**, NOT as CD↓ — CD is the wrong operationalization of the κ-channel,
   and the PA substrate gets its sign backwards (rung-4b's substrate-sign problem, on CD).
2. **C-1b (model, `cd_C1b.py`).** Holding the model's reference length fixed and injecting
   length-inflation drags CD-vs-birth monotonically `+0.0067 → −0.0018` (×0→8), flipping negative
   at ~×4. ⇒ *hypothesis:* the empirical CD-decline could be a reference-length artifact
   (Petersen-Holst-Macher). This **reframed C from reconcile → adjudicate.**
3. **C-2 sample (`cd_data_C2a/b.py`).** On the 1M sample the within-panel graph is only 1.9%
   dense (0.24 in-panel refs/paper): the decline replicates (`−0.00266`) but is selection-confounded
   and NOT in-sample decomposable (7% mediation). Pre-registered truncation limit.
4. **C-2-full (`cd_data_C2_full.py`).** The phase-1.2 parse retained refs for the full **24M v3
   population**; step-0 density check = **46.7%** in-population (25× the sample) ⇒ GO. Dense-graph
   CD (149.6M edges, 137.5K per-year focals, `cd_index_csr`, **all-time citations**): the decline
   replicates (`−0.00087`) and is **NOT length-driven** (mediation 24%; random cap *steepens* it).
   Read at the time as "the decline is real." ⇒ *hypothesis:* the length prong is not the artifact.
5. **C-2c (`cd_data_C2c_coverage.py`) — the decisive test.** The coverage battery caught what
   C-2-full missed: C-2-full used **all-time** citations, so old focals had ~50-yr observation
   windows and recent ones ~6 — and the CD-index reads long windows as disruptive. Correcting to a
   **fixed forward-citation window** (Park's own method) **erases the decline**.

## The decisive result (C-2c)

- **Fixed forward-citation window ⇒ no decline.** `W=5` (focals ≤2019): slope **+0.00044**, CI
  `[+0.00037, +0.00052]` (rises `−0.009 → +0.012` over 1970–2019). `W=10` (focals ≤2014): **+0.00006**,
  CI `[−0.00002, +0.00014]` (flat). The all-time `−0.00087` was the **observation-window artifact**.
- **Not the other coverage prongs either.** Field-growth control attenuates the year-slope only
  14%; reference-recording completeness is uniform across eras (pre-digital `−0.00083` ≈ born-digital
  `−0.00093`, the free sub-period pre-check). And not length (C-2b, 24%). ⇒ the CD-index is
  **length-robust but window-FRAGILE**; the naive all-time decline is essentially all window.
- **Fixed-window disruption AGREES with atypicality.** Flat-to-rising structural disruption matches
  the atypicality-*rise* (WS2 2.4): in our corpus, structural novelty is **not** declining.

*(Censoring: the year-tail showed the 24M population runs to 2025–26, so `last_complete=2024`
bounds a clean forward window; `cd_index_csr` gained tested `window`/`year_min` filters.)*

## What the model does and does not explain — the landing

The two-channel **decoupling stands on window-robust measures**, at 24M/WS2 scale:
- **Consolidation:** `H`↑ (canon Gini, WS2 2.2) — robust. *(Not CD↓: the CD-index is window-fragile.)*
- **Fragmentation:** atypicality↑ (WS2 2.4) — robust; and fixed-window CD is flat-to-rising, the
  **same direction** (a consistency check, not a pillar).
- They **coexist, orthogonally** — both rising under the demographic-scale lever.

The C/V ABM **reconciles this via `H`↑ (κ-channel) + atyp↑ (τ-channel)** — both model-reproduced and
data-confirmed. The CD-index is **not load-bearing**: the model's PA substrate mis-signs it (C-1),
and the data shows it is window-fragile (C-2c) — two independent reasons to build on `H` + atyp
instead. **Paper placement:** thesis on `H`↑ + atyp↑ (core results); CD's window-fragility +
consistency-with-atypicality in a **robustness/discussion subsection** that engages the Park debate
without staking the thesis on the fragile measure.

## Honest caveats

- **We do NOT overturn Park.** Park uses a fixed window and still finds a decline; our within-
  population graph (46.7% dense, CS+physics OpenAlex) ≠ his full WoS graph. The defensible claim is
  narrow: *in our corpus* the all-time decline is window-artifactual and fixed-window disruption is
  flat-to-rising. The gap from Park is corpus/coverage; a bold "disruption isn't declining" claim
  would need the full graph and is not made.
- **Model overstated length.** C-1b showed length *can* flip CD in the toy; on the data it accounts
  for only ~24%, and the real culprit was the observation window, which the toy did not model.
- **Methodological lesson.** C-2-full used all-time citations — a genuine error; CD must use a fixed
  forward window from the start. C-2c caught it. (Recorded in `tasks/lessons.md`.)
- **Snapshot/field.** All-field (CS+physics) population; population runs to 2025–26 (year-tail), so
  a clean fixed window bounds focals to ≤ `last_complete − W`.

## Whitespace-independence bridge

`cd_index` originated in WS3 (`measures.py`) and was **vendored WS3→WS2** (`v_extension.py`, pin
`282e09f`) with a byte-equivalence test; the 24M-scale `cd_index_csr` (scipy-sparse) is tested
bit-for-bit against it. WS3 read the WS2 Volume (`ws2-section0`) as *data* (no code coupling),
mirroring how WS3 earlier vendored `reference_atypicality` FROM WS2.

## Implications for the paper + D's fate

- **The paper is the decoupling + the C/V reconciliation, on window-robust measures.** Thesis:
  intellectual production **consolidates and fragments at once** — the canon concentrates (`H`↑)
  while the semantic/recombination frontier fragments (atyp↑); the minimal C/V ABM reproduces both
  from one lever (the κ/τ orthogonality + the crossover). **CD → a robustness/discussion
  subsection** engaging the Park debate: the naive all-time decline is window-fragile, fixed-window
  disruption is flat-to-rising (matching atyp) — so we build on `H` + atyp, not CD. This engages the
  field's most visible result without staking the thesis on a fragile measure.
- **D (cross-field OOS) — deferred.** Per plan §5, A–C landed *mixed* (A pass, B partial, C = a
  methodological fragility finding on CD + a window-robust decoupling), so D is not the clean
  capstone it would have been; the positive result stands without it.
