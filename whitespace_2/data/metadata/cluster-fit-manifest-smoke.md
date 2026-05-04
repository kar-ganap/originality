# Cluster-fit manifest (per Phase 0.1 plan §11)

**Run date:** 2026-04-28
**Mode:** smoke
**KMeans config:** random_state=46, n_init=20, max_iter=300

## Stratified pool S
- |S| = 60 rows; pulled per decade (1970s-2020s).
- Source parquet: `data/metadata/check5bd-stratified-pool-smoke.parquet`.
- Per-decade counts: {1970: 10, 1980: 10, 1990: 10, 2000: 10, 2010: 10, 2020: 10}

## Unstratified pool U (comparison only)
- |U| = 60 rows; OpenAlex `?sample=600` over 1970-2024.
- Source parquet: `data/metadata/check5bd-unstratified-pool-smoke.parquet`.

## Centroid arrays (one .npy per K × per fit)
- `data/metadata/cluster-fit-manifest-{S,U}-K10-smoke.npy` — shape (10, 768); inertia_S=7.23, inertia_U=7.59
- `data/metadata/cluster-fit-manifest-{S,U}-K25-smoke.npy` — shape (25, 768); inertia_S=4.14, inertia_U=4.44
- `data/metadata/cluster-fit-manifest-{S,U}-K50-smoke.npy` — shape (50, 768); inertia_S=0.61, inertia_U=0.79

## §11 production rule
The S-fit centroids at K=50 are the canonical cluster manifest. Every paper in the production corpus is assigned to its nearest centroid from this fit. The U fit is comparison-only — used to quantify the artifact §11 prevents (Check 5d).
