# AI-Collapse Bridge — the plan (tools + experiment)

**Goal.** Turn the Originality C/V theory + WS2 metrics into **reusable tools**, then use them to
test whether the theory (validated on 24M human papers) **predicts diversity collapse in an LLM
self-training loop**. This is the keystone that connects the human-science program to AI, and the
shared instrument for the whole five-project diversity-collapse portfolio (Originality, synthoracle,
ate-series, opensource_x, crit-thinking).

**Split.** Tools are built **here** (in `originality/`, as versioned packages — per the
whitespace-independence rule that shared utilities graduate to a package with tests). The
**experiment lives in a separate repo** that depends on those packages via pinned installs.

---

## Part A — the two tools (built here)

### A1. `diversity-metrics` — the WS2 measurement suite, packaged

A domain-agnostic library: give it vectors (or text + an embedder) and reference/token sets, get
back diversity + concentration metrics. **Same code for human papers and AI generations** — that
continuity is the scientific point.

- **Source** (extract + clean, don't rewrite): `whitespace_2/src/whitespace2/` →
  `semantic_metrics.py`, `canonical_metrics.py`, `divergence.py`, `v_extension.py`
  (`reference_atypicality`, `cd_index`).
- **Interface:**
  - `semantic_diversity(X: np.ndarray) -> {pairwise_cosine_mean, effective_dim, cluster_entropy, ...}`
  - `concentration(counts | refs) -> {gini, top_k_share, ...}`  (the `H`↑ analog)
  - `reference_atypicality(refs) -> np.ndarray`  (embedding-free structural novelty)
  - `distinct_n(texts) / self_bleu(texts)`  (standard generation-diversity, add for legibility)
  - `embed(texts, model="scincl"|"specter2"|"general") -> np.ndarray`  (optional wrapper)
- **Package:** `packages/diversity_metrics/` with `pyproject.toml`, `src/`, `tests/` (port the
  existing WS2 tests). Installable: `pip install git+…#subdirectory=packages/diversity_metrics`.
- **Discipline:** pin metric definitions (a version tag) so any result — human or model — is
  reproducible against the identical implementation.

### A2. `cv-predictor` — the WS3 C/V theory, as a callable + hosted service

Given a system's parameters, return the crossover and regime.

- **Source:** `whitespace_3/src/whitespace3/` → `analytics.py` (`crossover_lambda`,
  `v_star_meanfield`, carrier-survival), `conformity.py` (the `λ*` locator).
- **Interface:**
  - `predict(SystemParams) -> RegimeForecast`
    - `SystemParams = {n, kappa, epsilon, f, topology?}` (scale, conformity, innovation, fidelity)
    - `RegimeForecast = {lambda_star, regime: "V-favouring" | "C-favouring", v_trajectory, confidence}`
    - Backed by the **mean-field analytics** → milliseconds, ~free. This is the fast path.
  - `calibrate(SystemParams) -> SimResult` — runs the full `channel.run`/`subfield.run` sim
    (O(N²), the heavy path) to validate/refine the mean-field prediction. Runs on Modal.
- **Modal app `ws3-cv-predictor`:** `@modal.web_endpoint` for `predict` (fast, serverless,
  scales-to-zero, negligible cost) + `@app.function` for `calibrate` (pay-per-run sim). The
  at-scale sweep already ran the sim on Modal, so this reuses existing infra.
- **Package:** `packages/cv_predictor/` + `tests/` (assert `predict` matches `analytics` and the
  known anchors, e.g. `λ*≈0.09`).

### A3. Consumption

The separate AI-repo installs both packages (pinned to a commit) and calls
`diversity_metrics.*` on generations + `cv_predictor.predict(...)` for the forecast. Clean
contract, no ambient coupling.

---

## Part B — the experiment (separate repo)

### B1. Use-case selection — recursive generative self-training (model collapse) on research abstracts

Ranked by **likelihood-to-show-collapse × budget × theory-fit × portfolio-tie**:

| candidate | collapse likelihood | κ lever | why (not) the pick |
|---|---|---|---|
| **① Self-training on abstracts (WINNER)** | **highest** (Shumailov 2024 — proven, robust) | synthetic-recursion fraction (replace↔accumulate) | cheap (LoRA, no labels); κ maps cleanly to conformity with a **known crossover** (accumulate vs replace); domain = Originality's own, WS2 metrics built for it, 24M human study is the direct prior |
| ② RLHF/DPO mode-collapse (opensource_x) | high (RLHF↓diversity, documented) | KL-coefficient / reward pressure | strong **second experiment** — reuses the BT harness, shows the theory spans a *second* collapse mechanism; slightly more moving parts |
| ③ crit-thinking generation-diversity | static homogenization, not a loop | engagement mode | contributes DeepSeek infra + diversity metrics to ①, not a standalone collapse-over-rounds |
| ④ synthoracle (agent reasoning) | within-run, not a training loop | — | collapse is epistemic, not a generative-distribution loop; awkward fit |
| ⑤ ate (multi-agent) | population convergence | info symmetry | different mechanism (WS1 direction), more expensive |

**The pick: ①.** It maximizes the chance of a clean result, it's the canonical + most legible AI
setting, and it makes the narrative continuous: *AI-generated science collapses in diversity the
way the human canon concentrates — and the C/V theory forecasts it.* Hold ② in reserve as the
"theory generalizes across collapse mechanisms" follow-up.

### B2. What the training is

Recursive **unsupervised LoRA fine-tuning** of a small LM to generate CS research abstracts. Each
round trains on a mix of *real* seed abstracts and the model's *own* prior-round generations; over
rounds, the generated distribution narrows. It is **not** RLHF/preference training — plain causal-LM
fine-tuning on text, which keeps it cheap and label-free.

- **Model:** DeepSeek-small — `DeepSeek-R1-Distill-Qwen-1.5B` (small ⇒ fast, cheap, collapses
  legibly). Upsize to 7B only as a robustness check if budget allows. (From the crit-thinking stack.)
- **Round loop (per κ):**
  - `t=0`: LoRA-fine-tune base on the real seed → `M_0`.
  - `t≥1`: generate `G` abstracts from `M_{t-1}`; build round-`t` data = `κ`·(synthetic pool) +
    `(1−κ)`·(real seed); LoRA-fine-tune **from base** on that mix → `M_t`. (Fresh-from-base isolates
    the *data-composition* effect; a continued-from-`M_{t-1}` variant compounds collapse faster —
    spec both, run fresh-from-base as primary.)
  - Repeat `T ≈ 8–10` rounds.

### B3. How to construct the data

- **Real seed (you already own it):** sample `K ≈ 5–10K` real CS abstracts from the WS2 **24M v3
  population** (`section0-population-v3.parquet` on the `ws2-section0` Modal Volume). Reuse the §0
  filter. This is the ground-truth reference distribution — a major asset most model-collapse
  studies lack.
- **Synthetic pool:** each round's `G ≈ 5–10K` generations (prompt = a short "write a CS paper
  abstract about …" template seeded by a held-out real title/topic, so topical coverage is
  controlled and only *diversity within topic* is measured).
- **κ** = synthetic fraction of each round's training set. **No labels** — it's LM fine-tuning on text.

### B4. The κ-sweep — the crossover test

Run the loop at `κ ∈ {0.0, 0.25, 0.5, 0.75, 1.0}`:
- `κ=1.0` (full replace): expect collapse.
- `κ=0.0` (all-real each round): control — must **not** collapse (validates the pipeline).
- intermediate: locate the **crossover** — the κ above which diversity collapses.

### B5. Measurement — via `diversity-metrics`, every round on the generations

- **Diversity:** semantic (pairwise cosine, effective dim, cluster entropy on embeddings),
  `distinct-n`, self-BLEU.
- **Concentration (the `H`↑ analog):** cluster the generation embeddings (KMeans, fixed K) and
  track **cluster-occupancy Gini** over rounds — do generations concentrate into fewer clusters?
- **Quality control:** perplexity of generations vs. a held-out real set (distinguish *collapse*
  from *degeneration into gibberish*).
- Plot every metric's trajectory over rounds, per κ.

### B6. The theory-test — via `cv-predictor`

- Map the loop to C/V params: `κ` = synthetic fraction (clean); `n` = generation-set size / source
  diversity; `ε` = generation temperature / novelty rate; `f` = fidelity (model capacity × epochs).
  *This mapping is itself a contribution — flag it as approximate.*
- `cv_predictor.predict(params)` → predicted `λ*`, regime, trajectory.
- **Compare** predicted crossover vs observed (the κ where diversity collapses).
- **Fast vs. ground-truth (learned during the package build):** `predict()` is the *mean-field*
  approximation — a fast directional regime indicator, accurate at low fidelity (`f≈0.15 → λ*≈0.08`)
  but it *undershoots* at high fidelity (`f=0.6 → λ*≈0`, where the persistence saturates), whereas
  the **simulation** gives the vivid `λ*≈0.09`. So: use `predict()` for the **regime-ordering** gate
  (H3 primary — which κ collapse vs sustain, robust to the approximation), and the Modal
  **`calibrate()`** sim path for the **quantitative `λ*`** gate (H3 stretch). Don't stake the exact-λ*
  comparison on the fast predictor.

### B7. Pre-registered hypotheses + gates

- **H1 (reliable):** recursive self-training collapses all diversity metrics at high κ.
- **H2:** a **crossover** in κ exists (sustain ↔ collapse).
- **H3 (the theory-test):** `cv-predictor` forecasts it. *Primary gate:* regime-**ordering**
  correct (which κ collapse vs sustain) + a qualitative crossover. *Stretch gate:* quantitative
  `λ*` match within tolerance. *Honest-null:* mis-forecast ⇒ a **calibration result** (where the
  human-tuned theory needs adjustment for AI) — still publishable.
- **H4 (the duality):** as diversity collapses, **concentration rises** (cluster-Gini↑) — the AI
  analog of WS2's `H`↑ alongside frontier fragmentation.

### B8. Cost model (target ≤ $240 Modal)

- LoRA on 1.5B ≈ 15 min on an A10 (~$1–2/round). `5 κ × 8 rounds = 40` fine-tunes ≈ **$40–80**.
- Generation: `40 × ~8K` samples inference ≈ **$10–30**.
- `cv-predictor` hosting: negligible (serverless predict; sim `calibrate` a handful of runs).
- **Total ≈ $60–120**, leaving headroom for one 7B robustness upsize or a second κ point.

### B9. Risks + mitigations

- **Too-fast / degenerate collapse** (gibberish before the trajectory is visible): control LoRA
  (few epochs, low LR), moderate generation temperature, sample early rounds finely; the perplexity
  metric flags degeneration vs. genuine diversity-collapse.
- **No crossover** (collapses at all κ, or never): the accumulate-vs-replace distinction reliably
  gives one — ensure `κ=0` truly injects *fresh* real data each round; widen the κ grid if needed.
- **Loose C/V mapping** (B6): lean on the *regime-ordering* gate, not exact `λ*`; report the
  mapping honestly as a research question.
- **Small-model quirks:** upsize to 7B if 1.5B is too degenerate (budget permitting).

---

## Part C — narrative payoff

*"I built a theory of when knowledge-producing systems collapse toward homogeneity, validated it on
24M scientific papers, packaged it as a hosted predictor, and showed it forecasts diversity collapse
in LLM self-training — one instrument scoring collapse risk across a five-project program spanning
human science, LLM agents, multi-agent systems, RLHF, and generation."*

The predictor + metrics then retro-score the other four (synthoracle context-cementing, ate
information-symmetry, opensource_x reward-pressure, crit-thinking agreeable-bias) as κ-analogues —
the program as one system, not five PDFs.

---

## Part D — sequencing

1. **(Here) Build the two packages** — `diversity_metrics` + `cv_predictor` + the `ws3-cv-predictor`
   Modal endpoint, with tests. *This is the reusable spine and the first build step.*
2. **(New repo) Scaffold** the self-training loop; wire in both packages.
3. **Pilot:** `κ=1.0`, `T=5`, DeepSeek-1.5B — confirm collapse + that the metrics move + the
   predictor returns a forecast. (~$10.)
4. **Full κ-sweep + theory-test** (B4–B7).
5. **Writeup** + fold into the program research-statement (Part C).
