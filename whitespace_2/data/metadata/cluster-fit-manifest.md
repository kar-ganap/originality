# Cluster-fit manifest (per Phase 0.1 plan §11)

**Run date:** 2026-04-28
**Mode:** full
**KMeans config:** random_state=46, n_init=20, max_iter=300

## Stratified pool S
- |S| = 316 rows; pulled per decade (1970s-2020s).
- Source parquet: `data/metadata/check5bd-stratified-pool.parquet`.
- Per-decade counts: {1970: 35, 1980: 32, 1990: 36, 2000: 61, 2010: 72, 2020: 80}

## Unstratified pool U (comparison only)
- |U| = 600 rows; OpenAlex `?sample=600` over 1970-2024.
- Source parquet: `data/metadata/check5bd-unstratified-pool.parquet`.

## Centroid arrays (one .npy per K × per fit)
- `data/metadata/cluster-fit-manifest-{S,U}-K30.npy` — shape (30, 768); inertia_S=37.20, inertia_U=72.31
- `data/metadata/cluster-fit-manifest-{S,U}-K50.npy` — shape (50, 768); inertia_S=32.09, inertia_U=66.24
- `data/metadata/cluster-fit-manifest-{S,U}-K100.npy` — shape (100, 768); inertia_S=22.92, inertia_U=54.73

## §11 production rule
The S-fit centroids at K=50 are the canonical cluster manifest. Every paper in the production corpus is assigned to its nearest centroid from this fit. The U fit is comparison-only — used to quantify the artifact §11 prevents (Check 5d).
