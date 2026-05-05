# ORCID-linkage hand-audit — workflow guide

**Phase 0.2 Wave 3A.** Print-friendly companion to use alongside
`orcid-linkage-audit-input.csv`.

---

## Goal

Validate OpenAlex's ORCID linkage on 100 sampled author records.
For each row, decide whether the OpenAlex `author → orcid_url`
linkage is correct (`yes` / `likely`) or not (`no`), or whether
the profile is too sparse to determine (`unclear`).

Aggregator uses **Reading B**: rate = (yes + likely) / (yes +
likely + no). Unclear is excluded — "couldn't determine" is
neither evidence of correct nor incorrect linkage.

§4 thresholds:
- Overall ≥ 70%
- Per-region ≥ 50% (heuristic regions; you can re-classify
  during audit if needed)

Failure → §9a P5 methodology re-opens; trigger plan-revision.

---

## File to open

`whitespace_2/experiments/phase-0.2/orcid-linkage-audit-input.csv`

100 rows. Currently empty `linkage_correct` and `notes` columns.

## Recommended viewer

| Tool | Pros | Cons |
|---|---|---|
| **Numbers (macOS)** | Wide columns, clickable URLs, native CSV | Auto-imports as .numbers; export back to CSV |
| **VS Code + "Edit csv" extension** | Stays as CSV; no conversion | Need to install extension |
| **Google Sheets** | Collaboration; clickable URLs | Upload + re-download dance |
| Excel | Familiar | Mangles long IDs / URLs by default — avoid |

If using Numbers: when you finish, **File → Export → CSV** back
to the same path. Make sure the column order is preserved.

## Columns to keep visible (hide the rest)

| Column | What it is | Use |
|---|---|---|
| `orcid_url` | https://orcid.org/0000-... | Click to open profile |
| `openalex_display_name` | OA's view of the author's name | Compare to ORCID |
| `orcid_full_name` | ORCID's stored name | Compare to OA |
| `name_similarity` | 0–1 fuzzy match score | Pre-computed |
| `openalex_institutions` | Pipe-separated institutions | Compare to ORCID |
| `orcid_employments` | ORCID employment history | Compare to OA |
| `orcid_educations` | ORCID education history | Backup match |
| `institution_match` | bool (≥0.6 fuzzy) | Pre-computed |
| `institution_best_pair` | Best fuzzy-match pair | Inspection |
| `openalex_paper_doi` | Paper's DOI | For ORCID works lookup |
| `publication_doi_match` | bool: DOI in ORCID works? | Pre-computed |
| `orcid_n_works` | Total works on profile | Profile depth proxy |
| **`linkage_correct`** | **YOU FILL** | yes / likely / unclear / no |
| `notes` | optional | Flag interesting cases |

Hide: work_id, region_heuristic (unless you want to track per-region
during audit), openalex_pub_year, openalex_field_cell_year,
fetch_error.

---

## Decision rule per row

```
Step 1 — Name match (5 sec)
  Does openalex_display_name ≈ orcid_full_name?
  If clearly different person → mark `no`. Move on.
  If similar/identical → continue.

Step 2 — Open the ORCID profile
  Click orcid_url.

Step 3 — Look for the paper in ORCID's "Works" section
  Search by paper title or DOI.
  If found → `yes`. Done.

Step 4 — If paper NOT found, check career plausibility
  - Year match: is paper's year inside author's career window?
    (Education start year onward, or first work year)
  - Field match: scan 5–10 ORCID work titles. Same field?
  - Institution match: do openalex_institutions overlap with
    orcid_employments / orcid_educations?

  All three pass → `likely`
  Most pass, one ambiguous → `likely` or `unclear` (your call)
  Conflict (different field / different era) → `no`
  Profile too sparse to tell (orcid_n_works < 5, no employments,
  no education) → `unclear`
```

---

## Cheat sheet — fast lookup

| Pattern | Verdict | Time/row |
|---|---|---:|
| Name match + DOI in ORCID works | `yes` | ~10s |
| Name very distinctive ("Mariusz Eichberger") + name match | `likely` no profile open needed | ~5s |
| Common name + paper in ORCID works | `yes` | ~30s |
| Common name + paper NOT in works + career/field plausible | `likely` | ~60s |
| Common name + career/field clearly different | `no` | ~60s |
| Profile sparse (< 3 works, no career) | `unclear` | ~30s |
| Name doesn't match | `no` | ~5s |

---

## Common patterns to watch for

### 1. Common East-Asian names (Takashi Kobayashi, Wei Wang, In Seok Kang, etc.)

These were the bulk of the earlier conservative-LLM-pass `unclear`
calls. Profile inspection usually resolves:
- Profile genuinely empty (no works, no career listed) → `unclear`
- Profile has 50+ works in same field as the OA paper → `likely`
- Profile populated but in totally different specialty (e.g., OA paper
  is distributed systems; ORCID is for a different person doing
  molecular biology) → `no`

### 2. OpenAlex over-merge (Culbert 2025)

OA conflates same-name authors more aggressively than ORCID. Watch
for cases where name matches but the ORCID's career trajectory
doesn't fit the paper at all. Mark `no`.

### 3. Honest paper-not-in-ORCID-list

Many real authors don't bother to populate ORCID with all their
works. If career history + field strongly match, `likely` is
correct even without paper-level confirmation.

### 4. Recent ORCID, old paper

Paper from 1995, ORCID profile shows career started 2010.
- Could be a different person who happens to share the name → `no`
- Could be back-propagated linkage that may or may not be correct
  — use the rest of the profile to judge
- If profile sparse, default to `unclear`

### 5. Empty ORCID profiles

Registered but never populated. Hard to verify either way.
- If author behavior is consistent (e.g., paper from author's
  known institution at known year) → `unclear` (lean
  toward the linkage being correct but you can't prove it)
- If anything conflicts → `no`

---

## Pacing strategy

- **5 min — Cheap `yes` first pass.** Sort by `name_similarity` desc.
  Filter to rows where `institution_match=True` AND
  `publication_doi_match=True`. There are ~8 of these. Mark all
  `yes` without opening profiles. (One-line spot-check on first 2
  to verify pattern.)

- **5 min — Cheap `no` first pass.** Filter to rows where
  `name_similarity < 0.5` AND `institution_match=False` AND
  `publication_doi_match=False`. There are ~7 of these. Mark all
  `no` without opening profiles.

- **30–50 min — Bulk pass.** The remaining 85 rows. ~30–45 sec
  per row. Open ORCID URL, scan profile, decide.

**Save the CSV every 20–30 rows.** Numbers/Excel/Sheets crash
recovery isn't great.

---

## Sanity check mid-audit

```
cd whitespace_2
uv run python experiments/phase-0.2/orcid_linkage_aggregate.py
```

Will warn about empty rows (expected, since you're not done) and
show running totals. Use as a "am I way off track?" check halfway.

If the running rate is wildly different from your expectation
(e.g., 30% when you thought 80%), pause and re-check the first
few rows you marked.

---

## When done

```
cd whitespace_2
uv run python experiments/phase-0.2/orcid_linkage_aggregate.py
```

Produces:
- Stdout: overall + per-region rates with PASS/FAIL
- `experiments/phase-0.2/orcid-linkage-aggregate.md`
- `experiments/phase-0.2/orcid-linkage-aggregate-summary.json`

Ping me when done. I'll commit the audit + aggregate, fold any
methodology learnings into the artifact, and we proceed to Wave 5
close-out.

---

## Reference: methodology decision (Reading B is locked)

| Reading | Definition | Rate denominator | Status |
|---|---|---|---|
| A | Unclear treated as failure | yes + likely + no + unclear | Not used |
| **B** | **Unclear excluded entirely** | **yes + likely + no** | **Locked** |

Reading B rationale: "couldn't determine" is neither evidence of
correct linkage nor evidence of incorrect linkage. Putting it in
the denominator implicitly classifies ignorance as error.
Excluding it produces the rate over decisively-audited cases,
with the unclear count reported separately as residual
uncertainty.

---

## Workflow troubleshooting

### "I edited in Numbers and now my CSV looks weird"

Numbers' default export adds quotes around all string fields.
That's fine — pandas reads them correctly. Confirm by re-opening
in any text editor.

### "I lost my place"

Run the aggregator. It tells you `unaudited rows: N` so you know
how many remain.

### "I can't tell if it's the right person and the profile is empty"

Default to `unclear`. The aggregator excludes it from rate; it
only contributes to the residual-uncertainty count.

### "Two rows look like the same author"

It's possible — the random sample doesn't enforce author uniqueness.
Audit each row independently. If both have the same ORCID URL
opening to the same profile, your decision should be the same
on both.

### "An ORCID URL gave me a 404"

Mark `notes` with `404` and `linkage_correct` with `no`. ORCID URLs
shouldn't 404 unless the ORCID was deleted (rare). The pre-fetch
script logged 0 errors, but if one shows up at audit time, that's
flagged.
