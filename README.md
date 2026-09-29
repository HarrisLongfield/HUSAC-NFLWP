# NFL win probability 

This project uses the open-source `nflfastR` win probability model as a starting point for model building. It downloads the upstream model package and season-level NFL play-by-play data in parquet format, then trains and evaluates a compact XGBoost teaching model.

## Project layout

- `model/` — tracked copies of the two upstream WP model artifacts and their upstream build source.
- `external/` and `data/raw/pbp/` — downloaded upstream checkouts and PBP inputs. They are intentionally ignored by git.
- `scripts/download_nflfastR_assets.sh` — repeatable bootstrap/download script.
- `notebooks/train_wp.ipynb` — end-to-end preprocessing, feature engineering, XGBoost training, evaluation, and artifact export.
- `evals.py` — reusable BSS/AUC/KS metrics and expected-vs-actual calibration plot.
- `artifacts/` — saved XGBoost model JSON and feature manifest produced by the notebook.
- `results/` — generated evaluation tables and plots; intentionally ignored by git.

## Start here

The default downloads all seasons from 1999 through the current calendar year; an in-progress season is skipped if no parquet file has been published yet.

```sh
./scripts/download_nflfastR_assets.sh
```

To choose a smaller or different range:

```sh
./scripts/download_nflfastR_assets.sh 2010 2025
```

The season files are the standard nflverse play-by-play data and include regular-season and postseason games. The PBP release is maintained by nflverse and the model source is maintained under the nflverse GitHub organization; see the source links in the script and upstream repositories for licensing and attribution details.

## Evaluate predictions

`evals.py` is both the notebook's evaluation module and a small CSV command-line tool. Given a CSV with `target` and `prediction` columns:

```sh
python3 -m pip install -r requirements.txt
python3 evals.py predictions.csv --plot results/calibration.png
```

The command reports Brier Skill Score, ROC AUC, KS, Brier score, and log loss, and can save the expected-probability-versus-actual calibration plot. The notebook calls the same `evaluate_predictions()` function directly.

## Train or change the teaching model

After installing `requirements.txt`, open `notebooks/train_wp.ipynb` in JupyterLab. The notebook uses season-level train/validation/test splits, keeps final outcome fields out of the features, trains an `XGBClassifier`, calls `evals.py` for BSS/AUC/KS and calibration, and saves `artifacts/wp_xgboost.json` plus `artifacts/feature_schema.json`. Generated tables and plots under `results/` remain local.

## Upstream sources

- Model package: <https://github.com/nflverse/fastrmodels>
- Calculation package: <https://github.com/nflverse/nflfastR>
- PBP releases: <https://github.com/nflverse/nflverse-data/releases/tag/pbp>
