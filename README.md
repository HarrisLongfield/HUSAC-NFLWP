# NFL win probability teaching demo

This project uses the open-source `nflfastR` win probability model as a starting point for teaching model building. It downloads the upstream model package, the `nflfastR` calculation code, and season-level NFL play-by-play data in parquet format.

## Project layout

- `model/` — tracked copies of the two upstream WP model artifacts and their upstream build source.
- `external/fastrmodels/` — upstream model artifacts, including `wp_model.rda` and `wp_model_spread.rda`.
- `external/nflfastR/` — upstream R package source, including `calculate_win_probability()`.
- `data/raw/pbp/` — one `play_by_play_<season>.parquet` file per season. These files are intentionally ignored by git.
- `scripts/download_nflfastR_assets.sh` — repeatable bootstrap/download script.
- `scripts/evaluate_wp.py` — scores the published `wp` and `vegas_wp` columns and writes Brier/log-loss/calibration results.

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

## Upstream sources

- Model package: <https://github.com/nflverse/fastrmodels>
- Calculation package: <https://github.com/nflverse/nflfastR>
- PBP releases: <https://github.com/nflverse/nflverse-data/releases/tag/pbp>
