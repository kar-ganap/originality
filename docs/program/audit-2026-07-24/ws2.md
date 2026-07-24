# WS2 Adversarial Audit — Whitespace 2 (empirical OpenAlex/CS decomposition)

Auditor: independent. Scope: `whitespace_2/` only. Branch: `ws3-phase-2-empirical-bridge`
(clean tree). Date: 2026-07-24. Method: read code + committed artifacts, reproduced every
token-free claim I could from committed data (no raw parquet, no API, no cloud — `data/*` untouched).

---

## EXECUTIVE SUMMARY

- **ref_gini matched-null withdrawal (93% / +0.999 / singleton regime): SURVIVES CLEANLY.** Reproduced
  exactly from committed artifacts, and the null means regenerate **bit-for-bit (0.000e+00)** from the
  committed series alone — the null genuinely depends only on edge/target counts.
- **Age-restricted substrate gate (CS declines all 3 windows; "never reported"): SURVIVES.** Slopes match
  to the digit (t = −7.0/−6.1/−4.0); the series is absent from the phase-2.2 retro and divergence verdict.
- **"Measured correctly: CS canon flat, Physics rises": SURVIVES.** canon_share flat-to-declining + entropy-
  deficit falling in all 6 cells; cohort volume-controlled CS≈0 / Physics +0.0027…+0.0031; 24M pop confirmed.
- **Demographic plurality rises sharply: SURVIVES** (minor: a 2019→2024 plateau/decline the headline glosses).
- **Semantic fragmentation across three families: WEAKENED.** Directionally up on all 3 (perm-significant), but
  collinearity-controlled significance holds on **one** family; and WS2 measured mean-pairwise-cosine, not "atypicality."
- **MOST IMPORTANT FINDING:** the entire withdrawal lives **only on this unmerged branch**; `main` (the official
  record) still asserts "the citation canon concentrates," and `null_ref_gini.py` does not exist there.

---

## FINDINGS (most-severe first)

### [HIGH] `main` still asserts the withdrawn positive claim; the correction is unmerged
- **Claim affected:** the whole concentration withdrawal + program headline.
- **Location:** `main:whitespace_2/CLAUDE.md:16-17` vs this branch `whitespace_2/CLAUDE.md:14-83`.
- **What's wrong:** On `main`, WS2's headline reads *"Claim #13 robustly DISCONFIRMED … reframed as 'the citation
  canon concentrates while the semantic frontier + authorship diversify'"* with **0 correction markers**;
  `null_ref_gini.py`, `canon_share.py`, `cohort_concentration.py` are **absent** on main; the root program
  `CLAUDE.md` on main also has 0 WITHDRAWN markers. The withdrawal is 3 commits (`9a43718` 2026-07-22,
  `a0b99f4` 2026-07-22, `ae64b85` 2026-07-23) living **only** on `ws3-phase-2-empirical-bridge` (divergent:
  38 ahead / 3 behind main). A paper built from `main` inherits the *withdrawn* claim; the correction has
  never been reviewed/merged and is entangled in an unmerged WS3-named branch.
- **Evidence:** `git show main:whitespace_2/CLAUDE.md | grep -c "CORRECTION 2026-07-22"` → 0;
  `git cat-file -e main:whitespace_2/src/whitespace2/null_ref_gini.py` → absent;
  `git merge-base --is-ancestor 9a43718 main` → false. **CONFIRMED.**

### [MEDIUM] WS2 CLAUDE.md body still states the withdrawn headline as "Current Stage / Headline"
- **Claim affected:** concentration reframing.
- **Location:** `whitespace_2/CLAUDE.md:113-126` (and `:70`).
- **What's wrong:** Even on this branch, the "Current Stage" bullet asserts the reframed positive result
  ("the citation canon concentrates while the semantic frontier + authorship diversify"). It is flagged
  superseded by two boxes 100 lines above (the author explicitly chose not to edit the body), so it is
  *honest*, but a reader landing on the headline bullet reads the withdrawn conclusion as current.
- **Evidence:** direct read. **CONFIRMED.**

### [MEDIUM] "Semantic fragmentation across three families" is directional; strict significance is one-family; metric ≠ "atypicality"
- **Claim affected:** semantic-fragmentation leg.
- **Location:** `experiments/phase-2.3/series/aggregate-3family.json` vs
  `experiments/phase-2.2/series/robustness-sweep.json`.
- **What's wrong:** The raw permutation test (aggregate-3family) shows CS mean-pairwise-cosine up and
  perm-significant on all three families (SciNCL +22.6%/+3.35σ, Qwen3 +6.6%/+3.07σ, SPECTER2 +3.4%/+2.2σ,
  all p=0.0001). But the collinearity-controlled test (`resid_sig`, year VIF 44.3) is **True only for SciNCL**;
  Qwen3 mean-pairwise `resid_sig=False`; the other two semantic metrics (cluster_entropy, effective_dim) are
  non-significant, and cluster_entropy **reverses** under Qwen3 (raw_sd 0.099, dir down). So "fragmentation on
  three families" is really "mean-pairwise-cosine rises directionally on three, robustly-significant on one."
  Separately, the audit brief/program call this "atypicality↑" — **WS2 never computed atypicality**; the metric
  is embedding spread (mean pairwise cosine). The doc's own language ("pairwise cosine ↑ robustly; cluster-
  entropy/effective-dim noisier") *discloses* the softness, so this is a phrasing/label risk, not a hidden defect.
- **Evidence:** extracted `resid_sig` per spec; `aggregate-3family.json` values. **CONFIRMED.**

### [LOW] Committed null artifact uses 300 replicates; the runner default + documented command use 200
- **Claim affected:** bit-exact reproducibility of `ref-gini-null.json`.
- **Location:** `experiments/phase-2.2/null_ref_gini.py:74` (default 200) + docstring command (no `--replicates`)
  vs committed `ref-gini-null.json` (`n_replicates: 300`); `src/whitespace2/null_ref_gini.py:271` default 200.
- **What's wrong:** Running the documented command reproduces the *statistic* (93%) but not the committed
  artifact bit-for-bit (different replicate count → different RNG consumption → different null_slopes array).
  Headline robust either way.
- **Evidence:** artifact `n_replicates=300`; my RNG regeneration matched only when I used 300. **CONFIRMED.**

### [LOW] Documented quick-start test run fails 5 tests (missing `demo` extra)
- **Claim affected:** "make test passes" reproducibility gate.
- **Location:** `README.md:20-24`, `CLAUDE.md:273-279`, `pyproject.toml:54` (`gender_guesser` in `demo`, not `dev`).
- **What's wrong:** `uv sync --extra dev && make test` → **5 failed** (all `ModuleNotFoundError: gender_guesser`),
  277 passed, 1 skipped. Need `--extra demo`. Environmental, not a code defect; the concentration/null/metric
  tests all pass.
- **Evidence:** `uv run pytest -q` output. **CONFIRMED.**

### [LOW] Withdrawal box understates ref_gini's excursion (peaks 0.126, not 0.060)
- **Claim affected:** the "never leaves the near-all-singletons regime (0.013→0.060)" phrasing.
- **Location:** `CLAUDE.md:44`.
- **What's wrong:** ref_gini's stated range is start→end (1970→2024); the series actually **peaks at 0.1264 in
  1995** then *declines* to 0.060 by 2024. Still far below canon-scale (0.8), so the regime claim holds; if
  anything the hump means even "ref_gini rises" was a linear-fit-over-a-hump — further undercutting the original
  concentration reading, so the withdrawal is understated, not overstated.
- **Evidence:** committed series; max at year 1995. **CONFIRMED.**

### [LOW] Demographic "rises sharply" glosses a 2019→2024 softening
- **Claim affected:** demographic robustness headline.
- **Location:** `experiments/phase-2.2/series/demographic-joint.json` (CS).
- **What's wrong:** CS joint plurality rises 2.86 (1970) → 4.50 (2019) then dips to 4.375 (2024). The overall
  rise (+3.30σ) is large and robust; the endpoint plateau/decline is undisclosed in "rises sharply."
- **Evidence:** committed series. **CONFIRMED.**

---

## REPRODUCTION LOG

**Ran (all token-free, committed data only):**
- `uv sync --extra dev` → exit 0. Env: numpy 1.26.4, scipy 1.15.3.
- `uv run pytest -q` → **277 passed, 1 skipped, 5 failed** (5 = `gender_guesser` missing, `demo` extra). Key
  suites green: `test_null_ref_gini.py`, `test_concentration_measures.py`, `test_metrics.py` → **41 passed**.
  Null tests directly validate the argument: birthday-principle rise under uniform attachment, singleton-regime
  vs real-canon magnitudes (>0.80), vectorized≈exact per-paper null, pool-calibration recovers distinct count.
  Concentration tests validate the fixes: `canon_share` flat where ref_gini rose, matched-null tracks volume,
  volume-control removes density confound.
- **Independent null reproduction from committed artifacts** (`scratchpad/audit/repro_null.py`):
  - PART A (deterministic, from `ref-gini-null.json`): CS observed +0.001162/null +0.001084 = **93.3%**, corr
    **+0.9989**; Physics 92.6%, corr **+0.9996**; excess +0.000078 / +0.000089. Matches CLAUDE.md to the digit.
  - PART B (regenerate null means via RNG from `semantic-canonical.json` alone, seed 20260722, 300 reps,
    feeding a single fake `[n_ref_edges]` paper): `max|mine − committed| = 0.000e+00` for **both** fields →
    confirms the null is a pure function of (edges, distinct-targets) and the committed artifact is genuine.
  - PART C (age-restricted gate from `semantic-canonical.json`): CS W=3/5/10 = −0.00132/−0.00114/−0.00082
    (t=−7.0/−6.1/−4.0) DECLINES all three; Physics +0.00192/+0.00215/+0.00249 RISES. Matches doc.
- Replacement measures from committed artifacts: `canon-share.json` all 6 canon_share slopes ~0→negative,
  entropy-deficit slope negative in all 6; `cohort-concentration-pop.json` CS volctrl W10 −2.05e-5 / W5 −1.12e-4
  (≈0), Physics W10 +0.00309 / W5 +0.00274. `cohort-indegree-pop.json` header `n_population=24492279` (24M backed).
- Provenance: `git` merge-base checks; `main` vs branch content diff.

**Could NOT reproduce (marked NOT INDEPENDENTLY REPRODUCED — requires raw data):**
- Replay positive control `replay_max_error=0.0` — needs `data/base-1m/*.parquet` (raw referenced_works).
  Corroborated *indirectly* by the bit-for-bit null-mean regeneration (PART B), which shares the same
  `gini`/pool code path.
- Underlying per-year series values (ref_gini, mean_pairwise, cluster_entropy, effective_dim, age-restricted
  Gini, 24M in-degree) — taken from committed JSON; I verified slopes + internal consistency, not the
  embeddings / citation parse (requires 1M embeddings + population parquet).
- Female-share 22.4%→31.9% (phase-1.3) — not re-derived (separate artifact, requires raw demographic tables).

---

## WHAT SURVIVES CLEANLY (explicit coverage)

1. **Matched-null withdrawal of ref_gini** — 93% arithmetic, +0.999 correlation, singleton regime, near-identical
   CS/Physics vs opposite-direction age-restricted Gini: reproduced exactly *and* null means regenerate bit-for-bit
   from committed data. The null is a genuine matched null (uniform attachment; pool calibrated so expected distinct
   targets match observed; mechanism removed) and is unit-tested. **This is a sound, well-instrumented refutation.**
2. **Age-restricted substrate gate** — CS declines at all three windows (significant), Physics rises; and it is
   genuinely absent from the phase-2.2 retro and divergence verdict ("never reported" holds; ref_gini was the
   reported metric and is the `negative_control` in `divergence-verdict.json`).
3. **Replacement measures (canon_share + cohort in-degree)** — code computes what the prose says (fixed-K,
   own-year denominator; density-controlled fixed-window in-degree over the 24M population); committed artifacts
   match "CS flat / Physics rises"; matched nulls + density control are unit-tested.
4. **Subfield-mechanism null** (`phase-2.3/series/subfield-mechanism-results.md/.json`) — γ₁ sign is embedding-
   determined, significant specs contradict; honestly reported as "no robust localized mechanism," with committed
   perm p-values. No overclaim there.
5. **Demographic rise** and **CS semantic non-decline** — backed by committed series with standardized effects and
   permutation p-values (not bare point estimates).

**Overall:** the correction itself is rigorous, honest, and (uniquely for this program) matched-null-instrumented
and unit-tested. The residual risks are governance/record (main un-merged and still positive), one un-updated
in-body headline, and a semantic-fragmentation phrasing slightly stronger than the collinearity-controlled numbers.
