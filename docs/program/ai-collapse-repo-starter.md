# Canary — new-repo starter

> **Project: `canary`** — *an early-warning theory of diversity collapse in knowledge-producing
> systems, human and AI.* The name foregrounds the contribution: not that models collapse, but that
> a theory (the C/V predictor) forecasts *when* they do.
>
> **Copy this file into the new repo as `CLAUDE.md` (or `README.md`).** It is the self-contained
> onboarding doc: what the project is, why it exists, the exact experiment, the tools, the Modal
> setup, and the first thing to build.

---

## 0. One-paragraph pitch

Test whether the **C/V theory** — validated on 24M human research papers in the *Originality*
program — **predicts diversity collapse in an LLM self-training loop**. Recursively fine-tune a
small base LM on a mix of real + its own generated abstracts; measure the diversity/concentration
trajectory with the *same* metrics used on the human corpus; and check whether the theory's
**crossover** (the hosted `cv_predictor`) forecasts *which* recursion regimes collapse vs. sustain.
This is the keystone connecting a five-project diversity-collapse research program to AI.

## 1. Why this exists (portfolio context)

Five projects, one question — *when and why do knowledge-producing systems (human or AI) collapse
toward homogeneity, and what preserves diversity?*

| project | level | collapse finding |
|---|---|---|
| **Originality** (WS2/WS3) | human science | canon concentrates + frontier fragments; the **C/V theory** (complexity vs per-capita novelty diverge under scale + conformity κ) |
| **synthoracle** | single LLM agent | context-cementing → reasoning collapses to one causal narrative |
| **ate-series** | multi-agent | information symmetry → agents converge |
| **opensource_x** | RLHF | Goodhart mode-concentration; the diversity stakeholder is harmed |
| **crit-thinking** | generation | agreeable/plausible bias homogenizes defaults; critical engagement restores novelty |

**This repo is the bridge:** the human-validated theory → an AI collapse it predicts. The
frontier-lab framing is *"I built a theory of diversity collapse, validated it on 24M papers,
packaged it as a hosted predictor, and showed it forecasts model collapse in LLM self-training."*

## 2. The scientific question + pre-registered hypotheses

- **H1 (reliable):** recursive self-training collapses all diversity metrics at high κ.
- **H2:** a **crossover** in κ exists (sustain ↔ collapse), not monotone-everywhere.
- **H3 (the theory-test):** `cv_predictor` forecasts it. *Primary gate:* correct **regime-ordering**
  (which κ collapse vs sustain). *Stretch:* quantitative λ* match (use the **sim**, see §5). *Honest
  null:* mis-forecast ⇒ a calibration result — still publishable.
- **H4 (the duality):** as diversity collapses, **concentration rises** (cluster-Gini↑) — the AI
  echo of the human canon's `H`↑ alongside frontier fragmentation.

Pre-register these before running (the program's discipline: hypotheses + gates first).

## 3. Experiment design

### 3a. The loop (recursive self-training = model collapse, à la Shumailov 2024)

Per κ value:
- `t=0`: LoRA-fine-tune the **base** model on the real seed → `M_0`.
- `t≥1`: generate `G≈5–10k` abstracts from `M_{t-1}`; build round-`t` train set =
  `κ`·(synthetic pool) + `(1−κ)`·(real seed); LoRA-fine-tune **from base** on that mix → `M_t`.
  *(Fresh-from-base isolates the data-composition effect; a continued-from-`M_{t-1}` variant
  compounds collapse faster — run fresh-from-base as primary.)*
- Repeat `T≈8–10` rounds.

### 3b. κ-sweep (the crossover)

`κ ∈ {0.0, 0.25, 0.5, 0.75, 1.0}`: `κ=1.0` (full replace) → expect collapse; `κ=0.0` (all-real) →
control, must NOT collapse (validates the pipeline); intermediate → locate the crossover.

### 3c. Model choice — **small + base, not new + powerful**

You are picking an *experimental substrate*, not a product. The criteria invert the usual "best
model" instinct:
- **Small beats powerful** — collapse is faster/cleaner/cheaper on ~1.5B; 8B triples per-round cost;
  big MoEs (R2/V3.2/Kimi/ERNIE) are out of budget and irrelevant.
- **Base beats instruct/reasoning-tuned** — you generate *abstracts* and measure *semantic
  diversity*, not reasoning. Critically, **instruct/RLHF models are already partially
  mode-collapsed** (that's crit-thinking's agreeable-bias finding) — starting there conflates
  pre-existing alignment-collapse with recursion-induced collapse. A **base pretrained** small LM is
  the clean substrate.
- **Primary:** `Qwen2.5-1.5B` (base), `SmolLM2-1.7B`, or `Llama-3.2-1B`.
- **Robustness (≥2-family discipline):** run collapse on **two** families (e.g. Qwen-1.5B +
  Llama-1B) so it can't be dismissed as a model quirk.
- **Pilot de-risk:** confirm the loop + metrics on a classic (`Pythia-1.4B` / `GPT-2`) first — the
  collapse literature uses exactly these.
- *DeepSeek note:* R1 distills are reasoning-tuned (wrong domain) and the tie to crit-thinking (which
  used the big API V4 Pro, not a 1.5B) is thin — don't pay the premium for a weak narrative link.

### 3d. Data construction

- **Real seed (already owned):** sample `K≈5–10k` real CS abstracts from the Originality **24M v3
  population** — `section0-population-v3.parquet` on the Modal Volume **`ws2-section0`** (in the
  `gkartik` Modal workspace). Abstracts are stored as `abstract_inverted_index_json` (OpenAlex
  inverted index) — reconstruct to plain text (invert `{token: [positions]}` → ordered string).
  Reuse the §0 quality filter (score/length) already applied to that population.
- **Synthetic pool:** each round's `G` generations, prompted with a controlled template
  (`"Write the abstract of a computer-science paper about {topic}."`, topic seeded from a held-out
  real title) so topical coverage is fixed and you measure *diversity within topic*.
- **κ** = synthetic fraction of each round's training set. **No labels** — plain causal-LM fine-tuning.

## 4. The tools (from Originality `packages/`)

Two tested, pip-installable packages already built and gated (ruff + mypy-strict + tests green):

- **`diversity_metrics`** (numpy + scipy) — the WS2 metric suite:
  - `semantic`: `effective_dimensionality`, `mean_pairwise_cosine_distance`, `cluster_entropy`
  - `concentration`: `gini`, `top_k_share`
  - `novelty`: `reference_atypicality`, `cd_index` (+ `cd_index_csr` in `novelty_sparse`)
  - `divergence`: `ols_trend`, `permutation_slope_test`, `standardized_effect`
- **`cv_predictor`** (numpy; `modal` optional) — the WS3 C/V theory:
  - `predict(SystemParams) → RegimeForecast{lambda_star, regime, slope_at_lam, v_trajectory}` (fast,
    mean-field)
  - `modal_app.py`: `ws3-cv-predictor` (a `predict` web-endpoint + a `calibrate` sim stub)

### Install (Originality is a **private** repo)

Local dev — editable path installs (no auth):
```bash
pip install -e /Users/kartikganapathi/Documents/Personal/random_projects/originality/packages/diversity_metrics
pip install -e /Users/kartikganapathi/Documents/Personal/random_projects/originality/packages/cv_predictor[modal]
```
(SSH git-pin also works: `pip install "git+ssh://git@github.com/kar-ganap/originality.git#subdirectory=packages/diversity_metrics"`.)

### Usage
```python
import numpy as np
from diversity_metrics.semantic import effective_dimensionality, mean_pairwise_cosine_distance, cluster_entropy
from diversity_metrics.concentration import gini
from cv_predictor import SystemParams, predict

X = embed(generations)                          # (N, D) sentence embeddings of a round's abstracts
div = {"eff_dim": effective_dimensionality(X),
       "pairwise_cos": mean_pairwise_cosine_distance(X, max_sample=2000, seed=0)}
# concentration (the H↑ analog): cluster the embeddings, Gini of cluster occupancy
labels = kmeans_fit_predict(X, k=50)
conc = gini(np.bincount(labels, minlength=50))

fc = predict(SystemParams(lam=kappa_as_lambda, epsilon=gen_temp, f=fidelity))
print(fc.regime, fc.lambda_star)                # "V-favouring"/"C-favouring", the crossover
```

## 5. Measurement + the theory-test

Each round, on the generations: `effective_dimensionality`, `mean_pairwise_cosine_distance`,
`cluster_entropy`, `distinct-n`/`self-BLEU`, cluster-occupancy `gini` (concentration), and
**perplexity vs. a held-out real set** (to tell *collapse* from *degeneration into gibberish*). Plot
every metric's trajectory over rounds, per κ.

**Theory-test.** Map the loop to C/V params — `κ`→conformity `lam`, `ε`→generation temperature,
`f`→fidelity (capacity×epochs); this mapping is itself a contribution, so flag it as approximate.

> **`predict()` vs `calibrate()` — important.** `cv_predictor.predict()` is the **mean-field**
> approximation: a fast, directional regime indicator, accurate at low fidelity (`f≈0.15 → λ*≈0.08`)
> but it *undershoots* at high fidelity (`f=0.6 → λ*≈0`, persistence saturates), whereas the
> **simulation** gives the vivid `λ*≈0.09`. So use **`predict()` for the regime-ordering gate (H3
> primary)** and the Modal **`calibrate()` sim path for the quantitative λ* (H3 stretch)**. Don't
> stake the exact-λ* comparison on the fast predictor.

## 6. Modal setup

The experiment runs on Modal. **Do not pip-install from the private Originality repo on Modal** —
ship your own package source into the image the way WS2 did with `add_local_python_source`; only the
third-party deps go through `pip_install`:

```python
image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("numpy>=1.24", "scipy>=1.11", "scikit-learn",
                 "torch", "transformers", "peft", "accelerate", "datasets", "sentence-transformers")
    .add_local_python_source("diversity_metrics", "cv_predictor")   # your packages (editable-installed locally)
)
```
For this to resolve, the two packages must be importable in your *local* env (the `pip install -e`
above does that). The seed data lives on the existing `ws2-section0` Volume — mount it read-only:
`volumes={"/pop": modal.Volume.from_name("ws2-section0")}`. LoRA fine-tuning wants a GPU
(A10/A100); generation + metrics are cheap.

## 7. Cost model (target ≤ $240 Modal)

- LoRA on 1.5B ≈ 15 min/round on an A10 (~$1–2). `5 κ × 8 rounds ≈ 40` fine-tunes ≈ **$40–80**.
- Generation: `40 × ~8k` samples ≈ **$10–30**. `cv_predictor` hosting ≈ negligible.
- **Total ≈ $60–120**, leaving headroom for a second model family or a 7B robustness upsize.

## 8. Risks + mitigations

- **Too-fast / degenerate collapse** (gibberish before the trajectory is visible): few epochs, low
  LR, moderate generation temp; sample early rounds finely; the perplexity metric flags degeneration
  vs. genuine diversity-collapse.
- **No crossover:** the accumulate-vs-replace distinction reliably gives one — ensure `κ=0` truly
  injects *fresh* real data each round; widen the κ grid if needed.
- **Loose C/V mapping:** lean on the regime-ordering gate, not exact λ*; report the mapping honestly.
- **Model quirk:** the ≥2-family run is the defense; upsize to 7B only if 1.5B is too degenerate.

## 9. Milestones (sequencing)

1. **Scaffold** the repo (§10); `pip install -e` the two Originality packages; pre-register H1–H4.
2. **Pilot** — `κ=1.0`, `T=5`, one small base model: confirm collapse, that `diversity_metrics`
   moves, and `cv_predictor.predict()` returns a forecast (~$10).
3. **Full κ-sweep** (§3b) + per-round metric trajectories.
4. **Theory-test** — regime-ordering via `predict()`, quantitative λ* via `calibrate()`.
5. **Second model family** (robustness) + the H4 concentration-duality check.
6. **Writeup** + fold into the program research-statement.

## 10. Suggested repo structure

```
canary/
├── CLAUDE.md                 # this doc
├── pyproject.toml            # deps + editable refs to the two originality packages
├── src/canary/
│   ├── data.py               # seed sampling + inverted-index→text + κ-mix builder
│   ├── loop.py               # the recursive LoRA fine-tune + generate loop
│   ├── measure.py            # per-round metric battery (wraps diversity_metrics)
│   ├── theory.py             # loop→SystemParams mapping + cv_predictor calls
│   └── modal_app.py          # the Modal image + GPU functions
├── experiments/              # pre-registered runs, phase-organized (pilot, sweep, robustness)
├── tests/
└── docs/                     # pre-registration, the paper draft
```

## 11. Ground rules (inherited from the Originality program)

Plan-first for non-trivial work; **TDD / pre-register hypotheses + gates before running**; report
nulls honestly (a mis-forecast is a result); pin seeds/model versions/snapshot; ≥2 model families
for robustness; small focused commits, phase branches. Track spend.

## 12. Pointers back to Originality

- **Full plan:** `originality/docs/program/ai-collapse-bridge-plan.md` (the source of this starter).
- **Packages:** `originality/packages/{diversity_metrics, cv_predictor}` (built, tested, provenance-tagged).
- **Seed data:** Modal Volume `ws2-section0`, `section0-population-v3.parquet` (24M CS+physics papers).
- **The theory:** `originality/whitespace_3/` (the C/V ABM); `docs/phases/phase-2-experiment-C-retro.md`
  for how the human-side landed (concentration `H`↑ ⊥ fragmentation atyp↑; CD-index window-fragile).
