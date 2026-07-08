# Phase 2 · Experiment C (the disruption reconciliation) — retro

**Status: COMPLETE.** Outcome: the two-channel **decoupling is confirmed on the full 24M-paper
citation graph** (consolidation *and* fragmentation both rising, orthogonal). Our mid-course
*adjudication* hypothesis (that Park's CD-decline is a reference-length artifact) was **run to a
decisive test and disconfirmed by our own data** — the decline is real. This is the honest,
positive landing: we **confirm** Park and add the orthogonal fragmentation channel his narrative
misses.

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
   CD (149.6M edges, 137.5K per-year focals, `cd_index_csr`) settled it.

## The decisive result (C-2-full)

- **C-2a-full ✓ — Park replicates cleanly.** `CD-vs-year = −0.00086`, CI `[−0.00091, −0.00081]`,
  monotone **0.050 (1975) → 0.013 (2020)** across all eras (41% CD-eligible, not the sample's
  selection-biased 0.85%). A faithful 24M-scale replication of the disruption-decline.
- **C-2b-full ✗ — NOT a reference-length artifact.** Two independent length controls agree:
  - **mediation** (control the focal's + its citers' reference length): the year-slope attenuates
    only **24%** (`−0.00086 → −0.00065`) — below the 50% gate.
  - **random length-cap** (refs→8, early-era level): the slope **steepens** to `−0.00154`
    (−78% "attenuation") — length, if anything, *dampens* the decline.
  Reference lists did grow (5.9→19.0) but that is not the cause. **The pre-registered C-2b gate is
  NOT met ⇒ the adjudication is disconfirmed; the decline is a real consolidation signal.**

## What the model does and does not explain

The **empirical decoupling is real on both channels**, at 24M scale:
- **Consolidation:** CD↓ (Park, replicated) **and** `H`↑ (canon Gini, WS2 2.2).
- **Fragmentation:** atypicality↑ (WS2 2.4).
- They **coexist, orthogonally** — both rising under the demographic-scale lever.

The C/V ABM **reconciles this via `H`↑ (κ-channel) + atyp↑ (τ-channel)** — both model-reproduced
and data-confirmed. Park's CD-decline is an **independent third confirmation** of the consolidation
channel. The model's PA substrate gets the *CD-index's* sign backwards (C-1) — a **documented
limitation of the minimal model**, not a data artifact, and it does not affect the `H`-based
reconciliation.

## Honest caveats

- **Length artifact only.** We tested the reference-*length* prong of the CD-critique. A
  **citation-coverage/practice** artifact (recent papers better-covered) is untested — a separate,
  deeper investigation we deliberately did not open (it would re-litigate the whole Park debate and
  would not change the decoupling thesis). So: "not a *length* artifact," not "provably a pure
  signal."
- **Model overstated length.** C-1b showed length *can* flip CD in the toy; on the data it
  accounts for only ~24%. The minimal model's length-mechanism is real but not the empirical driver.
- **Recent-year eligibility.** 2024 focals are the fast-cited minority; but the decline is monotone
  through the middle decades, so it is not a recent-edge artifact.
- **Snapshot/field.** All-field (CS+physics) population, focal CD on the full graph (Park-style);
  our snapshot/field defs won't match Park's CD *magnitude* (the trend + controls are the targets).

## Whitespace-independence bridge

`cd_index` originated in WS3 (`measures.py`) and was **vendored WS3→WS2** (`v_extension.py`, pin
`282e09f`) with a byte-equivalence test; the 24M-scale `cd_index_csr` (scipy-sparse) is tested
bit-for-bit against it. WS3 read the WS2 Volume (`ws2-section0`) as *data* (no code coupling),
mirroring how WS3 earlier vendored `reference_atypicality` FROM WS2.

## Implications for the paper + D's fate

- **The paper is the confirmed decoupling + the C/V reconciliation.** Thesis: intellectual
  production **consolidates and fragments at once** — the canon concentrates (CD↓, `H`↑) while the
  semantic/recombination frontier fragments (atyp↑); the minimal C/V ABM reproduces both from one
  lever (the κ/τ orthogonality + the crossover). We confirm Park and locate the missing channel.
- **D (cross-field OOS) — deferred.** Per plan §5, A–C landed *mixed* (A pass, B partial, C
  confirms the decoupling but disconfirms the adjudication detour), so D is not the clean capstone
  it would have been; the positive result stands without it. Revisit only if the paper needs a
  cross-field generalization rung.
