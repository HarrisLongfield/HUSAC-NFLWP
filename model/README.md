# Included win probability model

The two `.rda` files in this directory are the current open-source model artifacts from [nflverse/fastrmodels](https://github.com/nflverse/fastrmodels):

- `wp_model.rda` — nflfastR's non-spread-adjusted win probability model.
- `wp_model_spread.rda` — nflfastR's spread-adjusted win probability model.

`MODELS.R` is the upstream model data/build source. `UPSTREAM_COMMIT.txt` records the exact upstream commit used for the copy. The upstream license is included as `UPSTREAM_LICENSE.md`.

The full `nflfastR` calculation package is downloaded separately under `external/` by `scripts/download_nflfastR_assets.sh`, but the model artifacts above are tracked in this repository so the GitHub repo contains the model itself.
