# Diversity Thermostat — OpenAI Build Week (Developer Tools) blueprint

**Product-first reframe (2026-07-13).** Build Week judges a **product** — equally-weighted on
Technological Implementation (Codex use), **Design** ("a complete, coherent product experience — *not
just a technical proof of concept*"), **Potential Impact** ("a credible, specific case for solving a
real problem for a real audience"), and Quality of Idea. So this leads with the **tool**; the science
(the C/V theory + the multi-agent diversity-collapse study) is the **engine and credibility**, not the
deliverable. The rigorous validation stays in the research/paper track. *(Correction to the earlier
draft: there is no "efficiency" judging axis — token-efficiency is a supporting Implementation point,
not the headline.)*

## The product

**What:** a real-time **monitor + preventer of diversity collapse** in multi-agent GPT-5.6 systems. It
runs (or attaches to) an agent ensemble, measures its collective-output diversity live, **forecasts
when it's about to collapse into sameness**, and **auto-triggers interventions** (exposure diversity,
agent insulation) to keep it varied.
**Problem (real, specific):** teams building agentic workflows / multi-agent systems / synthetic-data
loops **silently lose output diversity over time** (homogenization / mode-collapse) — degrading quality,
coverage, and creativity — with no principled tool to detect or prevent it.
**Audience:** developers building **agentic workflows** (a named use-case of the Developer Tools track).
**Track:** Developer Tools. **Working name:** "the diversity thermostat" — pick a product name (e.g.
*Chorus*, *Polyphony*, *Bellwether*).

## How it hits the four judging criteria

- **Technological Implementation (Codex):** built with Codex (session logs as evidence); a non-trivial
  real-time loop — a multi-agent GPT-5.6 ensemble + live diversity measurement + a forecasting
  controller. Model/effort tiering + a token meter show skillful, efficient use.
- **Design:** a coherent, **hosted, runnable** product — a live dashboard judges can drive (sliders, a
  collapse trajectory, an intervention toggle that *visibly recovers* diversity), not a local PoC.
- **Potential Impact:** a specific real problem (silent diversity collapse degrading multi-agent /
  self-training systems) for a real audience (agent-system devs); the demo shows it **detecting AND
  preventing** collapse.
- **Quality of Idea:** novel — a diversity-collapse "thermostat" grounded in a theory validated on 24M
  papers; differs from existing dev tools, which don't measure or prevent collective homogenization.

## The engine (science as credibility, underneath)

- **Endogenous collapse (the honest mechanism):** persona-conditioned GPT-5.6 agents attend to a shared
  popularity-weighted catalog and **homogenize because the model drifts toward popular priors** (no
  imposed filter). The **catalog-in-prompt-vs-not ablation** proves it's the LLM's doing — this is what
  makes the tool a real phenomenon, not a definitional artifact.
- **Forecast:** `cv_predictor` maps the loop's conditioning strength to a crossover and flags when the
  ensemble is approaching collapse (directional/regime-ordering — validated in the step-0 audit;
  `calibrate()` for exact λ*).
- **Monitor:** `diversity_metrics` (effective dim, pairwise cosine, cluster entropy) on the ensemble's
  output embeddings, live and cheap (no LLM-judge calls).
- **Interventions:** exposure diversity (uniform vs popularity-weighted catalog), agent insulation
  (shield a subgroup) — the "prevent" half.
- *The rigorous validation (phase diagram, the causal ablation as a pre-registered result, the
  statistical plan with seeds/CIs/refute criteria) is the **portfolio/paper track**, not the hackathon
  submission. The hackathon needs the working tool + a credible demonstration.*

## Build ladder — crawl → walk → run → sprint (by TIME-RISK)

- **CRAWL (~½ day).** The skeleton: a multi-agent GPT-5.6 loop + live `diversity_metrics` monitoring +
  the dashboard, on a **mock** agent then a real one; token-free harness + the ~$0.50 **kill-test** (is
  `minimal`-effort output diverse? does catalog-conditioning actually move outputs?).
- **WALK (~1–2 days) — the MVP = a complete submission.** The monitor **shows diversity collapsing** in
  a real GPT-5.6 ensemble + a **manual intervention** that recovers it, **hosted + testable**. Bank this
  before climbing — it is already a valid Developer-Tools entry.
- **RUN (~2–3 days).** The **auto** thermostat (`cv_predictor` forecasts → auto-intervene *before*
  collapse) + the intervention suite + demo polish; the catalog-ablation shown as the "why it works."
- **SPRINT (reach).** Hosting hardening, a 2nd use-case (a synthetic-data self-training loop), the
  autonomous-Codex-build + utilization story, the demo video.

## Hackathon requirements checklist

- **Register** on openai.devpost.com (Registration + Submission both open Jul 13).
- **$100 credits** requested (deadline Jul 17, 12pm PT; use by Jul 31). **API-key auth — no ChatGPT
  subscription needed** (platform account + key; credits apply there; Codex authenticates with the key).
- **Repo** — see "Repo decision"; if private, share with `testing@devpost.com` +
  `build-week-event@openai.com`.
- **Hosted demo** (a Dev-Tools *requirement* — judges must test **without rebuilding**): a public
  dashboard URL (Streamlit Cloud / a Modal web endpoint).
- **<3-min YouTube demo video** (audio; what you built + how you used Codex and GPT-5.6).
- **README:** how you collaborated with Codex (where it accelerated you, your key decisions) + **prior
  vs. new work** delineation (the packages are prior; the tool is in-window).
- **`/feedback` Codex Session ID** for the thread where the core functionality was built.

## Repo decision (LOCKED) — a separate tool repo; WS2/WS3 are never shared

Build in a **separate, product-named tool repo**. The **only** things ever shared with judges are
(a) this repo and (b) the hosted demo URL. **WS2, WS3, the papers, and the data stay fully private** —
never in this repo, never referenced, never shared.

**The bare-minimum dependency.** The tool needs `diversity_metrics` + `cv_predictor` — the *metric +
predictor* code, **not** the program. **Bundle them into the tool repo as vendored prior-work deps**:
either copy the two (small) packages in, or vendor only the ~8 functions the tool actually uses
(`effective_dimensionality`, `mean_pairwise_cosine_distance`, `cluster_entropy`, `gini`;
`v_star_meanfield` / `branching_survival` / `predict`), each with a provenance header. This makes the
shared repo **self-contained** (judges can install and run it) while exposing **only the tool + its
metric/predictor deps** — nothing of WS2/WS3. Document them as prior work in the README (the prior-vs-new
delineation the rules require); the NEW, in-window work is the thermostat built around them.
**Do NOT publish the packages to PyPI** — bundling into the private-shared repo is *less* exposing than
publishing, and it's all the judges need (this also honors "build conviction before publishing").

**What each shared surface reveals:** the repo → the tool code + the metric/predictor deps (no program);
the hosted demo → the running tool's behavior (no code/program); the video + README → the tool. **WS2/WS3
never leave your private control.**

## Model / effort + budget

- **Science calls:** `gpt-5.6-luna` at `minimal` effort (cached persona prefix −90%, Batch −50%) — the
  whole run is **~$1–50**. Embeddings: `text-embedding-3-small`.
- **Codex coding sessions:** **Terra / `medium`** default; **Sol / `high`** for hard/stuck (the
  `cv_predictor`/WS3 integration, gnarly debugging); **Luna / `low`** mechanical. `codex exec --model
  <tier> --config model_reasoning_effort=<effort>`. **API-key auth** (hard budget cap; no subscription).

## Preservation + porting

This doc lives at `originality/docs/program/ws1-hackathon-plan.md` (research repo; a design doc, not
code). **On build day:** create the tool repo and port this in as its `CLAUDE.md` + the Codex
`Prompt.md`; the `Plan.md` milestones come from the build ladder + the checklist.

## Ready to leverage

- Repo/deps template: `canary/pyproject.toml`, `canary/src/canary/{measure,theory}.py`.
- Engine pieces: `originality/packages/{diversity_metrics,cv_predictor}`; the endogenous↔conditioning
  mapping + the imposed-filter baseline from `whitespace_3/src/whitespace3/channel.py`.
- Codex build + evidence: `codex exec --json` / SDK `Turn.usage`; `Prompt/Plan/Implement/Documentation.md`;
  `$CODEX_HOME/sessions` `token_count` (doubles as the required Codex evidence).

## Full science-first blueprint (for the paper/portfolio track)

The prior, science-first version of this plan (the rigorous experiment: endogenous causal test, the
phase-diagram theory-validation, the statistical plan, the crawl→walk→run→sprint *science* ladder,
the Codex autonomy/observability detail) is preserved in git history of this file (pre-2026-07-13).
Retrieve it with `git log --follow -p docs/program/ws1-hackathon-plan.md` if the paper track needs it.
