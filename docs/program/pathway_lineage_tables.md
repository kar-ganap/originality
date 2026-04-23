# Pathway Lineage Tables for Claims #13 and #17

**A companion document to the deep research report, mapping each causal pathway to its supporting research lineages and key works.**

---

## What this document is

For each of the 16 causal pathways identified across Claims #13 and #17 (8 per claim), this document identifies:

- The primary research lineage(s) — the scholarly communities whose work most directly supports the pathway.
- The key works within each lineage.

The purpose is twofold. First, to make the empirical support for each pathway legible at a glance, so that when building a simulation or writing a paper, the load-bearing references are recoverable. Second, to make the natural reviewer pool for any resulting paper legible in advance, so that writing can engage those reviewers' prior work explicitly and pre-empt their critiques.

Two structural observations worth noting before the tables:

First, the lineages are **heavily concentrated in a few research programs**. For Claim #13, the Evans lab (Chu & Evans, Foster-Rzhetsky-Evans), the Kleinberg-Bommasani algorithmic-monoculture cluster, and the HHMI economics-of-science cluster (Azoulay and collaborators) do disproportionate load-bearing work. For Claim #17, the Wu-Wang-Evans collaboration, the Nemeth dissent tradition, the Zollman-Grim epistemic-networks tradition, and the Hong-Page-Burt organizational-diversity cluster dominate. This concentration is useful signal: these are the groups whose work any new contribution must engage with seriously, and they are the natural reviewers for submissions.

Second, pathways 13-F and 17-H — the **null/measurement-artifact pathways** — are supported by *critique literatures* rather than primary research programs. These are literatures that exist specifically to contest the mainstream claims. Including them as precommitted branches in a simulation is not just methodological hygiene; it is substantively responsive to the strongest extant criticism. Reviewers from those lineages will test whether you have taken their critique seriously, and including the nulls as explicit pathways rather than afterthoughts is the most defensible response.

## Claim #13: Intellectual plurality has declined despite demographic plurality rising

The claim: despite the rising demographic diversity of who produces intellectual work, the intellectual diversity of what gets produced has narrowed, because shared "actuators" (platforms, canonical texts, institutional filters, formative pipelines) flatten outputs even when inputs are diverse.

### Pathway-by-pathway lineage table

| Pathway | Primary supporting lineage(s) | Key works |
|---|---|---|
| **13-A** Channel / recommender convergence | Algorithmic monoculture theory; information retrieval; recent LLM-homogenization research | Chaney, Stewart & Engelhardt 2018 (RecSys); Kleinberg & Raghavan 2021 (PNAS 118(22), "Algorithmic monoculture and social welfare"); Bommasani et al. 2022 (NeurIPS, "Picking on the Same Person"); Padmakumar & He 2024 (ICLR, "Does Writing with Language Models Reduce Content Diversity?"); Doshi & Hauser 2024 (Science Advances 10, eadn5290); Kirk et al. 2024 (ICLR, RLHF diversity effects); Anderson, Shah & Kreminski 2024 (C&C, LLM creative ideation homogenization) |
| **13-B** Demographic diversification as cosmetic | Sociology of diversity; diversity-innovation scholarship; diversity management research | Hofstra et al. 2020 (PNAS, "Diversity-Innovation Paradox"); Page 2007, 2017 (cognitive-vs-identity diversity distinction); Kalev & Dobbin 2006 (on diversity-program evaluation failures); Scott Page corpus generally |
| **13-C** Institutional selection pressure | Economics of science and creativity; Mertonian sociology of science; critique-of-science literature | Azoulay, Graff Zivin & Manso 2011 (RAND J. Econ. 42, "Incentives and Creativity," HHMI vs. NIH); Manso 2011 (J. Finance, on tolerance for failure); Foster, Rzhetsky & Evans 2015 (ASR 80(5), "Tradition and Innovation"); Packalen & Bhattacharya 2019 (on novelty and career incentives); Smaldino & McElreath 2016 (Royal Soc. Open Sci., "Natural selection of bad science"); Merton 1968 (Science 159, "Matthew Effect"); Bourdieu 1984 *Homo Academicus* |
| **13-D** Network-topology-driven convergence | Network science; scientometrics of attention concentration | Barabási 1999 (preferential attachment); Chu & Evans 2021 (PNAS 118(41), canonical ossification at field scale); Uzzi & Spiro 2005 (AJS, small-world creativity inverted-U); Centola & Macy 2007 (complex contagion); Bornmann 2021 (QSS, updated Matthew effect analysis) |
| **13-E** Translation / linguistic asymmetry | Sociology of translation; world-literature studies; linguistic-niche analysis | Heilbron 1999 (European Journal of Social Theory, "Towards a Sociology of Translation"); Casanova 2004 *The World Republic of Letters*; Gordin 2015 *Scientific Babel*; UNESCO Index Translationum (primary data source, ~1.3M records through ~2012); Lupyan & Dale 2010 (PLOS One, "Language Structure Is Partly Determined by Social Structure"); Dale & Lupyan 2012 (Adv. Complex Systems, ABM of linguistic niche) |
| **13-F** Measurement artifact (null) | Critique of disruption-index literature; scientometrics methodology debate | Petersen, Arroyave & Pammolli 2024 (QSS 5(4), CD-index citation-inflation critique); Holst, Algaba et al. 2024 (arXiv:2402.14583, dataset-artifacts critique of Park-Leahey-Funk); Macher et al. 2024 (Research Policy, patent-disruption truncation correction); Leibel & Bornmann 2024 (Scientometrics 129(1), multiverse robustness analysis); Ruan et al. (methodological critiques of CD index) |
| **13-G** Cognitive / psychological conformity pressure | Social psychology of conformity; minority-influence research; social-media empirical work | Asch 1956 (conformity classics); Nemeth 1986 (minority influence); Nemeth 2018 (*In Defense of Troublemakers*); Mäs & Flache 2010 (individualization and clustering); Salganik, Dodds & Watts 2006 (Science, Music Lab, Gini 0.21 → 0.50 under social influence); Bakshy et al. 2015 (Science, filter bubble empirics); Moscovici (minority influence foundational) |
| **13-H** Endogenous actuator emergence | Tipping-point / critical-mass literature; co-evolving network ABMs; sociology of canon formation | Centola et al. 2018 (Science, 25% critical-mass tipping point); Centola-González-Avella-Eguíluz-San Miguel 2007 (co-evolving network dynamics); Collins 1998 *The Sociology of Philosophies*; Guillory 1993 *Cultural Capital* (canon formation sociology) |

### Reading the Claim #13 table

Notice that 13-A's lineage is overwhelmingly **recent** (2018-2024), reflecting that the specific mechanism — algorithmic or foundation-model-driven homogenization — is a contemporary phenomenon with a correspondingly young literature. Any simulation of 13-A inherits the conceptual machinery of this young literature and should cite heavily within it.

13-C and 13-D rest on **longer, more established lineages** going back to Merton and Barabási respectively. Simulations of these pathways have deeper historical grounding but face the challenge that decades of prior work have to be engaged with.

13-E is **under-cited in science-of-science work** and mostly lives in translation studies and sociolinguistics. A paper that brings 13-E into a scientometric conversation has novelty value precisely because the bridging rarely happens.

13-F is a **contested methodological debate** — the Park-Leahey-Funk decline vs. the Petersen-Holst-Macher critiques. Any simulation that purports to reproduce declining disruption must take a position on this debate or show that its findings are robust to either side being correct.

## Claim #17: Small protected groups produce disproportionate per-capita originality

The claim: small groups with external insulation and some combination of internal trust, duration, and cognitive diversity produce more originality per person-year than larger or less protected groups.

### Pathway-by-pathway lineage table

| Pathway | Primary supporting lineage(s) | Key works |
|---|---|---|
| **17-A** Size effect | Science-of-science team dynamics; group productivity psychology | Wu, Wang & Evans 2019 (Nature 566, "Large teams develop and small teams disrupt"); Lin, Frey & Wu 2023 (Nature 623, "Remote collaboration fuses fewer breakthrough ideas"); Paulus & Nijstad 2003 *Group Creativity* (review volume, productivity-loss findings); Brooks 1975 *The Mythical Man-Month* (coordination cost); Uzzi et al. 2013 (Science, atypical combinations and team performance) |
| **17-B** Internal trust / permissive filter | Minority-influence psychology; heterarchy theory; LLM multi-agent research | Nemeth 1986 (differential contributions of majority/minority); Nemeth 2018 *In Defense of Troublemakers*; Peterson & Nemeth 1996 (Sage, focus vs. flexibility and dissent); Stark 2009 *The Sense of Dissonance* (heterarchy and dissonance); Swanson et al. 2024 (Nature, "Virtual Lab" critic-agent architecture) |
| **17-C** External insulation | Philosophy of science epistemic networks; organizational learning; peripheral-revolt in world literature | Zollman 2007 (Philosophy of Science, bandit-network epistemics); Zollman 2010 (Erkenntnis, extended analysis); Fang, Lee & Schilling 2010 (Organization Science 21(3), semi-isolated subgroups in March-style learning); Lazer & Friedman 2007 (ASQ 52, "Network Structure of Exploration and Exploitation"); Casanova 2004 (peripheral revolt in world literature); Grim et al. 2013 (epistemic networks and truth-tracking) |
| **17-D** Selection / assortative matching (null) | Quantitative careers literature; individual-ability models | Sinatra et al. 2016 (Science, Q-model of career productivity); Hofstra et al. 2020 (PNAS, diversity-innovation paradox — relevant for who-gets-credit asymmetry); standard selection-effect econometrics literature |
| **17-E** Duration / iterative refinement | Career-trajectory science-of-science; incentive-design economics | Liu et al. 2018 (Nature, "hot streaks" in careers); Azoulay, Graff Zivin & Manso 2011 (HHMI year-4/5 onset of risk-taking effects); Liu et al. 2021 (Nature Communications, hot-streak follow-up); Simonton corpus on creative careers |
| **17-F** Cognitive diversity / Hong-Page | Collective-intelligence / diversity-trumps-ability; landscape-dependence critique | Hong & Page 2001 (Journal of Economic Theory); Hong & Page 2004 (PNAS, "Groups of diverse problem solvers"); Page 2007 *The Difference*; Page 2017 *The Diversity Bonus*; Grim et al. 2019 (landscape-dependence critique of Hong-Page); Barkoczi & Galesic 2016 (Nature Communications 7:13109, strategy-dependent network effects) |
| **17-G** Network bridging / structural holes | Economic sociology; organizational network theory | Burt 1992 *Structural Holes*; Burt 2004 (AJS 110(2), "Structural Holes and Good Ideas"); Burt 2015 (brokerage and closure); de Vaan, Vedres & Stark 2015 (AJS, "Game Changer," structural folding); Granovetter 1973 (AJS, "Strength of Weak Ties"); Uzzi et al. 2013 (atypical combinations — bridges 17-F and 17-G) |
| **17-H** Survivorship bias (null) | Methodological meta-literature; history-of-science case-study critique | Sinatra et al. 2016 (Q-model as implicit null for group-level effects); standard survivorship-bias econometrics; Mesoudi 2011 *Cultural Evolution* (on null model design in cultural-evolution studies); the wider critique of retrospective case-study selection in organizational and scientific history |

### Reading the Claim #17 table

17-A and 17-C have the **strongest quantitative empirical backing** — Wu-Wang-Evans's 65M-paper analysis and Lin-Frey-Wu's 20M-article analysis for 17-A, Zollman's formal bandit-network results and Fang-Lee-Schilling's organizational-learning simulations for 17-C. A simulation testing either of these pathways inherits robust empirical anchors.

17-B and 17-E rest on **shorter but growing literatures**. The LLM multi-agent research (Swanson et al. Virtual Lab) is especially fresh and relevant to 17-B. The hot-streak literature (Liu et al.) is directly relevant to 17-E and is well-cited but still young enough to leave room for extension.

17-F's lineage is **actively contested**. The Hong-Page theorems are mathematically real but Grim et al. 2019's landscape-dependence critique shows they require conditions that may not always hold. Any simulation invoking 17-F must address landscape ruggedness explicitly.

17-G and 17-C are in **partial tension** — brokerage requires connection across groups, while insulation blocks brokerage. The resolution (insulated generation + bridged sourcing — maintaining information flow while blocking normative flow) is a conceptual contribution in its own right, not an established finding.

17-D and 17-H are **nulls supported by methodology rather than primary research programs**. They are the claims that a simulation has to beat, and taking them seriously is a mark of rigor.

## Cross-claim observations

### Shared lineages across both claims

Several research programs contribute to pathways in both Claim #13 and Claim #17:

- **The Evans lab** contributes to 13-D (canonical ossification via Chu-Evans) and implicitly to 17-A (Wu-Wang-Evans on small teams).
- **Uzzi's work** contributes to 13-D (small-world creativity) and 17-G (atypical combinations as bridging).
- **Nemeth's dissent research** contributes to 13-G (minority influence against conformity pressure) and 17-B (dissent as internal-trust mechanism).
- **Centola's complex contagion work** contributes to 13-D (network amplification) and 13-H (tipping dynamics for endogenous actuator emergence).
- **Hofstra et al. 2020** contributes to 13-B (demographic-diversity-as-cosmetic finding) and 17-D (the selection null).

These overlaps mean that a research program addressing both claims jointly (as the full Whitespace 1 would) can cite the same foundational works across multiple pathways, producing a more coherent intellectual genealogy.

### Reviewer pool implications

If any of the whitespace projects is submitted to peer review, the natural reviewer pool concentrates in a predictable way:

- **Expected reviewers across projects**: Evans (Chicago), Wang (Northwestern/Kellogg), Fortunato (Indiana), Uzzi (Northwestern/Kellogg), Azoulay (MIT), Nemeth (Berkeley emerita), Page (SFI/Michigan), Burt (Chicago Booth), Zollman (CMU), Centola (Penn).
- **Critics likely to scrutinize methodology**: Petersen (UC Merced), Holst / Algaba, Macher, Leibel & Bornmann — the CD-index-critique cluster.
- **Bridging reviewers**: Hofstra, Sekara, Sharkey (diversity-innovation); Rendell, Muthukrishna (cultural evolution); Mason, Watts (collective intelligence).

Writing for this audience means engaging their prior work visibly and pre-empting their methodological concerns. This is not strategic flattery — it is the baseline standard for work that intends to contribute to a specific literature.

## When to consult this document

Read or reference this document when:

- Drafting the related-work section of any paper in the research program.
- Building a simulation and needing to identify the specific prior work that a given pathway is responsive to.
- Preparing a pre-emptive defense of methodological choices for peer review.
- Identifying potential collaborators or PI matches for funding conversations.
- Checking whether a newly discovered paper fits into one of the existing pathways or suggests a pathway that has been missed.

The tables are deliberately condensed. The deep research report contains the narrative context for why each lineage matters. This document exists to make the structural mapping easy to recover at a glance.

## Relationship to other documents in the research program

- **Research program overview**: explains why Claims #13 and #17 were selected and how the three whitespaces fit together.
- **Deep research report**: contains the full literature review, pathway narratives, datasets, and methodological precedents.
- **Whitespace 2 compass**: execution guide for the empirical decomposition paper.
- **Whitespace 3 compass**: execution guide for the theoretical reconciliation paper.
- **This document**: the lineage mapping that supports writing, engagement with prior work, and reviewer preparation across all of the above.
