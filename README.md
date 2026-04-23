# Originality

A research program on intellectual plurality: why original thought is hard,
why it has arguably become harder despite rising demographic diversity, and
whether small insulated groups produce disproportionate originality.

## Structure

```
originality/
├── CLAUDE.md                           Program orientation, ground rules
├── docs/program/
│   ├── desiderata.md                   Immutable program principles
│   ├── research_program_overview.md    How the program was narrowed from a broader conversation
│   ├── originality_deepresearch_markdown.md  Literature review + pathway DAGs
│   └── pathway_lineage_tables.md       Reference tables: pathways → research lineages
├── whitespace_1/                       LLM multi-agent simulation (future)
├── whitespace_2/                       Empirical decomposition study (ACTIVE)
└── whitespace_3/                       Theoretical reconciliation paper (future)
```

Each whitespace is an independent subproject with its own `pyproject.toml`,
`Makefile`, `CLAUDE.md`, `docs/`, `tasks/`, `src/`, and `tests/`. They do not
share a lockfile.

## Active Work

**Whitespace 2** — empirical time-series study of ~5–10M OpenAlex CS papers
(1970–2024): do demographic plurality, semantic plurality, and canonical
concentration diverge over time? Target: 3–5 months, $50–500 compute.

```bash
cd whitespace_2
uv sync --extra dev
make test
```

See `whitespace_2/CLAUDE.md` for the study thesis, stage map, and current phase.

## Order of Whitespaces

Studies are ordered by ascending cost/risk, with each prior study de-risking
the next:

1. **Whitespace 2** (empirical, ~$500) — establishes whether the central
   decoupling claim holds in observable data.
2. **Whitespace 3** (theoretical, ~$0) — formalizes the tension between
   cumulative preservation and per-capita variance generation.
3. **Whitespace 1** (simulation, higher cost) — agent-based model of actuator
   homogenization, activated once the empirical and theoretical grounding is in
   place.

## House Rules

See `CLAUDE.md` (program) and `docs/program/desiderata.md` (immutable
principles). Each whitespace has its own `CLAUDE.md` and `docs/desiderata.md`
that extend these.
