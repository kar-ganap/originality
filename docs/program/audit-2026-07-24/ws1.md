# WS1 ch.2 (OSS adjudication arm) — Independent Adversarial Audit

Scope: `/Users/kartikganapathi/Documents/Personal/random_projects/originality/whitespace_1` only.
Branch: `ws3-phase-2-empirical-bridge` (all WS1 ch.2 work lives here; **unmerged to `main`**). Working
tree clean before and after the audit — every reproduction below was byte-identical, so nothing tracked
was modified. No paid API calls were made.

---

## EXECUTIVE SUMMARY

- **RUNG 0** (imposed strategy collapse, gap +9.9% CI [6.3,13.9]) — **SURVIVES.** Bit-exact reproduce; CI excludes 0; both skeleton procedures pre-registered. Caveat: the "reasoning>output" headline is **procedure-specific** (the `decisions` skeleton reverses, −6.8%, and that CI *excludes* 0 too).
- **RUNG 1** (output-null replicates; P_top4 = sampling artifact, 232%/p=0.19) — **SURVIVES.** Bit-exact reproduce; the matched null is genuine and kills the arm's *own* concentration (conservative direction).
- **RUNG 2a** (V_reason also holds, null deepens; V_out −0.001, V_reason +0.0026) — **SURVIVES.** Bit-exact reproduce.
- **RUNG 2b** (reasoning actuator not live, uptake +0.009 CI straddles 0 → unreadable) — **SURVIVES**, honestly caveated as single-implementation.
- **INSULATION** (Claim #17 NOT supported; gap −0.017 CI [−0.165,+0.123], p=0.66) — **SURVIVES as a null**, but the "Claim #17 unsupported" prose over-generalizes one equal-size operationalization.
- **Single most important finding:** 3 of 5 rungs (rung-1/2a/2b) have their **raw per-run artifacts gitignored** — only summary JSONs are committed. Bit-exact reproducible on *this* disk; **not** regenerable from a fresh clone. None of the three fatal program failure-modes (matched-null vulnerability, uncertainty-free crossover, provenance-fabrication) are present in the fired work.

---

## FINDINGS (most-severe first)

### [MEDIUM] Reproducibility gap — rung-1/2a/2b raw artifacts are gitignored, only summaries committed
- **Claim affected:** RUNG 1, RUNG 2a, RUNG 2b (bridge replication, null-deepens, actuator-not-live).
- **File:** `whitespace_1/.gitignore` lines 2–4 (`runs/rung1-r4/`, `runs/rung2-r4/`, `runs/rung2-reasoning/`); `experiments/analyze_rung1_r4.py:5` ("local, gitignored").
- **What's wrong:** `git ls-files` shows **0 tracked files** in each of those three dirs, versus 24 on disk in each (72 raw artifacts total). Only the derived `runs/rung{1-r4,2-r4,2-reasoning}-{confirm,null}.json` summaries are committed. The program's own reproducibility gate is "can results be regenerated from committed code + documented parameters?" For these three rungs, an external party with a fresh clone **cannot** — the bootstrap inputs are absent, and DeepSeek generation is not deterministically re-obtainable. I verified them only because the raws exist in this working copy. By contrast rung-0 v2 (`runs/rung0-v2-*.json`) and insulation (`runs/insulation/*.json`) raws **are** committed and fully reproducible.
- **Evidence:** `git ls-files whitespace_1/runs/rung1-r4/ | wc -l` → 0; disk → 24. Summaries match docs exactly (below).
- **Mitigation:** the size rationale (full 1536-d embeddings) is documented in `.gitignore`; summaries are committed and I confirmed them bit-exact against the on-disk raws. Not concealment — a size tradeoff — but it means 3/5 headline verdicts rest on uncommitted inputs.
- **Confidence:** CONFIRMED.

### [MEDIUM] The rung-0 headline is procedure-dependent; "reasoning collapses more than output" reverses under the `decisions` skeleton
- **Claim affected:** RUNG 0 "strategy +27% ▸ output +17% ▸ decisions +10%; decisions runs the other way."
- **File:** `docs/ws1-oss-rung0-v2-prereg.md:169-176`; `experiments/pool_rung0_v2_seeds.py:104,137-141`; `src/whitespace1/rung0_v2.py:35-36` (`SKELETON_PROCEDURES`, `PRIMARY_PROCEDURE`).
- **What's wrong (nuance, not defect):** the primary estimand (registered `strategy` skeleton, I1) gives gap **+9.9%** [+6.3,+13.9], all three instruments agreeing (I2 +11.5%, I3 +5.1%). But the *second registered* procedure `decisions` gives gap **−6.8%** [−9.0,−4.5] — reasoning declining *less* than output, and that CI **excludes 0 on the negative side**. So "reasoning homogenizes more than output" is true for one of two pre-registered skeleton granularities and *significantly false* for the other. Both were registered pre-run (verified: `rung0_v2.py` defines both procedures; prereg §"skeleton extraction" names "a terse 'strategy abstract' and a 'decision-point list'"), and the doc **does** disclose the reversal and reframes it as "the collapse is STRATEGIC, not total." This is honest, but a paper must carry the qualifier — the bare "+27/+17/+10 ordering" invites over-reading a procedure-specific effect as a general one.
- **Confidence:** CONFIRMED (artifact-backed; reproduced +9.9%/+27.1%/+17.1%/−6.8% exactly).

### [LOW] `pool_rung0_v2_seeds.py` mislabels the `decisions` CI as "includes 0" when it excludes 0
- **File:** `experiments/pool_rung0_v2_seeds.py:140` — `excl = "excludes 0" if lo > 0 else "includes 0"`.
- **What's wrong:** the label only tests `lo > 0`, so a CI entirely *below* zero ([−9.0%,−4.5%], the decisions row) prints "**includes 0**." It does not — it excludes 0 negatively (a significant reverse gap). The committed docs interpret it correctly as a real opposite-signed effect; only the script's console output is wrong. Cosmetic, but mildly ironic in an arm whose discipline is CI rigor, and it *understates* the decisions finding to a casual re-runner. (Line 81, the headline row, uses the same one-sided check but is safe there because that gap is positive.)
- **Confidence:** CONFIRMED.

### [LOW] Insulation prose ("both founding claims now unsupported") over-generalizes one operationalization
- **Claim affected:** INSULATION / Claim #17.
- **File:** `docs/ws1-insulation-prereg.md:83-96`; `experiments/run_insulation.py:36-45`.
- **What's wrong:** the fired test is a *single* operationalization — "isolated" = the **same 5 personas** on a separate catalog with different seeds (`ISO_SAMPLING=20260800+i` vs `FIELD_SAMPLING=20260723+i`), equal group size (5v5), adoption = echo by a conformity-biased field, n=8 run-ids, CI [−0.165,+0.123]. The prereg is well-scoped and explicitly defers the group-**size** dimension (the "small" in "small insulated groups") to "a registered secondary, not the primary." But the results prose rounds up to "both program founding claims are now empirically unsupported on their own tests." The size axis was never run, and this is one substrate/definition; the clean null is real *for what it tested*, which is narrower than the summary sentence implies. The wide-CI caveat is, to their credit, stated.
- **Confidence:** CONFIRMED.

### [LOW] Doc/code drift — stale `todo.md`; misleading `analyze_rung2.py` docstring
- **Files:** `tasks/todo.md:5` still says "chapter 2 is designed but **not built**" though rungs 0–2b + insulation all fired; `experiments/analyze_rung2.py:8-9` module docstring asserts the headline as "V_reason collapses while V_output holds -> measurement artifact" — the *opposite* of the actual verdict (neither collapses / null deepens). The verdict *logic* (lines 55-74) is correct and branches over all cases; only the header prose is stale. No result affected.
- **Confidence:** CONFIRMED.

### [LOW] Hierarchical bootstrap holds the 2 topics fixed (inherited from polyphony) — conservative, not a defect
- **Claim affected:** RUNG 1 / 2a / 2b CIs.
- **File:** `src/whitespace1/rung1_confirm.py:174-181,217-240`.
- **What's right:** the bootstrap correctly resamples the two units that matter — **run-ids within topic** (`_resample_prepared`, 4 per topic → 8) and **persona indices within round** (`rng.integers(0, gram.shape[0], size=5)`, same indices across the paired pop/uni/abl conditions). Rounds are the regression x-axis (correctly not resampled). This is a faithful two-level cluster bootstrap and a verbatim port of polyphony's `walk_r4_confirm.py:199-344`.
- **The only limitation:** with 2 topics you cannot bootstrap the topic level, so between-topic variance is uncaptured — which biases toward *narrower* CIs. This is conservative-safe for every verdict actually drawn here: all rung-1/2 collapse CIs straddle zero and are read as **"no collapse,"** so any understatement would only make the null *more* secure, never manufacture a collapse. It does **not** understate uncertainty in a way that threatens a conclusion.
- **Confidence:** CONFIRMED.

---

## REPRODUCTION LOG

Environment: `uv sync --extra dev` (clean). All runs zero-spend, deterministic, seeds pinned.

| what I ran | result | vs committed doc/artifact |
|---|---|---|
| `uv run pytest -q` | **100 passed** in 70s (token-free mocks) | — |
| `ruff check src/ tests/` | **All checks passed** | validation gate ✓ |
| `mypy src/ --strict` | **Success, no issues (15 files)** | validation gate ✓ |
| `pool_rung0_v2_seeds.py` | guarded gap **+9.9%** [+6.3,+13.9] excl 0; reason +27.1%, output +17.1%; I2 +11.5%, I3 +5.1%; decisions **−6.8%** [−9.0,−4.5] | matches `ws1-oss-rung0-v2-prereg.md` exactly |
| `analyze_rung1_r4.py` | uptake +0.04197 (lo +0.02106); feedback +0.00627 (lo +0.00108); popV −0.00275 (up +0.00604); pop−abl −0.00048; pop−uni −0.00481; **no collapse** | matches `rung1-r4-confirm.json` + doc table exactly |
| `analyze_rung1_null.py` | replay err 2.22e-16; obs pop−uni +0.00627; null pop−het +0.01456 = **232%**; pop-vs-null raw excess −0.00301 **p=0.1869**, norm excess −0.07206 p=0.0035 → **SAMPLING ARTIFACT** | matches `rung1-r4-null.json` + doc exactly |
| `analyze_rung2.py` | uptake +0.03444 (live); V_output −0.00096 (up +0.00802); V_reason +0.00262 (up +0.00926); **neither collapses → null deepens** | matches `rung2-r4-confirm.json` + doc exactly |
| `analyze_rung2_reasoning.py` | uptake **+0.00947 (lo −0.00354) NOT live**; V_reason +0.00048, V_output +0.00298 → **unreadable** | matches `rung2-reasoning-confirm.json` + doc exactly |
| `analyze_insulation.py` | live +0.0643; iso 2.6444, conn 2.6616; gap **−0.0172** [−0.1647,+0.1227]; null p=0.6571 → **NOT supported** | matches `insulation-confirm.json` + doc exactly |

Every committed summary re-derived **byte-identically** (git tree stayed clean after re-runs). Day-0 gate
also checks out (`rung1-day0-deepseek.json`: diversity 0.5816, shift +0.0657, both pass — matches doc).

**Could not reproduce:** nothing token-free was blocked. The underlying *generation* of rung-1/2a/2b raw
artifacts is NOT INDEPENDENTLY REPRODUCED (requires paid DeepSeek + those raws are gitignored) — but the
full analysis pipeline on the extant raws is bit-exact.

---

## PROVENANCE CHECK

**`catalog.py` — VERBATIM IN MECHANISM.** `diff` vs `polyphony/src/polyphony/catalog.py` shows only:
(a) an added "Ported verbatim" docstring, (b) whitespace/one-line-signature reformatting, (c) one
`return cast(FloatVector, vector / norm)` type-annotation cast. **Zero behavioral difference.** Claim holds.

**`rung1_null.py` — VERBATIM IN MECHANISM.** `diff` vs `polyphony/src/polyphony/null_p_top4.py` shows:
(a) heavy docstring/comment trimming (cosmetic), (b) a *dropped reporting feature* — `ArmSummary.raw_band`/
`normalized_band` and the `_summarize(..., band=)` arg were removed (affects nothing in the p-values or
comparisons), (c) `load_runs` glob `r4-confirm-*.json` → `*.json` and condition fallback adapted to the new
filename convention, (d) **one registered parameter change**: null seed `20260722` → `20260725`. That seed
is registered in `ws1-oss-rung1-prereg.md:110` ("null 20260725"), i.e. a documented change, not drift. The
simulation math (`simulate`, `NullMode`, `MATCHED_NULL`, `compare_to_null`) is identical. Claim holds.

**Bonus — `rung1_confirm.py`** (claimed ported from `walk_r4_confirm.py`): the bootstrap/estimand/threshold
logic is a faithful port; the only additions are `v_embeddings_key`/`uptake_embeddings_key` params (to switch
the collapse channel for rung 2, defaults preserve rung-1 behavior) and `topic_id` vs `topic` field rename
(documented in the docstring). No mechanism drift.

**Is the P_top4 null genuinely MATCHED?** YES. `MATCHED_NULL` pairs the popularity arm with `NullMode.POPULARITY`
= popularity-weighted sampling + catalog growth + echo magnitudes resampled from the *pooled observed*
similarities, removing **only** the agents' content-specific echo targeting. Sampling rule, growth, and echo-
magnitude distribution are preserved identically; the positive-control `replay_run` validates the process model
to 2.2e-16. The null reproduces **232%** of the observed pop−uniform slope and the popularity arm sits *at/below*
its matched null (raw p=0.19, normalized excess −0.072) — so the arm concludes its own concentration is an
artifact. This is the *correct, conservative* use of a matched null (it refutes the arm's own Gate-2), the exact
opposite of the WS2 `ref_gini` failure. **No matched-null vulnerability.**

**Cross-substrate replication provenance (failure-mode #3 check):** the rung-1 claim replicates polyphony's
*corrected* R4 finding — live actuator + output-null + concentration-is-artifact — and `polyphony/src/polyphony/
null_p_top4.py` **is committed** (commit `93743e3`, "Add matched null for R4's P_top4 concentration statistic").
The *withdrawn* "R4 reproduces WS2 decoupling" capstone is explicitly disavowed in `ws1-oss-reasoning-arm.md:30-39`.
So the replication targets a genuinely-in-record source finding. **No provenance fabrication.** Personas
(`stimuli.ROLES`, 5 names) and the 8-item seed catalog were spot-checked verbatim against polyphony
(`persona.py`, `day0_r3.py` — "Decision Ledger: retain the evidence, owner, and reversal trigger behind each
ensemble…" matches).

---

## WHAT SURVIVES CLEANLY

- **All five headline verdicts reproduce bit-exactly** from committed code + on-disk artifacts; every doc number
  matches its committed summary JSON. No doc-vs-artifact numeric mismatch found.
- **The three fatal program failure-modes are absent** from the fired work: the matched null is genuine and
  *kills the arm's own* concentration; there is no uncertainty-free crossover (the λ* crossover was explicitly
  retired to a "threshold" in `ws1-oss-reasoning-arm.md:84-109`, and Rung 3 was never run); the cross-substrate
  replication points at polyphony's actually-committed corrected record.
- **Ported code is verbatim in mechanism** (`catalog.py`, `rung1_null.py`, `rung1_confirm.py`); the one
  parameter change (null seed) is registered.
- **The hierarchical bootstrap is correctly specified** (run-ids within topic + paired persona indices within
  round) and errs conservative for the null conclusions drawn.
- **Validation gates all green:** 100 tests pass, ruff clean, mypy --strict clean, `make check` is token-free.
- **Honest-null discipline is real:** rung-0's binary gate replicated only 2/3 and the doc says so and pivots to
  the continuous estimand; rung-2b's dead actuator is reported as "unreadable," not spun as resistance; the
  spend ledger and its own defects are logged candidly.
