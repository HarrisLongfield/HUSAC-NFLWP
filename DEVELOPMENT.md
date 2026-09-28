# Development progress

## 2026-09-28 — initial data/model bootstrap

- Created the teaching-demo project structure.
- Downloaded shallow upstream checkouts of `nflverse/fastrmodels` and `nflverse/nflfastR` under `external/`.
- Copied the two nflfastR win-probability artifacts (`wp_model.rda` and `wp_model_spread.rda`) plus the upstream model-build source into `model/` so the model is part of the GitHub repo.
- Downloaded season-level nflverse PBP parquet files for 1999–2026 into `data/raw/pbp/` (the 2026 file is the current in-progress-season release).
- Added `scripts/evaluate_wp.py`, which scores the published `wp` and `vegas_wp` predictions with Brier score, log loss, Brier skill versus a 50% baseline, and reliability-bin summaries.

### First evaluation snapshot

The first run used all 28 downloaded season files. It scored 1,214,344 valid play-level predictions across 7,305 games (ties excluded):

| Prediction | Brier score | Log loss | Brier skill vs. 50% |
| --- | ---: | ---: | ---: |
| `wp` | 0.1622 | 0.4827 | 0.3513 |
| `vegas_wp` | 0.1485 | 0.4488 | 0.4060 |

These values are a baseline for the teaching demo, not a claim that the two columns are independent predictions: both are the published nflfastR outputs included in the PBP release.

## Next teaching-demo milestones

1. Run the first full evaluation and commit its summary output or a compact excerpt.
2. Add a notebook or lesson that starts with a simple baseline and progressively adds game-state features.
3. Compare the rebuilt teaching model against the published nflfastR predictions on a held-out season.
4. Add clear attribution and a short explanation of the feature engineering and calibration choices.
