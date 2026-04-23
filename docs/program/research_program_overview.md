# Research Program Overview: From a Conversation About Originality to Three Testable Projects

**A precursor and context document for the deep research report and the Whitespace 2 and Whitespace 3 compasses.**

---

## What this document is

This is the map of how a broad philosophical conversation about originality and intellectual diversity narrowed into a concrete, testable research program consisting of three projects in a specific order. It exists so that when you return to the research plan — or hand it to a collaborator, advisor, or funder — the full reasoning chain is recoverable without having to retrace the original dialogue.

It references, and is the precursor to:
- **The deep research report** (literature review and pathway DAGs for both claims, methodological precedents, datasets).
- **The Whitespace 2 compass** (empirical paper on demographic vs. semantic plurality).
- **The Whitespace 3 compass** (theoretical paper reconciling cumulative complexity and per-capita variance generation).

## Where this started

The conversation began with two broad philosophical questions:

1. Why are most people unoriginal? Or equivalently: why is originality hard?
2. Why has it become harder to seek inputs that differ from the mainstream?

Initial answers were offered at a mixture of evolutionary, cognitive, epistemological, and sociological registers. Key observations that emerged and held up under scrutiny:

- Minds run on cached abstractions; deviation is metabolically and socially expensive.
- Originality typically comes from unusual input combinations, not from raw talent.
- Recognition of originality is cheap; production is expensive — most people live on the recognition side.
- Platforms, institutions, and formative pipelines have narrowed the channels through which diverse minds express themselves.
- Demographic plurality has risen while intellectual plurality has arguably fallen — a striking decoupling.
- Small protected groups appear to produce disproportionate originality; historical examples are vivid but methodologically suspect.
- The aversion to holding contested beliefs alone has evolutionary, developmental, epistemological, identity-preservation, and modern-intensification components.

The conversation then did something important: it turned self-critical. The claims were catalogued, epistemic status was audited, and the load-bearing claims were identified as those resting most on plausible narrative rather than on clean empirical or formal support.

## The audit and what it found

Twenty-eight distinct assertions were catalogued across the conversation. Each was classified by:

- Strength of empirical backing (Strong / Moderate / Weak / None).
- Whether it is simulatable.
- Whether it has already been simulated.

Most assertions had reasonable backing. The assertions most relied on for emotional force of the argument turned out to be among the least supported:

- **Claim #13**: intellectual plurality has decreased despite demographic plurality increasing, due to homogenization of cultural and intellectual actuators.
- **Claim #14**: raw cognitive variance hasn't declined; only the expression channels have narrowed.
- **Claim #17**: small protected groups produce disproportionate per-capita originality.
- **Claim #25**: "wrong-alone" is psychologically more costly than "wrong-with-crowd" in an asymmetric way.
- **Claim #26**: internal reference points are built through earlier experiences of vindication against consensus.
- **Claim #27**: planetary-scale visible consensus miscalibrates band-sized conformity machinery.

These six emerged as load-bearing but weakly supported. Of them, the two most consequential, most central to the broader philosophical argument, and most tractable via simulation methods were Claim #13 and Claim #17.

## Why Claim #13 and Claim #17 were selected for deeper work

### Tractability via simulation

Claims #25, #26, and #27 are fundamentally about individual human psychology. Testing them rigorously requires experimental psychology methods — longitudinal studies, controlled experiments, physiological measurement — which are expensive, slow, and outside the scope of what a computational research program can produce.

Claim #14 is difficult to operationalize; "raw cognitive variance" is not directly measurable and the measurements that exist are indirect.

Claims #13 and #17, by contrast, are about **population-level dynamics** that are natural candidates for:

- **Agent-based simulation** — they describe how collections of agents, acting under certain rules, produce aggregate patterns over time. This is exactly the modality where agent-based modeling is strongest.
- **Scientometric empirical study** — they make predictions about observable patterns in scientific literature, for which large datasets exist (OpenAlex, S2AG, SciSciNet, Semantic Scholar).
- **Theoretical formalization** — they involve distinctions (demographic vs. intellectual plurality; cumulative preservation vs. variance generation) that lend themselves to formal models.

### Load-bearing status

Claims #13 and #17 are also the two that carry the most weight in the broader philosophical argument about originality:

- If #13 is wrong, the story about "actuators homogenizing a demographically diverse population" falls apart, and the critique of modern intellectual conditions loses much of its force.
- If #17 is wrong, the recommendation of "small protected groups as a mechanism for recovering originality" loses its empirical grounding, and the prescriptive side of the argument weakens substantially.

Testing these two claims is therefore both methodologically tractable and substantively central.

### The relationship between them

Claim #13 and Claim #17 are not independent. The actuators that homogenize intellectual production in #13 are precisely the things small protected groups in #17 are protected *from*. If #13 is strongly correct, #17 is likely correct as a mechanical consequence — small insulated groups would be residual spaces where the homogenizing actuators haven't reached. If #17 is correct but #13 is not, the small-group advantage must be explained by something else (group-internal dynamics, selection, cognitive diversity).

This mutual dependence is why the two claims are best studied together rather than separately. A research program that tests both jointly can ask questions that neither test alone can answer — in particular, whether the mechanism producing #13 also modulates the magnitude of #17.

## From philosophical claims to research projects

Having selected these two claims, the conversation moved through a sequence of narrowing moves:

### 1. Pathway identification

For each claim, 8 distinct causal pathways were identified — different mechanisms that could plausibly produce the claimed phenomenon. For Claim #13 these ranged from recommender systems to institutional selection to network topology to linguistic asymmetry to measurement artifact. For Claim #17 they ranged from pure size effects to internal trust to external insulation to selection to duration to cognitive diversity to network bridging to survivorship bias.

Each pathway was specified at the level of nodes, edges, supporting lineage, and competing alternative hypothesis. The point was to prevent the common failure mode where a simulation "confirms" a mechanism simply because it's the only one implemented. A good simulation needs competing pathways to be distinguishable, not just the target pathway to be reproducible.

### 2. Literature review for whitespace

A deep literature review (captured in the deep research report) identified:

- Where existing empirical work was strongest and weakest.
- Which simulation architectures have been built and what they have not tested.
- Which datasets are available for companion empirical analysis.
- Which research lineages are most relevant and who the natural reviewers would be.

The key finding: **the whitespace sits at a three-way intersection** of (1) opinion-dynamics agent-based models that have never incorporated a distinct "actuator layer," (2) science-of-science scientometrics that measures concentration and disruption but rarely runs mechanistic simulations, and (3) LLM multi-agent frameworks that inherit actuator-homogeneity as a bug without treating it as a tunable variable.

### 3. Three research projects emerged

From the intersection of load-bearing claims, tractable methods, and identified whitespace, three distinct projects crystallized:

**Whitespace 1: A joint agent-based simulation** that parameterizes actuator-sharing and group-insulation together, uses LLM-based agents with rich persona conditioning, and measures per-capita originality at both demographic and semantic levels. This is the most ambitious project and directly tests both Claim #13 and Claim #17 as mechanisms.

**Whitespace 2: An empirical time-series study** that jointly measures demographic and semantic plurality on the same body of scientific literature over ~50 years, testing whether they actually diverge as Claim #13 predicts. This is the cheapest project and provides empirical grounding that either supports or disconfirms Claim #13 before any simulation investment.

**Whitespace 3: A theoretical reconciliation paper** that shows how the Henrich-tradition ("larger populations produce more cumulative complexity") and Wu-Wang-Evans-tradition ("smaller teams produce more per-capita disruption") are reconciled via fitness-component decomposition. This provides the theoretical scaffolding that prevents Whitespace 1's eventual results from being misread as contradicting the population-complexity literature.

## Why the order is 2 → 3 → 1

Several orderings were considered. The chosen order optimizes for **risk reduction and information gain per dollar**.

### Whitespace 2 first

Low cost (~$50-500 and 3-4 months), standalone publishable, and critically: its outcome directly determines whether the simulation work is worth pursuing. If the empirical study shows that demographic and semantic plurality actually track each other rather than diverge, Claim #13 is partially falsified, and Whitespace 1 loses much of its motivation. Better to discover this at the $500 stage than at the $20,000 stage. The option value of doing Whitespace 2 first is very high.

### Whitespace 3 second

Also low cost (essentially $0 and 3-4 months), also standalone publishable, and provides the theoretical framework that Whitespace 1 needs to avoid being dismissed by the cultural-evolution community. Doing it before Whitespace 1 means the simulation is built with the theoretical decomposition already in hand, rather than being retrofitted later.

### Whitespace 1 third

The most expensive and most ambitious project. Should be undertaken only after Whitespace 2 has verified the phenomenon exists and Whitespace 3 has provided the theoretical framework. By this stage, the target is well-defined, the framework is mature, and any funding pitch can point to two published papers as track record.

### Current funding constraint

Whitespace 1 is out of personal budget (~$7-40K depending on ablation scope). The plan is: execute Whitespace 2 and Whitespace 3 independently, then use the two completed papers to pursue external funding for Whitespace 1.

This is a reasonable and disciplined approach. It also has the side benefit of being intellectually honest: you do not commit to a $20K simulation before knowing whether the phenomenon you're simulating actually exists.

## The three projects in relation to each other

The three projects are nested, not parallel:

- **Whitespace 2** is the empirical foundation — does the phenomenon exist?
- **Whitespace 3** is the theoretical scaffolding — what framework does the phenomenon fit into?
- **Whitespace 1** is the mechanistic explanation — what dynamics can produce the phenomenon under the framework?

Doing them in the chosen order means each step's output informs the next. If Whitespace 2 reshapes the empirical picture, Whitespace 3's theoretical setup shifts accordingly, and Whitespace 1's simulation targets shift with both.

Each project is independently publishable. No one of them requires the others to be completed first. But together they form a coherent research program with a clear intellectual arc.

## What the three projects produce, individually and together

### Whitespace 2 outputs

- A time-series decomposition of demographic vs. semantic plurality in 2-3 scientific fields.
- Methodology for this kind of decomposition that other researchers can reuse.
- Within-field subfield analysis linking canonical concentration to divergence magnitude (the key within-field test of the actuator-sharing mechanism).
- A peer-reviewed paper, likely in Quantitative Science Studies or similar.
- Empirical targets for Whitespace 1 to reproduce.

### Whitespace 3 outputs

- A formal decomposition of cumulative complexity (C) and per-capita variance generation (V) as distinct fitness components.
- A minimal formal model demonstrating that both the Henrich and Wu-Wang-Evans results emerge from the same underlying dynamics, just measured differently.
- A phase diagram of the parameter regimes where each fitness component dominates.
- A peer-reviewed paper, likely in Behavioral and Brain Sciences, Proceedings B, or QSS.
- Theoretical framework for Whitespace 1 to instantiate.

### Whitespace 1 outputs (when eventually funded)

- A joint agent-based simulation with actuator-sharing and group-insulation knobs.
- Mechanism-sufficiency results: under what conditions do the observed phenomena emerge?
- Distinguishing tests that separate competing pathways for each claim.
- A peer-reviewed paper, likely in Nature Human Behaviour, PNAS, or equivalent.
- Concrete recommendations for institutional design around protecting or eroding intellectual diversity.

### Combined output

Together, the three projects constitute a research program that:
- Establishes empirically whether intellectual plurality has declined despite demographic plurality rising.
- Provides the theoretical framework for understanding that decline (or its absence) in relation to cultural-evolutionary literature.
- Demonstrates via simulation which mechanisms are sufficient to produce the observed patterns.
- Produces concrete institutional and policy implications, grounded in all three layers.

This is the kind of research agenda that can span a multi-year arc, support subsequent work, and open doors to related projects (institutional design, platform design, cognitive diversity measurement in new settings).

## Key decisions made along the way, and why

### Why combine Claims #13 and #17 rather than study them separately

Because the actuators that homogenize in #13 are what small protected groups in #17 are protected from. The mechanisms interact. A joint simulation can ask whether the same parameter that drives #13's homogenization also modulates #17's small-group advantage — a question neither claim's isolated test can answer.

### Why simulation + empirics + theory rather than any one alone

Simulation alone risks being a model in search of a phenomenon. Empirics alone risks describing a pattern without explaining it. Theory alone risks reconciling two literatures without showing the reconciliation matters in observable data or in generative dynamics. The three together are mutually reinforcing: empirical phenomenon + theoretical framework + mechanistic demonstration.

### Why LLM-based agents for Whitespace 1 rather than abstract-state agents

Because the actuator-sharing knob — "fraction of agents sharing a foundation model" — has a clean operational meaning in LLM-based agents that has no equivalent in abstract-state models. The specific mechanism being tested (shared formative substrate as a homogenization force) is best implemented in systems where substrate-sharing is literally a parameter. LLM-based multi-agent frameworks have matured to the point where this is now tractable.

### Why the minimum-viable ablation set is (13-A, 13-F, 17-A, 17-C, 17-D, 17-H) and not the full 16 pathways

Because these six are implementable as knobs on a single architecture without structural additions, and because they include the two nulls (13-F measurement artifact, 17-D selection null, 17-H survivorship null) that any substantive mechanism claim must beat. Remaining pathways require either architectural extensions or are better studied separately. This is a deliberate scoping choice, not a compromise.

### Why defer Whitespace 1 until funding is available

Because the simulation's cost (~$7-40K) is large enough to warrant de-risking via the cheaper projects first, and because the two earlier projects produce track record that materially improves funding prospects. Rushing into Whitespace 1 before establishing empirical grounding and theoretical framing would be both riskier and a weaker funding pitch.

## When to return to this document

Read this again when:
- You're starting a new work block and want to re-situate.
- You're writing an introduction or motivation section for either Whitespace 2 or Whitespace 3.
- You're about to explain the project to a potential collaborator, advisor, or funder.
- You're questioning whether the project is worth pursuing.
- A reviewer or critic asks why you chose this specific scope.
- You're preparing materials for a funding application for Whitespace 1.

## Where to go from here

- **For execution of Whitespace 2**: see `whitespace_2_compass.md` for week-by-week pipeline, data sources, and failure modes.
- **For execution of Whitespace 3**: see `whitespace_3_compass.md` for the formal model setup, reading list, and paper structure.
- **For deeper literature, pathways, and datasets**: see the deep research report for the full map of prior work and the 8-pathway breakdown for each claim.

## One more thing

This research program exists because a conversation about why originality is hard turned into an audit of its own claims, then into a literature review, then into a set of specific testable projects. The arc from philosophical question to research program is the thing that should feel worth preserving, because it's what lets the program's later steps remain connected to the original motivation.

The point is not to "prove" that intellectual plurality has declined, or that small groups produce more originality. The point is to find out, rigorously, whether and in what form these claims hold — and to produce work that can be built on whether the answers turn out to be what we currently expect or not. Good research programs are legible to themselves; this one is built to remain so.
