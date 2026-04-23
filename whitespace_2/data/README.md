# Whitespace 2 — Data

## Layout

```
data/
├── README.md                  This file
├── metadata/                  Small, committed, human-authored metadata
│   └── field_definitions.csv  (to be created in Phase 0.1)
├── openalex_raw/              Bulk OpenAlex snapshots (gitignored)
├── s2ag_embeddings/           Precomputed SPECTER2 embeddings (gitignored)
├── arxiv_full_text/           Optional: full-text fallback (gitignored)
└── derived/                   Regenerable parquet aggregates (gitignored)
```

Everything except this README and `metadata/` is gitignored. See
`../.gitignore`.

## Storage conventions

- **Format:** Apache Parquet (columnar, compressed, plays nicely with DuckDB
  and pandas).
- **Partitioning:** by year for large tables; by year × field concept where
  appropriate.
- **Immutability:** raw snapshots are never edited in place (per program
  desiderata §5). Cleaning and derivation always produce new files under
  `derived/`.

## Sources

### OpenAlex

Primary bibliographic and authorship data. Free bulk dump updated roughly
monthly. Pull URL and snapshot date are recorded in
`metadata/field_definitions.csv` (snapshot column) and in every phase plan
that consumes the snapshot.

- Docs: https://docs.openalex.org/
- Bulk dump: https://docs.openalex.org/download-all-data/openalex-snapshot

### S2AG (Semantic Scholar Academic Graph)

Primary source for precomputed SPECTER2 embeddings. Evaluate in Phase 0.1
whether to use precomputed embeddings or run SPECTER2 locally over OpenAlex
abstracts.

- Docs: https://api.semanticscholar.org/
- SPECTER2: https://github.com/allenai/SPECTER2

### arXiv (optional fallback)

Full-text for the subset of CS/Physics papers where abstract-only embedding
is insufficient.

## Do not commit

- Any raw bibliographic dump (too large, regenerable from pinned snapshot).
- Any embedding file (too large, regenerable from pinned model + text).
- Any author-linked personal data beyond what OpenAlex already publishes.
- Copyrighted PDFs (use `../literature-review/` conventions).

## Snapshot pinning

Per `../docs/desiderata.md` §1, every analysis run records the OpenAlex
snapshot date. Use `metadata/field_definitions.csv` as the canonical record.
