# Mapping the whitespace for simulating intellectual plurality and small-group originality

This review argues that the most promising simulation whitespace sits at a **three-way intersection**: (1) opinion-dynamics / cultural-evolution ABMs that have never incorporated a distinct "actuator layer" (shared texts, recommenders, institutional filters), (2) science-of-science scientometrics that measure disruption and semantic novelty but rarely run mechanistic simulations, and (3) LLM multi-agent frameworks (ResearchTown, Generative Agents, AgentRxiv) that inherit actuator-homogeneity as a bug, never as a tunable variable. A new simulation that explicitly parameterizes actuator sharing and group insulation — and that reports **per-capita** originality decomposed against demographic plurality — would occupy ground that is thin in every adjacent literature.

Two load-bearing claims structure the report. **Claim #13** (intellectual plurality declining despite rising demographic plurality, due to homogenizing actuators) is well-supported *directionally* — by canonical ossification studies (Chu & Evans 2021 PNAS), RLHF diversity-loss (Kirk et al. 2024), music/film homogenization (Serrà 2012, Mauch 2015, Cutting 2011), translation asymmetry (Heilbron 1999; UNESCO Index Translationum), and algorithmic-monoculture theory (Kleinberg & Raghavan 2021) — but the headline Park-Leahey-Funk 2023 CD-index decline is *contested* (Petersen et al. 2024, Holst et al. 2024, Macher et al. 2024). **Claim #17** (small insulated groups produce disproportionate per-capita originality) is directly supported by Wu-Wang-Evans 2019, Lin-Frey-Wu 2023, Azoulay-Graff Zivin-Manso 2011 (HHMI), Moser-Voena-Waldinger 2014 (émigrés), Burt 2004 brokerage, Paulus-Nijstad group productivity loss, and Nemeth's dissent corpus — but faces a formal challenge from Henrich's Tasmania thesis and Powell et al. 2009, which predict *larger* populations should be more creative. The reconciliation lies in distinguishing **cumulative complexity preservation** (where N helps) from **variance generation / originality per capita** (where small insulated high-trust groups can dominate) — a distinction no existing ABM formalizes.

Below I map each literature in depth, specify 6–8 competing causal pathways per claim, and identify the concrete datasets and architectures a new simulation would build on.

## 1. Claim #13: intellectual plurality declining despite demographic plurality rising

### 1.1 Empirical status

The claim has three distinguishable components, each with different evidential support.

**Component A — declining intellectual plurality over time.** The headline evidence is Park, Leahey & Funk 2023 (*Nature* 613), reporting ~92% decline in CD5 for papers and ~79% for patents from 1945–2010 across 45M papers and 3.9M patents. This is seriously contested. Petersen, Arroyave & Pammolli (2024, *QSS* 5(4); arXiv:2306.01949) show the decline is driven mechanically by citation-inflation as reference lists grow; in citation-normalized SciSciNet data, CD actually **increased** 2005–2015 and the team-size coefficient turns positive at size ≥8. Holst et al. (2024, arXiv:2402.14583) show the decline largely disappears for science and attenuates for patents once zero-reference database artifacts are excluded. Macher et al. (2024, *Research Policy*) show highly-disruptive patents have increased since 2008 after truncation correction. Leibel & Bornmann (2024, *Scientometrics* 129(1)) run a "multiverse" analysis and conclude DI5 is more robust than DI1, and convergent validity is "not entirely conclusive." **The Park-Leahey-Funk decline should be treated as a contested secondary target, not a stylized fact to reproduce.**

More robust support for declining plurality comes from **Chu & Evans 2021** (*PNAS* 118(41)), analyzing 1.8B citations across 90M papers, 241 subjects: as annual publication volume grows, top-50-most-cited lists ossify (Spearman rank correlation across years rises from ~0.25 in small fields toward much higher values in large ones), new papers rarely break into canon, and disruption propensity declines. This is a **scale-driven preferential-attachment mechanism** that is independent of the CD-index controversy. **Foster, Rzhetsky & Evans 2015** (*ASR* 80(5)) show via ~6M MEDLINE abstracts that "repeat" research strategies outnumber "jump" strategies ~6:1, and the expected return favors tradition except in the upper tail — a micro-level conformity mechanism.

**Component B — demographic plurality rising.** Broadly accepted from OpenAlex/WoS institutional data on authorship by country, gender, and institution. Hofstra et al. 2020 (*PNAS*, "Diversity-Innovation Paradox") shows minority-background scholars introduce novel concepts at higher semantic-distance rates but receive less citation uptake — a striking existence proof that demographic and intellectual plurality can *decouple*.

**Component C — homogenizing actuators as the mechanism.** Evidence varies by actuator class:
- **Recommender systems**: Chaney, Stewart & Engelhardt 2018 (RecSys) ABM shows algorithmic confounding increases user-behavior Jaccard homogenization without utility gains. Kleinberg & Raghavan 2021 (*PNAS* 118(22)) prove algorithmic monoculture can reduce social welfare even when individually accurate. Bommasani et al. 2022 NeurIPS ("Picking on the Same Person") formalizes outcome homogenization from component-sharing.
- **LLM-mediated content**: Padmakumar & He 2024 (ICLR) show InstructGPT (RLHF-tuned) co-writing significantly reduces inter-author content diversity while base GPT-3 does not — **isolating RLHF as the homogenizing operator**. Doshi & Hauser 2024 (*Science Advances* 10, eadn5290) replicate across 300 short-story writers. Anderson, Shah & Kreminski 2024 (C&C) show individual-level diversity preserved but group-level semantic diversity drops under ChatGPT ideation. Kirk et al. 2024 (ICLR) provide the mechanistic explanation: RLHF induces mode collapse relative to SFT.
- **Translation/linguistic asymmetry**: UNESCO Index Translationum (via Heilbron 1999 *EJST*) shows English accounts for 55–60% of all source-translated books worldwide while UK/US publish <5% translations — a stark hub-and-spoke structure. Lupyan & Dale 2010 analyze >2,000 languages showing large-population lingua francas shed inflectional morphology. Gordin's *Scientific Babel* documents >90% of science now publishes in English, up from ~40% in 1910.
- **Media concentration**: Bagdikian's 50→5 trajectory (1983→2004); Serrà et al. 2012 *Scientific Reports* show restricted pitch transitions and timbral homogenization across 464,411 recordings 1955–2010; Mauch et al. 2015 *RSOS* find 1986 the least diverse year in Billboard analysis of 17,000 songs; Cutting et al. 2011 document mean shot length dropping from ~13.0s (1945) to ~4.3s (2005) across 160 films. Franchise films captured ~82.5% of 2019 Hollywood worldwide box office.
- **Institutional / paradigm pressure**: Kuhn's paradigm concept; Bourdieu's *Homo Academicus* correspondence analysis; Abbott's fractal distinctions; Merton's Matthew effect (updated by Bornmann 2021 *QSS*). Azoulay, Graff Zivin & Wang 2010 "Superstar Extinction" (*QJE* 125) show premature superstar deaths cause 5–8% permanent productivity drops in field collaborators, and their 2019 *AER* extension shows such deaths *open* subfields to outsider entry and novelty — a natural experiment on gatekeeper homogenization.

### 1.2 Literature map for Claim #13

| Thread | Core works | What it contributes |
|---|---|---|
| Opinion-dynamics ABMs | Deffuant et al. 2000; Hegselmann-Krause 2002; Axelrod 1997; Flache & Macy 2011 | Baseline fragmentation/consensus kernels; polarization via repulsive influence |
| Mass-media-extended ABMs | González-Avella et al. 2005, 2007; Peres & Fontanari 2011; Sîrbu et al. 2019; Pansanella et al. 2022 | External-field / broadcast mechanisms; algorithmic-bias as partner-selection bias |
| Canonical ossification | Chu & Evans 2021; Foster-Rzhetsky-Evans 2015; Rzhetsky-Foster-Foster-Evans 2015 | Scale-driven attention concentration; strategy-frequency ratios |
| Disruption decline & critiques | Park-Leahey-Funk 2023; Petersen et al. 2024; Holst et al. 2024; Macher et al. 2024; Leibel-Bornmann 2024 | Contested headline decline; methodological caution on CD-index |
| Cultural evolution / conformity | Boyd-Richerson 1985; Mesoudi 2011; Henrich 2020 WEIRDest People; Schulz et al. 2019 (*Science*, kinship index) | Conformist transmission at scale; global WEIRDification |
| Media / recommender homogenization | Bagdikian 1983/2004; Serrà 2012; Mauch 2015; Interiano 2018; Cutting 2011; Chaney 2018; Kleinberg-Raghavan 2021; Bommasani 2022 | Documented content compression; formal monoculture theorems |
| LLM homogenization | Padmakumar-He 2024; Doshi-Hauser 2024; Anderson et al. 2024; Kirk et al. 2024; Shumailov 2024 (model collapse); Taubenfeld et al. 2024 | RLHF as homogenizing operator; model collapse; silicon-agent convergence |
| Sociology-of-science actuators | Kuhn 1962; Price 1963; Merton 1968; Bourdieu 1984; Abbott 2001; Wellmon 2015 | Theoretical vocabulary for actuator types |
| Translation asymmetry | Heilbron 1999; Casanova 2004; UNESCO Index Translationum; Gordin 2015; Lupyan-Dale 2010 | Core-periphery cultural flow quantification |

**Current gaps specific to Claim #13:**
1. No ABM represents "shared canonical text" as an object distinct from mass-media broadcast or stubborn-agent influence — agents jointly ingesting a corpus with heterogeneous priors, producing derivative outputs, is unmodeled.
2. No ABM reproduces Park-Leahey-Funk CD decline from first principles while separately varying reference-list growth, canonical-reference concentration, and field size — which would adjudicate Petersen's citation-inflation-artifact null against a genuine homogenization hypothesis.
3. No longitudinal decomposition links demographic plurality (OpenAlex author metadata) to semantic plurality (SPECTER2 embedding variance) over time — Hofstra et al. 2020 comes closest but is cross-sectional.
4. No ABM varies the **LLM backbone across agents** to test whether actuator diversity prevents the Chuang/Taubenfeld/Santurkar convergence pattern.
5. Recommender-system effects are theorized (Chaney 2018, Smaldino 2024) but never coupled to scientific production dynamics in the Park-Leahey-Funk style.
6. Sociology-of-knowledge actuator theories (Kuhn paradigms, Bourdieu field capital, Abbott fractal distinctions, Wellmon media-technology, Merton Matthew effect) have never been formalized as competing ABM primitives with distinguishable predictions.

### 1.3 Competing causal pathways for Claim #13

Each pathway below is specified at node/edge level for iteration before structural-equation commitment.

**Pathway 13-A: Channel / recommender convergence (the user's own hypothesis).**
Nodes: `PlatformRecommender`, `ContentCatalog`, `UserExposure`, `UserOutput`, `CollectiveOutputVariance`. Edges: Recommender → Exposure (ranking compression); Exposure → Output (imitation with bounded noise); Output → Catalog (feedback); Catalog → Recommender (retraining loop). Confounders: user productivity heterogeneity; outside-option consumption. Prior simulation: Chaney-Stewart-Engelhardt 2018 is the direct template. **Distinguishing signature**: diversity collapse is a function of recommender feedback-loop intensity; turning off retraining restores diversity. Empirical anchor: Padmakumar-He InstructGPT effect.

**Pathway 13-B: Demographic diversification as cosmetic (shared formative channels flatten outputs).**
Nodes: `DemographicGroup`, `FormativeInstitution` (university, curriculum, textbook), `CognitiveRepertoire`, `Output`. Edges: Demographic → Institution-choice; Institution → Repertoire (curricular homogenization); Repertoire → Output. Confounders: self-selection into institutions. Prior work: Page's cognitive-vs-identity diversity distinction (2007/2017); Hofstra et al. 2020 PNAS; Kalev-Dobbin 2006 on diversity-program failure. **Distinguishing signature**: demographic variance high but repertoire variance low when institutional sharing is high; varies monotonically with curricular overlap. Novel contribution: this has never been simulated with *endogenous* institutional selection.

**Pathway 13-C: Institutional selection pressure (academic/media incentives reward conformity).**
Nodes: `RiskAversion`, `ResearchStrategy` (tradition/jump), `Reward`, `CareerPosition`, `StrategyDistribution`. Edges: Position → RiskAversion; RiskAversion → Strategy; Reward → Strategy (reinforcement); Strategy → Output. Confounders: talent heterogeneity, field maturity. Prior work: Azoulay-Graff Zivin-Manso 2011 (HHMI vs NIH); Foster-Rzhetsky-Evans 2015; Packalen-Bhattacharya 2019; Smaldino-McElreath 2016 "natural selection of bad science." **Distinguishing signature**: varying reward structure (tolerance-for-failure, evaluation-cycle length) mechanically shifts strategy distribution without any change in platform or demographic variables. Rich empirical anchor in HHMI data.

**Pathway 13-D: Network-topology-driven convergence (small-world/scale-free amplification of dominant nodes).**
Nodes: `NetworkTopology`, `PreferentialAttachment`, `AttentionConcentration`, `Output`. Edges: Topology → Attachment intensity; Attachment → Concentration; Concentration → Output (citation/reference imitation). Prior work: Barabási 1999 preferential attachment; Uzzi-Spiro 2005 inverted-U parabolic creativity curve in Broadway; Chu-Evans 2021 scale-driven ossification; Centola-Macy 2007 complex contagion requirements. **Distinguishing signature**: diversity should be a non-monotonic function of connectivity with an inverted-U (Uzzi-Spiro bliss point); pure scale-up of a scale-free network reproduces ossification without any change in actuator semantics.

**Pathway 13-E: Translation / linguistic asymmetry (English as universal solvent).**
Nodes: `LanguageProduced`, `TranslationFlow`, `CrossLanguageExchange`, `ConceptualRepertoire`. Edges: English-status → Translation flow asymmetry; Flow → Exchange (one-way); Exchange → Repertoire (peripheral absorbs from core; core rarely absorbs from periphery). Prior work: Heilbron 1999; Casanova 2004; Gordin 2015; Lupyan-Dale 2010 (the one existing ABM for linguistic niches, Dale-Lupyan 2012 *Adv. Complex Systems*). **Distinguishing signature**: diversity asymmetry by position in translation network — peripheral languages' output should become more English-like over time, while English output shows no reciprocal effect. Dataset: Index Translationum (pre-2012).

**Pathway 13-F: Measurement artifact (no real decline; observer/index bias).**
Nodes: `TrueOutputDiversity`, `CitationPractices`, `ReferenceListGrowth`, `MeasuredCD`. Edges: Reference-list growth → CD_measured (mechanical); CitationPractices → CD_measured. This is the Petersen / Holst / Macher critique — a null hypothesis that must be precommitted to as a simulation branch. **Distinguishing signature**: measured decline reproduces under pure citation-inflation with zero change in underlying output diversity, *if* reference-list growth rate is the single varying parameter. This null is essential to include because any ABM that "reproduces" Park-Leahey-Funk without ruling it out has proven nothing.

**Pathway 13-G: Cognitive/psychological conformity pressure (visible consensus amplifies conformity).**
Nodes: `VisibleConsensusLevel`, `ConformityPropensity`, `IndividualExpression`, `AggregateDiversity`. Edges: Visible consensus → Conformity (Asch-style); Conformity → Suppression of minority expression; Expression → Aggregate. Prior work: Nemeth 1986 minority-influence corpus; Mäs-Flache 2010 on noise / individualization driving clustering; Salganik-Dodds-Watts 2006 Music Lab (Gini 0.21 independent → 0.50 strong social influence). **Distinguishing signature**: hides diversity at expression level while preserving it at belief level — a latent/manifest variable gap. Moderate-dissent-induced divergent thinking (Nemeth) breaks this path.

**Pathway 13-H: Endogenous actuator emergence (platforms and canons bootstrap themselves).**
Nodes: `EarlyAdoption`, `Platform/CanonStatus`, `Adoption`, `Output`. Edges: Early adoption → Platform status (via network externality); Platform status → Further adoption; Adoption → Output (shared exposure). This is a **bridge pathway** between 13-A and 13-D: actuators are not exogenous but emerge from topology. Closest precedent: Centola-González-Avella-Eguíluz-San Miguel 2007 co-evolving networks. Key novelty: lets the simulation show that homogenization can appear even when no actor intends it.

### 1.4 Discriminating predictions

A simulation that precommits to these pathways would distinguish them via **five measurement axes**:
1. Demographic-vs-intellectual diversity ratio over time (13-B and 13-H predict gap; 13-D predicts coupled decline).
2. Diversity response to actuator-sharing knob (13-A and 13-H predict strong; 13-C and 13-E weak).
3. Diversity-vs-connectivity curvature (inverted-U for 13-D; monotonic for 13-A; flat for 13-F).
4. Latent-vs-expressed diversity gap (13-G only).
5. Reproducibility of Park-Leahey-Funk decline *without* underlying output change (13-F diagnostic).

## 2. Claim #17: small protected groups and per-capita originality

### 2.1 Empirical status

Claim #17 has stronger and more convergent empirical support than #13, but faces one formal theoretical challenge.

**Supporting evidence.**
- **Wu, Wang & Evans 2019** (*Nature* 566) — 65M papers/patents/software 1954–2014. Small teams (1–3 authors) produce systematically higher CD values; Nobel-prize papers cluster in top ~2% of disruption. Small teams draw on older, less popular references. Effect persists within-individual controlling for field/era. Caveat: non-monotonic in Petersen et al.'s corrected analysis, but the *small-team-disruption* association survives in multiple datasets.
- **Lin, Frey & Wu 2023** (*Nature* 623) — 20M articles + 4M patents. Remote co-authored teams produce disruptive work at lower rates across all fields, sizes, and eras. Strongly supports co-location / high-trust mechanism.
- **Azoulay, Graff Zivin & Manso 2011** (*RAND J. Econ.* 42) — HHMI investigators vs. propensity-matched NIH R01 recipients. HHMI's "people not projects," 5-year cycle, failure-tolerant model yields substantially more top 1% papers; MeSH analysis shows migration to newer scientific frontiers, effects emerging years 4–5.
- **Azoulay, Fons-Rosen, Graff Zivin 2019** (*AER*) — superstar deaths open subfields to outsider entry and novelty (after lag).
- **Moser, Voena & Waldinger 2014** (*AER* 104) — German Jewish émigré dismissals post-1933. US patenting in émigré chemistry fields rose 31%, driven by attracting new entrants.
- **Hunt & Gauthier-Loiselle 2010** (*AEJ: Macro* 2) — 1pp rise in immigrant college-grad share → 9–18% rise in patents per capita.
- **Burt 2004** (*AJS* 110) — structural-hole brokers disproportionately produce highly-rated ideas in electronics-firm study (N=673 managers).
- **Paulus & Nijstad 2003** *Group Creativity* (review volume) — nominal groups outperform face-to-face groups by 30–50% in idea quantity and originality; interacting-group productivity loss via blocking/apprehension.
- **Nemeth 1986, 2018** — authentic minority dissent shifts attention from convergent to divergent thinking; small groups with genuine dissenters produce more original word-associations and detect more hidden-figure solutions.
- **Zollman 2007, 2010** — bandit-problem ABMs where less-connected scientific communities reach correct answers more reliably; connectivity causes premature consensus.
- **Fang, Lee & Schilling 2010** (*Organization Science* 21) — semi-isolated subgroups in March-style organizational learning: moderate isolation maximizes long-run performance by preventing premature convergence. The single closest methodological precedent for Claim #17.
- **Lazer & Friedman 2007** (*ASQ* 52) — less-connected networks outperform fully-connected on hard problems (NK-landscape). Extended and refined by Barkoczi & Galesic 2016 (*Nat. Commun.* 7): effect is *strategy-dependent* — inefficient networks help under best-member strategy, hurt under conformity.
- **Guimerà, Uzzi, Spiro & Amaral 2005** (*Science* 308) — team assembly mechanisms: newcomers + incumbents + low repetition maximize impact; critical point to large-connected-community phase transition.
- **Invisible-college tradition**: Price 1963; Crane 1972 — ~100-person cores in research fields account for most ideational propagation. Narrative extensions to Copenhagen physics, Bourbaki, Bell Labs, Xerox PARC, IAS Princeton, Santa Fe Institute — all qualitatively supportive but **quantitatively unbenchmarked** per-capita productivity.

**Formal challenge.**
- **Henrich 2004** (*American Antiquity* 69) Tasmania model + **Powell, Shennan & Thomas 2009** (*Science* 324) population-size metapopulation ABM: small isolated populations *lose* cultural complexity under "Best" transmission with Gumbel noise. **Vaesen et al. 2016** (*PNAS* 113) rebut — the result is not robust to transmission-rule variation — but the Henrich tradition remains the orthodoxy a Claim #17 ABM must confront.
- **Derex et al. 2013** (*Nature* 503), **Muthukrishna et al. 2014** (*Proc. R. Soc. B*): larger groups and more models preserve complex skills. **Rendell et al. 2010** (*Science* 328) social-learning tournament: nearly pure social-learning wins when a minority of innovators are supplying novelty.

**The resolution** requires distinguishing two fitness components:
- **Complexity preservation** (faithful transmission of cumulative culture; Henrich-Powell-Derex regime; N helps).
- **Variance generation / originality per capita** (producing novel outputs; small insulated high-trust groups can dominate via Nemeth dissent, Burt insight arbitrage, Zollman premature-consensus avoidance, Azoulay-Manso failure tolerance).

No existing ABM explicitly decomposes these. This is the central theoretical contribution available.

### 2.2 Literature map for Claim #17

| Thread | Core works | Contribution |
|---|---|---|
| Team size & disruption | Wu-Wang-Evans 2019; Lin-Frey-Wu 2023; Uzzi et al. 2013 (atypical combinations) | Strongest quantitative backbone |
| Incentive / tolerance | Azoulay-Graff Zivin-Manso 2011 HHMI; Manso 2011 (*JF*); Azoulay et al. 2010, 2019 (superstar death) | Causal evidence for insulation-from-short-cycle-evaluation |
| Émigré / outsider effect | Moser-Voena-Waldinger 2014; Hunt-Gauthier-Loiselle 2010; Simonton outsider corpus | Causal evidence small insulated groups disproportionately innovate |
| Network-structure-innovation | Lazer-Friedman 2007; Fang-Lee-Schilling 2010; Barkoczi-Galesic 2016; Mason-Watts 2012 | Core methodological templates |
| Structural holes & brokerage | Burt 1992, 2004, 2015; de Vaan-Vedres-Stark 2015 (structural folding) | Brokerage vs. insulation tension |
| Complex contagion | Centola & Macy 2007; Centola 2010, 2018; Centola et al. 2018 (25% tipping) | Internal density requirement for complex innovations |
| Minority influence | Nemeth 1986, 2018; Moscovici; Paulus-Nijstad 2003 | Small-group dissent → divergent thinking |
| Cultural-evolution orthodoxy | Henrich 2004; Powell et al. 2009; Derex et al. 2013; Muthukrishna et al. 2014; Rendell et al. 2010 | Formal challenge: large populations preserve complexity |
| Orthodoxy critique | Vaesen et al. 2016; Kobayashi-Aoki 2012 | Conditionality of N→complexity result |
| Invisible colleges | Price 1963; Crane 1972; Merton; Collins 1998 *Sociology of Philosophies* | Qualitative-to-quantitative bridge |
| Diverse-solver theorems | Hong-Page 2001, 2004; Page 2007, 2017; Grim et al. 2019 critique | Diversity trumps ability, conditionally |
| Zollman effect | Zollman 2007 (*Phil. Sci.*), 2010; Grim et al. 2013 | Less-connected scientific networks track truth better |
| Heterodox institutes | Gertner 2012 Bell Labs; Hiltzik 1999 PARC; SFI case histories | Narrative evidence; quantitative benchmarks absent |

**Current gaps specific to Claim #17:**
1. Fang-Lee-Schilling 2010 varies inter-group connectivity but all groups are peers — no ABM tests the topology of **one mainstream + N small insulated subgroups with asymmetric influence flow**, which is precisely Claim #17's structure.
2. Almost no ABM reports **per-capita originality**. Uzzi-Spiro, Guimerà, Fang-Lee-Schilling all measure team-total or equilibrium performance.
3. "Internal trust" as a tunable parameter is absent. Guimerà's q (tie-repetition) + Friedkin-Johnsen anchoring are usable proxies but have not been combined.
4. No model reconciles Henrich-Powell ("N helps") with Wu-Wang-Evans + Lin-Frey-Wu ("small helps") by decomposing complexity-preservation from variance-generation.
5. Quantitative per-capita productivity of heterodox institutes (IAS, SFI, Bell Labs, PARC, MIT Media Lab) is unbenchmarked — available as a companion meta-analysis opportunity.
6. Burt brokerage and Claim #17 insulation imply *opposing* optimal topologies; no ABM splits generation from evaluation/selection to test whether insulated generation + brokered evaluation Pareto-dominates either pure strategy.
7. Hong-Page's landscape-ruggedness sensitivity (Grim et al. 2019) has never been linked to the historical question of whether modern knowledge landscapes are smoothing (which would eliminate Claim #17's small-group advantage per Grim).
8. LLM-ABMs of research communities (ResearchTown, AgentRxiv, Virtual Lab) have not systematically varied inter-cluster connectivity and external-attention budget to test Claim #17 directly.

### 2.3 Competing causal pathways for Claim #17

**Pathway 17-A: Size effect — low coordination cost, deeper mutual understanding.**
Nodes: `GroupSize`, `CoordinationCost`, `MutualUnderstandingDepth`, `SharedIdeaRefinement`, `PerCapitaOriginality`. Edges: Size → Cost (super-linear); Size → Understanding (inverted); Understanding → Refinement → Originality. Confounders: task complexity, division of labor. Prior work: Paulus-Nijstad 30–50% productivity-loss finding; Brooks's Law generalized; Wu-Wang-Evans team-size effect. **Distinguishing signature**: originality is a decreasing function of size *conditional on task allowing small-team execution*; disappears for tasks requiring extensive labor division.

**Pathway 17-B: Internal trust / permissive filter — speculation survives to refine.**
Nodes: `TrustLevel`, `InternalCriticism`, `IdeaSurvivalProbability`, `Refinement`, `Originality`. Edges: Trust → Internal criticism weight (lower early filter); Trust → Survival; Survival × Criticism-later → Refinement. Confounders: groupthink (too-high trust collapses diversity). Prior work: Nemeth dissent; Virtual Lab's critic agent architecture (Swanson et al. 2024 *Nature*); Stark 2009 heterarchy. **Distinguishing signature**: at moderate trust levels, idea novelty is preserved long enough for refinement; extreme trust produces echo chambers; extreme distrust produces premature rejection. Inverted-U prediction.

**Pathway 17-C: External insulation — group develops local norms divergent from mainstream.**
Nodes: `ExternalContactRate`, `ExposureToMainstreamNorms`, `LocalNormDrift`, `Originality`. Edges: Contact → Exposure → Norm convergence; reduced contact → Local drift → Novel-from-mainstream perspective. Confounders: selection (who chooses isolation). Prior work: Zollman 2007 bandit networks; Fang-Lee-Schilling subgroup isolation; Casanova peripheral-revolt authors (Joyce, Beckett, Ibsen). Closest precedent: Zollman's architecture extended with insulation as tunable parameter. **Distinguishing signature**: originality (measured as semantic distance from mainstream field centroid) scales inversely with external contact rate, controlling for size and membership composition.

**Pathway 17-D: Selection / assortative matching — talented heterodox individuals co-locate; group is effect not cause.**
Nodes: `IndividualTalent×Heterodoxy`, `GroupJoining`, `GroupOutput`. Edges: Talent×Heterodoxy → Joining (assortative); Joining → Output. This is the **null** for the group-effect claim: the protected-group pattern reduces to a survivorship story over an unmeasured base rate. Prior work: Sinatra et al. 2016 Q-model (individual ability stable across career); Hofstra et al. 2020 diversity-innovation paradox. **Distinguishing signature**: controlling for individual pre-group outputs eliminates the group effect; an ABM that assigns random individuals to insulated groups and finds no originality gain supports this null.

**Pathway 17-E: Duration / iterative refinement — time allows depth.**
Nodes: `GroupDuration`, `IterationCount`, `DepthOfExploration`, `Originality`. Edges: Duration → Iterations → Depth → Originality. Prior work: Liu et al. 2018 Nature "hot streaks" — 4–5 year focused exploitation periods in 90% of creative careers; Azoulay-Manso HHMI year-4/5 effect onset. **Distinguishing signature**: originality per group-year is low early, rises at a characteristic lag, then plateaus. Destroying or interrupting groups before the lag should eliminate the effect. Empirical anchor: HHMI 4–5-year onset.

**Pathway 17-F: Cognitive diversity within group (Hong-Page mechanism).**
Nodes: `WithinGroupHeuristicDiversity`, `ProblemLandscape`, `CollectiveSearch`, `Originality`. Edges: Diversity → Search breadth → Originality (conditional on ruggedness). Prior work: Hong-Page 2001, 2004; Grim et al. 2019 landscape-dependent critique. **Distinguishing signature**: originality advantage depends on landscape ruggedness; disappears on smooth problems. **Importantly**, this pathway cuts *across* Claim #17's "protected" framing — a diverse small group may outperform via Hong-Page even without external insulation.

**Pathway 17-G: Network bridging / structural holes — groups at intersection of otherwise-disconnected communities.**
Nodes: `GroupPosition`, `NonRedundantExposure`, `Recombination`, `Originality`. Edges: Position at structural hole → Exposure → Recombination → Originality (Burt). Confounders: coordination cost of straddling. Prior work: Burt 2004; de Vaan-Vedres-Stark 2015; Uzzi et al. 2013 atypical combinations. **Distinguishing signature**: originality scales with structural-hole constraint measure, not with size or insulation per se. **Key tension**: this pathway predicts the OPPOSITE of 17-C (brokerage requires connection across groups, insulation blocks brokerage). A good simulation separates generation (17-C favored) from evaluation/selection (17-G favored) phases.

**Pathway 17-H: Pure survivorship bias — no real effect beyond selection on unmeasured base rate.**
Nodes: `UnobservedGroupCount`, `OutputVarianceAcrossGroups`, `ResearcherAttention`, `SelectionOfCasesIntoLiterature`. Edges: Many groups → variance in outputs → ex-post selection of high-output groups → apparent small-group advantage. This is the stronger null for the historical/case-study evidence (Bell Labs, PARC, SFI). **Distinguishing signature**: if an ABM can reproduce the *distribution* of group outputs under pure noise + selection, the case-study evidence proves nothing. Empirical check: compare per-capita productivity of *all* similarly-insulated groups (successful and failed), which requires compiling non-famous institute data — a companion meta-analysis.

### 2.4 Discriminating predictions

A Claim #17 simulation should report:
1. Per-capita originality vs. group size (17-A direct; 17-F conditional on landscape).
2. Per-capita originality vs. within-group trust parameter, with inverted-U expected (17-B).
3. Per-capita originality vs. external-contact rate, with monotonic decrease expected (17-C).
4. Effect of random-vs-selective assignment to groups (17-D, 17-H nulls).
5. Per-group-year onset curve of originality (17-E lag test).
6. Interaction of landscape ruggedness × group diversity (17-F sensitivity).
7. Generation-phase vs. evaluation-phase topology optimum (17-C vs. 17-G separation).
8. Full distribution of insulated-group outputs, not just extrema (17-H bias test).

## 3. The central whitespace

Integrating across the five subreviews, the highest-value research whitespace is the intersection of three gaps that, taken together, no existing work addresses:

**Whitespace 1: A joint ABM of actuator-sharing and group-insulation with a per-capita originality metric.** All existing work picks one: opinion-dynamics ABMs vary actuators (mass-media extensions of Axelrod) but have uniform network topology; network-innovation ABMs (Fang-Lee-Schilling, Lazer-Friedman) vary topology but have no actuator layer; scientometrics measures disruption in historical data but runs no mechanism simulation; LLM-ABMs (ResearchTown, AgentRxiv) inherit actuator-homogeneity implicitly. A single ABM varying both dimensions — with a heterogeneous agent population sampled from Park et al. 2024's 1,052-persona bank or a synthetic analog — would let Claims #13 and #17 be tested jointly.

**Whitespace 2: Decomposing demographic plurality from intellectual/semantic plurality, over simulated time.** No work computes these on the same population over the same horizon. OpenAlex metadata + SPECTER2 embeddings + the SciSciNet-merged disruption fields make this concretely feasible on real data (companion meta-analysis), and an ABM can output both variables natively.

**Whitespace 3: Reconciling Henrich ("N helps complexity") with Wu-Wang-Evans ("small helps disruption") via explicit decomposition of cumulative-preservation vs. variance-generation fitness components.** This would clarify that Claim #17 is about *variance generation per capita*, not about cumulative skill preservation, and would predict the scale at which insulation stops helping (when loss of access to necessary prior complexity outweighs gain in local normative freedom).

A methodologically minimal starting architecture: **ResearchTown** (Yu et al. 2024, arXiv:2412.17767) as the agent-graph scaffold, **AutoGen or CAMEL** as infrastructure, **Chuang et al. 2024 opinion-dynamics topology** for the peer-interaction module, **Park 2024** 1,052-persona conditioning (or simpler synthetic personas) for demographic plurality, **SPECTER2 / text-embedding-3** embeddings for semantic novelty measurement, **AgentRxiv** pattern for a shared-catalog actuator, with two critical ablation knobs: (a) fraction of agents sharing an LLM backbone (tests 13-A) and (b) external-attention budget of each subgroup (tests 17-C). This combination does not exist in published work.

## 4. Datasets and empirical anchors for companion meta-analyses

For Claim #13, the most actionable datasets are:
- **OpenAlex** (free, CC0, ~250M works) — the primary successor to MAG. Provides authorship demographics + citations.
- **SciSciNet** (Lin et al. 2023, *Scientific Data* 10:315) — 134M publications linked to funding, patents, clinical trials, Altmetric; precomputed CD, Q-values, hit-paper flags. Best single starting point for reproducing Wu-Wang-Evans, Park-Leahey-Funk, Chu-Evans.
- **Semantic Scholar S2ORC / S2AG** — ~200M papers, full-text for ~81M, SPECTER2 embeddings via API.
- **CrossDI** (2025 Nature Sci. Data) — cross-source disruption-index dataset across WoS, Dimensions, OpenCitations. Enables Petersen/Holst-style robustness.
- **USPTO / PatentsView** — ~10M patents for Park-Leahey-Funk replication.
- **UNESCO Index Translationum** — ~1.3M records for translation-asymmetry analysis (caveat: frozen ~2012).
- **Million Song Dataset + AcousticBrainz + Spotify API** — for music-homogenization time series.
- **Cutting et al. film corpus** (160 films annotated) for film-style convergence; Comscore for franchise-share trends.
- **GDELT / Media Cloud** — for news-similarity embedding analysis.
- **WALS (World Atlas of Language Structures)** — for Lupyan-Dale linguistic-niche replication.
- **arXiv + SPECTER2 embeddings** — for pre-publication idea-flow analysis.
- **Mathematics Genealogy / NeuroTree / Academic Family Tree** — for advisor-advisee lineage analysis as proxy for "trust network."

For Claim #17, layered on the same scientometric infrastructure:
- **HHMI investigator rosters + matched NIH R01 recipients** (Azoulay et al. reproduction material).
- **Bell Labs and Xerox PARC patent/publication data** (USPTO + DBLP + ACM DL) for quantitative per-capita benchmarking — the Simonton-style work that has never been done.
- **SFI working-paper archive** and **IAS School of Natural Sciences publication records** for heterodox-institute benchmarking.
- **Moser-Voena-Waldinger replication data** for émigré chemistry fields on USPTO.
- **DBLP** for CS-specific short-cycle team-formation analysis.
- **APS Data Set** (~650k physics papers, ~10M citations) for physics career/team studies.

## 5. Methodological precedents — recommended templates

The five most transferable simulation architectures, in priority order:

1. **ResearchTown (Yu et al. 2024, arXiv:2412.17767)** with TextGNN message-passing on a heterogeneous agent-data graph — the single best existing template for an LLM-agent research community. Open code. Directly extensible with actuator and insulation knobs.
2. **Fang, Lee & Schilling 2010** (*Organization Science* 21(3)) semi-isolated-subgroups March-style organizational learning — the closest non-LLM precedent for Claim #17's topology. Extend to one-mainstream-plus-N-subgroups structure.
3. **Chaney, Stewart & Engelhardt 2018** (RecSys) algorithmic-confounding ABM — directly maps recommender-loop homogenization to a cultural/intellectual actuator.
4. **Chuang et al. 2024** (NAACL Findings) LLM-based opinion dynamics — cleanest ablation-ready architecture for actuator-sharing effects.
5. **Barkoczi & Galesic 2016** (*Nature Communications* 7:13109) — essential robustness control showing network effects are strategy-dependent; any Claim #17 simulation must precommit to social-learning rule.

Secondary templates: **Zollman 2007/2010** bandit-network architecture (extends Hong-Page with network structure for science epistemology); **Axelrod 1997 + González-Avella et al. 2005** mass-media extension (classical scaffold for Claim #13); **Guimerà et al. 2005** team-assembly mechanisms with tie-repetition parameter q as internal-trust proxy; **Centola 2018** complex-contagion rules for modeling outward propagation from insulated groups; **STORM (Shao et al. 2024)** for perspective-diversity subroutines; **Dale & Lupyan 2012** (*Adv. Complex Systems*) as a rare existing ABM of linguistic-niche homogenization.

## Conclusion

The simulation-ready whitespace is specific and narrow, which is good news. Claim #13's strongest empirical support comes not from the contested Park-Leahey-Funk decline but from Chu-Evans canonical ossification, Foster-Rzhetsky-Evans conservatism ratios, and the RLHF-diversity-loss literature (Padmakumar-He, Doshi-Hauser, Kirk). Claim #17's strongest support comes from Wu-Wang-Evans, Lin-Frey-Wu, Azoulay-Manso HHMI, Moser-Voena-Waldinger émigrés, and Zollman's network-epistemology ABMs. The challenging orthodoxy is Henrich-Powell's population-size-helps-complexity tradition, which a well-designed simulation can accommodate by decomposing preservation from variance-generation fitness.

The eight pathways per claim are **deliberately overspecified** — several will collapse into each other or into confounds once functional forms are committed. The three predictions most worth precommitting to, before structural equations, are:
- For Claim #13, that a simulation can reproduce the demographic-vs-intellectual plurality gap purely by varying actuator sharing, *without* changing agent-population demographic composition.
- For Claim #17, that per-capita originality is inverted-U in external-contact rate at fixed size and trust, and that this curve shifts with task complexity (landscape ruggedness).
- For both claims jointly, that the Park-Leahey-Funk decline is reproducible under a *measurement-artifact-only* null (Petersen-Holst-Macher), so any mechanism explanation must out-predict that null on a separate target (e.g., semantic-embedding variance, not CD-index).

These are the precommitments worth making before writing structural equations. The next step the user indicated — concrete DAG discussion — should focus on which edges are load-bearing for each pathway, which nodes are measurable in simulation output vs. only in data, and which confounders (selection, survivorship, measurement) must be instrumented in the simulation design rather than assumed away.