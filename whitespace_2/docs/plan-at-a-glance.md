# Whitespace 2 — Plan at a Glance

**Purpose.** Visual summary of the Phase 0.1 scoping and Phase 0.2
pre-registration decisions. Complements — does not replace — the
authoritative plan in `phases/phase-0.1-plan.md`. Use this doc to:

- See the decision structure before diving into text
- Identify where a branch point lives before re-reading
- Explain the plan shape to a collaborator, reviewer, or future-you
- Check whether the plan's conditional logic still holds after updates

**Relationship to authoritative plan.** When `phases/phase-0.1-plan.md`
and this doc disagree, the plan wins. This doc is a derivative
representation; keep it in sync when the plan updates, but don't treat
it as the commitment.

**Diagrams use Mermaid** (renders on GitHub and in most Markdown
viewers). If a diagram seems stale after a plan update, regenerate.

---

## 1. Program context: three whitespaces, three epistemic layers

The originality research program has three whitespaces, each operating
on a distinct epistemic layer. Ws2 is one of three; its role in the
program determines what it must establish and what it can defer.

```mermaid
flowchart LR
    WS2["<b>WS2 — Empirical (observational)</b><br/>Establishes: phenomenon, quantitative<br/>constraints, mechanism-space narrowing<br/><br/>Cannot: identify counterfactuals"]
    WS3["<b>WS3 — Theoretical (formal)</b><br/>Establishes: plausible structural stories,<br/>identifiable parameters, regimes<br/><br/>Cannot: establish which story operates"]
    WS1["<b>WS1 — Simulation (interventional)</b><br/>Establishes: counterfactual trajectories,<br/>intervention effects<br/><br/>Cannot: validate sim structure vs. real science"]

    WS2 -->|anchors empirically| WS1
    WS3 -->|specifies structure| WS1
    WS2 -.->|constrains phenomenology| WS3
```

**Consequence for ws2's framing:** Methods and Discussion reserve
counterfactual claims for ws1. Ws2 documents the phenomenon and
narrows the space of plausible structural stories; it does not claim
to identify the true one. See `conceptual.md` §"Epistemic scope and
limits" for the full argument.

---

## 2. Phase and stage backbone

Phase 0 scoping produces the pre-registered plan; Stages 1–3 execute
it. Validation gates separate phases; gate failures trigger re-planning
rather than silent proceeding.

```mermaid
flowchart LR
    P01["<b>Phase 0.1</b><br/>Scoping + methodology<br/>commitments<br/>(3 weeks)"]
    P02["<b>Phase 0.2</b><br/>Pre-registration of<br/>divergence test<br/>(2 weeks)"]
    S1["<b>Stage 1 (Crawl)</b><br/>Data pull, disambig,<br/>demographic inference"]
    S2["<b>Stage 2 (Walk)</b><br/>Embedding + metrics<br/>+ primary tests"]
    S3["<b>Stage 3 (Run)</b><br/>Robustness, cross-field,<br/>mechanism, paper"]

    P01 -->|9 validation gates| G1{All gates<br/>pass?}
    G1 -->|yes| P02
    G1 -->|no| P01_replan[Re-plan Phase 0.1]
    P01_replan --> P01

    P02 --> S1
    S1 --> S2
    S2 --> S3

    S3 --> Done[(arXiv + peer-<br/>reviewed venue)]
```

**Phase 0.1 gate summary** (full list in plan §"Validation gates"):
pilot query returns expected data; abstract coverage workable;
classifier drift characterized; demographic inference coverage
characterized; disambiguation error spot-checked; field definitions
committed; retro written; literature review closed; drift-pilot
decision committed.

---

## 3. Drift-mitigation ladder (conditional branching)

Drift mitigation operates on two axes. Cross-architecture robustness
(Mitigation 2, cross-model replication) is always run; sophistication
axis (Flavor B, per-era fine-tune) is conditional on Stage 2 results.
Flavor A is conditional on the Phase 0.1 drift-pilot result.

```mermaid
flowchart TB
    Default["<b>Stage 2 DEFAULT (always run)</b><br/>• Mitigation 2: SPECTER2 + SciNCL + Qwen3-0.6B<br/>• Mitigation 4: Anchor-dim projection"]

    Pilot{"<b>Phase 0.1 drift-pilot</b><br/>Check 5c: 1970s era-match rate<br/>(100-abstract nearest-neighbor)"}

    FA["<b>Flavor A (Stage 3)</b><br/>Word2Vec per decade<br/>+ Procrustes alignment<br/>+ document aggregation"]
    Skip["Skip Flavor A"]

    Stage2["Stage 2 main run<br/>Tests I-IV on default stack"]

    CheckS2{"Stage 2 results:<br/>does drift remain<br/>material?"}

    FB["<b>Flavor B (Stage 3)</b><br/>Per-era fine-tuned SPECTER2<br/>+ anchor-paper Procrustes"]

    FC["<b>Flavor C (reserve)</b><br/>Dynamic embedding models<br/>(Bamler-Mandt, Rudolph-Blei)"]

    Default --> Pilot
    Pilot -->|rate < 70%| FA
    Pilot -->|rate ≥ 70%| Skip
    FA --> Stage2
    Skip --> Stage2
    Stage2 --> CheckS2
    CheckS2 -->|yes or<br/>pre-1990 load-bearing| FB
    CheckS2 -->|no| Done[Stage 3 without B]
    FB --> Done

    FC -.->|only if reviewer push<br/>+ B unresolved| Done
```

**Rationale for two axes** (full explanation in plan subsection 2):
Flavor A adds *cross-architecture* robustness (Word2Vec is non-
transformer); Flavor B adds *sophistication* on the domain-adaptation
dimension. They address different aspects of drift; they're not
sequential escalations of one ladder.

---

## 4. Test structure

Four co-primary tests, one mechanism test, one break-point analysis,
with several Stage 3 extensions. Tests I–III operate at aggregate
scale; Test IV operates at per-paper scale; item 11 (the new
production-capture decomposition) bridges the two scales.

```mermaid
flowchart TB
    subgraph Aggregate["<b>Aggregate-scale (year-level)</b>"]
        T1["<b>Test I</b><br/>Standardized-gap trend<br/>Newey-West + Mann-Kendall"]
        T2["<b>Test II</b><br/>Gap regression with 7 controls<br/>(reformulated on Gap_Y)"]
        T3["<b>Test III</b><br/>De-trended cross-correlation<br/>+ Granger causality at lags"]
    end

    subgraph Mechanism["<b>Mechanism tests</b>"]
        SMT["<b>Subfield mechanism</b><br/>Canon-concentration → divergence<br/>(post-1990, per §10)"]
        BP["<b>Break-point analysis</b><br/>Bai-Perron + Chow at<br/>pre-registered candidates"]
    end

    subgraph PerPaper["<b>Per-paper-scale (cross-section)</b>"]
        T4["<b>Test IV</b><br/>Team diversity (T_p) × novelty (N_p)<br/>Double-clustered SEs"]
        T4ext["<b>Test IV Persistence Extension</b><br/>log(1+C_15) × T_p × N_p<br/>+ C_10/C_3 persistence ratio<br/>(Stage 3, papers ≤ 2014)"]
    end

    subgraph Bridging["<b>Scale-bridging (new)</b>"]
        PC["<b>Item 11: Production-capture<br/>aggregate decomposition</b><br/>N(G,Y) and C_10(G,Y) per demographic group<br/>(Stage 3)"]
    end

    T1 --> SMT
    T2 --> SMT
    T1 --> BP
    T4 --> T4ext
    T4 --> PC
    T4ext --> PC
```

**Scale logic:** Tests I–III document aggregate distributional
patterns; Test IV documents per-paper relationships; item 11 uses
per-paper measurements aggregated by demographic group to produce
a population-scale externality claim. See Hofstra review Synthesis
Pointer 11 for the scale-difference framing.

---

## 5. Semantic-diversity metric stack

Three metrics across two families, with a shared robustness column.

```mermaid
flowchart TB
    subgraph Continuous["<b>Continuous-space metrics</b>"]
        B["<b>Primary B: Effective dimensionality</b><br/>Participation ratio of eigenvalues<br/>(year-centered embeddings)"]
        Sec["<b>Secondary: Mean pairwise cosine distance</b><br/>Bootstrap-subsampled"]
    end

    subgraph Categorical["<b>Categorical-space metric</b>"]
        A["<b>Primary A: Cluster entropy</b><br/>Shannon over K=50 cluster assignments<br/>(temporally stratified fit, per §11)"]
    end

    subgraph NEW["<b>Hofstra-style aggregate (new, 2a)</b>"]
        HofAgg["<b>Aggregate novel-pair rate</b><br/>+ concept-diversity entropy<br/>(citation-independent)"]
    end

    subgraph Robust["<b>Robustness column (applied to all)</b>"]
        Mit4["Recompute in anchor-projected space<br/>(Mitigation 4, drift-robust)"]
    end

    A --> Mit4
    B --> Mit4
    Sec --> Mit4
    HofAgg --> Mit4
```

**K=50 main choice** justified empirically in Phase 0.1 Check 5d
(cluster-quality diagnostics). **Cluster fit** on temporally-
stratified pooled subsample (equal papers per decade). Non-negotiable
per desiderata §11.

---

## 6. Novelty metric stack (Test IV)

Three per-paper novelty constructions, running at different Stages,
with different citation dependencies.

```mermaid
flowchart LR
    P["<b>Primary N_p</b><br/>Embedding distance to<br/>citation-context centroid<br/><br/>Stage 2<br/>Citations: define context only"]
    S["<b>Secondary N_p (new)</b><br/>Hofstra-style concept-linkage<br/>First-pairwise-co-occurrences<br/>(PMI-filtered FREX concepts)<br/><br/>Stage 2<br/>Citations: none (zero dependency)"]
    T["<b>Tertiary N_p (optional)</b><br/>Hofstra-style preferred over<br/>Uzzi-style reference-pair recombination<br/><br/>Stage 3 (if pursued)<br/>Citations: none (if Hofstra-style)"]

    P -. "parallel cross-methodology robustness" .- S
    S -. "tertiary variant" .- T
```

**Why secondary exists:** Hofstra's "plethora of reasons to cite"
concern motivates a citation-independent parallel measure. Co-movement
of primary and secondary under Test IV's team-diversity regression
is cross-methodology robustness.

**Why tertiary is optional:** Stage 3 extension; only pursued if
resources allow or reviewers push.

---

## 7. Pathway coverage (Claim #13)

Ws2's engagement level with the 8 pathways for Claim #13. Silent
pathways are substantive scope choices, not omissions.

| Pathway | Engagement | Primary mechanism in ws2 |
|---|---|---|
| 13-A Channel/recommender convergence | Circumstantial | Break-point timing near platform eras |
| **13-B Demographic diversification as cosmetic** | **Direct test** | Tests I–III + Test IV + Item 11 |
| 13-C Institutional selection pressure | Indirect | Prestige/career controls in Test II |
| **13-D Network-topology convergence** | **Direct test** | Subfield mechanism test (Chu-Evans) |
| 13-E Translation/linguistic asymmetry | Silent | English-only corpus |
| **13-F Measurement artifact (null)** | **Directly constrained** | Drift-mitigation ladder + metric plurality |
| 13-G Individual conformity psychology | Silent | No individual-level measures |
| 13-H Endogenous actuator emergence | Weakly suggestive | Break-point patterns |

**Direct coverage:** 3 of 8 pathways (13-B, 13-D, 13-F).
**Circumstantial/indirect/weakly suggestive:** 3 of 8 (13-A, 13-C, 13-H).
**Silent:** 2 of 8 (13-E, 13-G).

**Where the discounted pathways live:** 13-A and 13-G require
interventional or individual-level methodology; scope-appropriate for
ws1 follow-up, not ws2.

---

## 8. Phase 0.1 sanity-check structure

Five numbered checks, two with sub-checks, one with a new addition.
Output lives in `experiments/phase-0.1/`.

```mermaid
flowchart TB
    C1["<b>Check 1</b><br/>Abstract availability<br/>by year"]
    C2["<b>Check 2</b><br/>Concept classifier drift audit<br/>(5 sub-checks 2a-2e)"]
    C3["<b>Check 3</b><br/>Demographic inference<br/>coverage + bias"]
    C4["<b>Check 4</b><br/>Disambiguation<br/>spot-check"]
    C5a["<b>Check 5a</b><br/>Pilot query<br/>(1000 CS papers)"]
    C5b["<b>Check 5b</b><br/>Metric convergence<br/>+ cluster-stratification A/B"]
    C5c["<b>Check 5c</b><br/>Drift-pilot<br/>(1970s era-match)"]
    C5d["<b>Check 5d (new)</b><br/>Cluster-quality<br/>diagnostics"]
    C6["<b>Check 6</b><br/>Literature review<br/>deep dive"]

    C1 --> Close[Phase 0.1 closure]
    C2 --> Close
    C3 --> Close
    C4 --> Close
    C5a --> Close
    C5b --> Close
    C5c -->|gates Flavor A decision| Close
    C5d --> Close
    C6 --> Close
```

**C5c is load-bearing:** its era-match rate result decides whether
Flavor A is committed as a Stage 3 escalation (see diagram 3 above).

---

## Maintenance notes

**When to update this doc:**

- Plan subsection changes that alter a diagram's structure → update
  the corresponding diagram.
- New tests or analyses committed to Phase 0.2 → update diagram 4
  (test structure) and diagram 7 (pathway coverage if applicable).
- Drift-mitigation conditions change → update diagram 3.
- New phases added (e.g., Phase 0.3) → update diagram 2.

**When this doc is authoritative:** never. The plan is authoritative;
this is derivative.

**When to revisit the doc's level of detail:** if a reader needs to
consult the plan to understand a diagram, either the diagram is too
abstract (add detail) or the plan is overspecified for a visual
summary (simplify the plan text). Both cases suggest an edit to one
or the other.
