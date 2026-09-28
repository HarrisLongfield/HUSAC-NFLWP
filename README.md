# NFL win probability teaching demo

This project uses the open-source `nflfastR` win probability model as a starting point for teaching model building. It downloads the upstream model package, the `nflfastR` calculation code, and season-level NFL play-by-play data in parquet format.

## Project layout

- `model/` — tracked copies of the two upstream WP model artifacts and their upstream build source.
- `external/fastrmodels/` — upstream model artifacts, including `wp_model.rda` and `wp_model_spread.rda`.
- `external/nflfastR/` — upstream R package source, including `calculate_win_probability()`.
- `data/raw/pbp/` — one `play_by_play_<season>.parquet` file per season. These files are intentionally ignored by git.
- `scripts/download_nflfastR_assets.sh` — repeatable bootstrap/download script.
- `scripts/evaluate_wp.py` — scores the published `wp` and `vegas_wp` columns and writes Brier/log-loss/calibration results.
- `notebooks/train_wp.ipynb` — end-to-end preprocessing, feature engineering, XGBoost training, evaluation, benchmarking, and artifact export.
- `evals.py` — reusable BSS/AUC/KS metrics and expected-vs-actual calibration plot.
- `artifacts/` — saved XGBoost model JSON and feature manifest produced by the notebook.

## Start here

The default downloads all seasons from 1999 through the current calendar year; an in-progress season is skipped if no parquet file has been published yet.

```sh
./scripts/download_nflfastR_assets.sh
```

To choose a smaller or different range:

```sh
./scripts/download_nflfastR_assets.sh 2010 2025
```

The season files are the standard nflverse play-by-play data and include regular-season and postseason games. The PBP release is maintained by nflverse and the model/package source is maintained under the nflverse GitHub organization; see the source links in the script and upstream repositories for licensing and attribution details.

## Evaluate the downloaded model outputs

Install the one Python dependency and run the evaluator over every local season:

```sh
python3 -m pip install -r requirements.txt
python3 scripts/evaluate_wp.py
```

The script evaluates nflfastR's `wp` (no spread) and `vegas_wp` (spread-adjusted) predictions against the eventual game winner, excluding ties because they do not have a binary winner label. It writes `results/wp_evaluation.csv` and `results/wp_calibration.csv`. Use `--seasons 2020 2021` to evaluate a smaller range or `--predictions wp` to score only one column.

## Train or change the teaching model

After installing `requirements.txt`, open `notebooks/train_wp.ipynb` in JupyterLab. The notebook uses season-level train/validation/test splits, keeps final outcome fields out of the features, trains an `XGBClassifier`, calls `evals.py` for BSS/AUC/KS and calibration, benchmarks the published nflfastR columns, and saves `artifacts/wp_xgboost.json` plus `artifacts/feature_schema.json`.

## Upstream sources

- Model package: <https://github.com/nflverse/fastrmodels>
- Calculation package: <https://github.com/nflverse/nflfastR>
- PBP releases: <https://github.com/nflverse/nflverse-data/releases/tag/pbp>
