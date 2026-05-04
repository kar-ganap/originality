# Phase 0.1 Consolidation Pass

**Phase:** 0.1 (Stage 0 — Foundation)
**Consolidation date:** 2026-05-04
**Gate:** Phase 0.1 plan validation gates §10 — "holistic review of
accumulated framing artifacts, Synthesis Pointers across review
files, Epistemic Scope subsections in `conceptual.md`, and pending
Phase 0.2 pre-registration batch items. Compress or prune where the
accumulated material is overlapping, noise, or doing less work than
its maintenance cost implies."

This document is the gate-10 evidence.

---

## Why this pass exists

Per the original phase plan, this is the deliberate end-of-phase
prune, *not* continuous compression during the phase. The rationale
(quoted from `phase-0.1-plan.md` §"Validation gates" item 10):
"pruning decisions are higher-quality once the full cross-paper
landscape is visible, at the cost of temporarily carrying some
redundancy."

In this case, the consolidation pass was *missed* in the initial
draft of `phase-0.1-retro.md` and `phase-0.2-plan.md`. Both were
written as accumulation artifacts (every check finding + every
Tier 2A surface absorbed without prune-or-keep evaluation). User
caught the miss; this document is the corrective pass.

---

## What was reviewed

| Artifact | Lines | Status |
|---|---:|---|
| `docs/phases/phase-0.2-plan.md` | 846 | reviewed; pruned |
| `docs/phases/phase-0.1-retro.md` | 533 | reviewed; amended (gate-10 row) |
| `docs/phases/phase-0.1-plan.md` | ~2000 | reviewed; not touched (historical record) |
| `literature-review/*.md` (11 files) | many | reviewed Synthesis Pointers; harvest deferred to Stage 3 |
| `docs/conceptual.md` Epistemic Scope subsections | ~90 | reviewed; no overlap with Phase 0.2 plan §14 |
| `docs/desiderata.md` | locked | verified Phase 0.2 commitments don't violate |

---

## Pruning decisions

Decisions split into:
- **Autonomous (A-D)**: clear over-engineering or methodology
  errors; applied without further user input.
- **User-judgment (E-I)**: scope-cut decisions requiring user call.

### A. §0 production junk-year-token list — chip names pruned [APPLIED]

**Issue.** Phase 0.2 plan §0 added `tms320`, `tms9900`, `mos6502`,
`z80` as junk-year tokens. **These are pre-1990 chip names**:
TMS9900 (1976), Z80 (1976), MOS6502 (1975). Including them as
junk-year tokens would systematically exclude legitimate 1970s-80s
hardware papers — a methodology bug, not a methodology choice.

Also at risk: `cnn` (Fukushima neocognitron 1980 lineage uses CNN
abbreviation), `rnn` (Hopfield/Elman/Jordan networks late-1980s),
`word embedding` (some 1980s connectionist papers use this term),
`https` (some 1989-90 networking papers reference it).

**Decision.** Pruned chip-family tokens + (cnn, rnn, word embedding,
https) from the production junk-year token list. Kept only
post-2000-coined terms: blockchain, transformer (model), smartphone,
R-CNN, IoT, internet of things, big data, cloud computing, GAN,
BERT, GPT, ChatGPT, attention is all you need, LSTM, OpenID Connect,
MQTT, WebRTC, TLS 1, digital twin, VR headset, wearable.

**Rationale.** The junk-year filter is a *defense against post-2000
content with `publication_year=1970` sentinel data*. Tokens that
existed pre-1990 don't serve that purpose; they cause systematic
false-positive exclusion of legitimate early-era CS+Physics papers.

**File touched.** `docs/phases/phase-0.2-plan.md` §0.

### B. §0 empty-abstract filter threshold — 30 → 15 tokens [APPLIED]

**Issue.** Phase 0.2 plan §0 specified "minimum 30 tokens after
inverted-index reconstruction." Pre-1990 abstracts (especially
conference papers) were often 50-100 words total; 30 tokens may
exclude legitimate short-but-substantive abstracts.

**Decision.** Relaxed threshold to 15 tokens.

**Rationale.** The methodological intent is to catch boilerplate
fillers like "abstract not available" / "preview only" (which run
~7-12 tokens). 15 tokens preserves the catch while not over-filtering
brief legitimate abstracts.

**File touched.** `docs/phases/phase-0.2-plan.md` §0.

### C. Robustness scope items #6 + #7 — removed (already in test specs) [APPLIED]

**Issue.** Phase 0.2 plan §"Robustness scope" listed item #6
(Test II three-spec team-size) and item #7 (Test IV quadratic +
interaction) as Stage-3 robustness items. Both are actually part
of the Test II + Test IV pre-registered specifications. Listing
them as "robustness" creates the impression they're optional or
Stage-3-only when they're load-bearing for the Test II + IV
pre-registrations.

**Decision.** Removed items #6 and #7 from robustness scope.
Re-numbered remaining items.

**Rationale.** Pre-registered test specifications are not
robustness; they're the primary analysis. Conflating the two
weakens the Stage 3 robustness commitment.

**File touched.** `docs/phases/phase-0.2-plan.md` §"Robustness scope".

### D. Retro gate-10 row mislabeled — corrected [APPLIED]

**Issue.** `phase-0.1-retro.md` validation-gates table row 10 was
"✅ This document". That conflated gate 7 (retro written) with
gate 10 (consolidation pass). Gate 10 was unmet at the time the
retro was written.

**Decision.** Separated gate 7 and gate 10 in the table; gate 10
becomes ✅ with this document's commit. Added a corresponding
"What I'd do differently next phase" lesson about doing the
consolidation pass deliberately (not at end-of-phase rush).

**File touched.** `docs/phases/phase-0.1-retro.md` validation-gates
section + lessons section.

### E. Test II compression — KEPT (E2) [USER DECISION]

**Question.** Test II has 3 specifications × 3 measures = 9
reportings. Compress to primary spec × primary measure with the
other 8 cells deferred to Stage 3?

**User decision.** **E2 (keep).** Test II is methodologically
engaging two distinct literatures (W-W-E vs Petersen 2025 spec
debate; semantic vs reference-graph scope measures). The full 9-
cell report is the *content* of that engagement.

**Rationale.** ws2's value-add on team-size methodology is
specifically that we engage both W-W-E and Petersen 2025
specifications head-on. Compressing to one spec would weaken the
methodology contribution. The 9-cell report is heavy but the
substantive payoff is real.

**File touched.** None (Test II spec unchanged).

### F. Test IV compression — KEPT (F2) [USER DECISION]

**Question.** Test IV pre-registers `novelty ~ team_diversity +
team_size + team_size² + team_diversity × team_size`. Compress
quadratic + interaction to Stage 3 robustness?

**User decision.** **F2 (keep).** W-W-E's saturation+reversal
pattern is empirically established; pre-registering the quadratic
captures it. Defending it later is harder than committing now.

**Rationale.** Pre-registration discipline favors specifying
likely-relevant terms upfront. The W-W-E literature establishes
that team-size has a non-monotone effect on cross-discipline
breadth (saturates 8-10, reverses); ws2's Test IV engages this
directly. Removing the quadratic at pre-reg time would force a
post-hoc addition if the linear spec showed non-monotonicity.

**File touched.** None (Test IV spec unchanged).

### G. Stage 1 prereqs — KEPT (G2) [USER DECISION]

**Question.** Phase 0.2 plan lists 7 Stage 1 prereqs. Compress to
5 by moving Genderize key procurement / NamSor account setup /
production-pull-spec dry run into Stage 1 initial tasks?

**User decision.** **G2 (keep).** All 7 prereqs affect Stage 1
planning (NamSor setup determines budget shape; pull-spec dry run
de-risks the bulk pull).

**Rationale.** A clean Phase-0.2 → Stage 1 gate requires the
methodology AND the operational setup to be locked. Moving setup
tasks into Stage 1 would weaken the gate semantics.

**File touched.** None (prereqs unchanged).

### H. Robustness scope items #5, #8, #9 — partially compressed (H1 with #5 kept) [USER DECISION]

**Question.** Mark #5 (subfield mechanism), #8 (Petersen 2024
inflation correction), #9 (Holst zero-ref filter) as "conditional
on reviewer push" rather than upfront commitments?

**User decision.** **H1 with #5 kept.** Conditionalize #8 and #9.
Keep #5 (subfield mechanism) as upfront commitment.

**Rationale.**
- #5 (subfield mechanism: canonical-concentration → divergence
  linkage) is intrinsic to claim #13's mechanism story. It's not
  reviewer-anticipation; it's the mechanism evidence for the
  paper's headline claim. Upfront commitment.
- #8 (Petersen 2024 inflation correction) and #9 (Holst zero-ref
  filter) are reviewer-anticipation defenses. Run only if reviewers
  push. Conditional commitment.

**File touched.** `docs/phases/phase-0.2-plan.md` §"Robustness scope".

### I. Lit-review Synthesis Pointers harvest — defer to Stage 3 [NO ACTION NOW]

**Question.** Multiple lit-review files' Synthesis Pointers reference
the same Methods sections. Compress into a single per-Methods-section
harvest pass now?

**Decision.** **No action now.** Synthesis Pointers are documented
per-paper for auditability. At Stage 3 paper-drafting, harvest all
Pointers per-Methods-section in a single pass. Keep per-paper
Pointers in the .md files as the source of truth.

**Rationale.** Per-paper Pointers preserve which paper contributed
which methodological commitment. A pre-emptive cross-file merge
would lose that audit trail. Stage 3 harvest is when Methods
section drafting needs the consolidated view.

**File touched.** None.

---

## What survived without prune

The substantial majority of accumulated material. Specifically:

- **§0 analytical population definition** (locked).
- **§4 demographic features** including the full Genderize +
  gender_guesser + NamSor + ORCID validation pipeline (locked).
- **§9 demographic-inference uncertainty stack** (a-e all locked).
- **§11 cluster-fit stratification** + production-scale re-validation
  + CV-by-region diagnostic (locked).
- **§9e propensity-corrected aggregates** (locked).
- **Per-metric N_target from Check 5b** (locked).
- **Test I (headline divergence)** specification (unchanged).
- **Test II three-spec × three-measure specification** (kept per E2).
- **Test III canonical concentration** specification (unchanged).
- **Test IV with quadratic + interaction** specification (kept per F2).
- **All 7 Stage 1 prereqs** (kept per G2).
- **Robustness items #1-#5** (embedding swap, anchor projection,
  Flavor A, cross-field replication, subfield mechanism).
- **Tier 2A close-read review files** with full template (Background
  + Three-Level Discourse + Study Questions + Challenge Corner +
  Synthesis Pointers + Discussion Notes).
- **conceptual.md Epistemic Scope subsections** (program-level
  positioning; no overlap with Phase 0.2 plan §14).

The pass identified a small number of specific compressions, not
a wholesale prune. This is consistent with the Phase 0.1 plan's
methodology-decision discipline being broadly correct.

---

## Methodological lesson logged

**The consolidation pass IS its own work item.** Writing the retro
+ pre-reg as accumulation artifacts (absorbing every check + every
surface) and then doing the consolidation as a separate pass is
appropriate — but the consolidation pass needs to be deliberately
scheduled, not assumed-implicit.

For Phase 0.2 + future phases: gate-N "consolidation pass" should
be its own todo item, not a sub-bullet of "write retro." Logged
to `tasks/lessons.md` with a note about putting consolidation
ahead of retro-writing in the next phase's order of operations.

---

## Verification

```bash
cd whitespace_2

# A: chip-family tokens removed
grep -A 25 "Junk-year-token filter" docs/phases/phase-0.2-plan.md | \
  grep -E "tms|z80|mos6502|^[ -]*cnn|^[ -]*rnn|word embedding|https" \
  && echo "BUG: A failed" || echo "A OK"

# B: empty-abstract threshold relaxed
grep -A 2 "Empty / near-empty abstract filter" docs/phases/phase-0.2-plan.md | \
  grep "30 tokens" && echo "BUG: B failed" || echo "B OK"

# C: robustness scope items #6/#7 removed
grep -A 2 "Test II three-spec" docs/phases/phase-0.2-plan.md && \
  echo "BUG: C failed" || echo "C OK"

# D: retro gate 7 + gate 10 separated
grep -E "^\| 10 " docs/phases/phase-0.1-retro.md | head -1

# H1: items #8 + #9 conditional; #5 unconditional
grep -A 2 "Petersen 2024 citation-inflation" docs/phases/phase-0.2-plan.md | \
  grep -i conditional && echo "H1 #8 OK" || echo "BUG: H1 #8 failed"
grep -A 2 "subfield mechanism test" docs/phases/phase-0.2-plan.md | head -3

# Consolidation-notes.md exists
ls -la experiments/phase-0.1/consolidation-notes.md
```

All checks should pass after this commit.
