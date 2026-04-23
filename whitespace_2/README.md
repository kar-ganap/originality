# Whitespace 2: Demographic vs. Semantic Plurality

Empirical decomposition of three annual time series over ~5–10M OpenAlex CS
papers (1970–2024):

1. **Demographic diversity** — inferred gender, nationality, career stage,
   institutional prestige of authors.
2. **Semantic diversity** — embedding-based novelty/spread of paper content
   (SPECTER2 primary, second model for robustness).
3. **Canonical concentration** — citation concentration among the top-N
   papers per year.

**Central question:** do (1) and (2) diverge over time? If so, that empirically
supports the program's claim that intellectual plurality has decoupled from
demographic plurality. If they track, the claim is disconfirmed — a successful
null.

## Quick Start

```bash
uv sync --extra dev
make test
make lint
make typecheck
```

For embedding work add `--extra embed`; for plotting add `--extra plot`.

## Pipeline (drafted; see `docs/conceptual.md` for full detail)

1. **Fetch** — OpenAlex bulk dump, stratified sample by year × field concept.
2. **Author disambiguation + demographic inference** — gender-guesser, country
   from affiliation, prestige from public rankings.
3. **Embed** — SPECTER2 on abstracts (local), plus one alternative family for
   robustness.
4. **Metrics** — ≥2 metrics each for demographic, semantic, canonical
   concentration (see `docs/desiderata.md` §8).
5. **Time-series analysis** — annual binning, divergence test (pre-registered
   in phase plan).
6. **Robustness** — cross-field (Physics), embedding swaps, metric variants,
   subfield mechanism test.
7. **Paper** — 3-panel figure, robustness table, methods + limitations.

## Cost & Timeline

- **Budget:** $50–500 (embedding API calls + optional paid demographic services)
- **Timeline:** 3–5 months at ~15 hrs/week
- **Compute:** Apple M-series local; SPECTER2 embeddings run on CPU/MPS over
  ~4 days for the full sample.

## Repo Layout

```
whitespace_2/
├── CLAUDE.md                 Study thesis, stage map, ground rules
├── docs/
│   ├── conceptual.md         North star (moved from whitespace_2_compass.md)
│   ├── desiderata.md         Immutable principles for this study
│   └── phases/               phase-X.Y-plan.md and phase-X.Y-retro.md
├── src/whitespace2/          Pipeline modules
├── tests/                    Unit tests for metrics, embedding, inference
├── data/                     Raw + derived data (gitignored except README/metadata)
├── experiments/              Experiment runs (results/logs gitignored)
├── literature-review/        Supporting reading (PDFs gitignored)
└── tasks/                    todo.md, lessons.md, spend.md (gitignored)
```

## Status

**Stage 0 — Foundation.** Scaffold complete. Next: phase-0.1-plan.md
(OpenAlex scoping + field/concept ID definitions).

## References

- `CLAUDE.md` — navigation + ground rules
- `docs/desiderata.md` — immutable principles
- `docs/conceptual.md` — full study compass
- `../docs/program/` — program-level context
