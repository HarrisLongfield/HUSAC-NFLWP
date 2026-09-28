#!/usr/bin/env bash
set -euo pipefail

# Download the current open-source nflfastR model code/artifacts and season-level
# nflverse PBP parquet files. Large downloads are kept outside git via .gitignore.

project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
external_dir="$project_root/external"
pbp_dir="$project_root/data/raw/pbp"
model_dir="$project_root/model"
parallel_downloads="${NFL_PBP_PARALLEL:-4}"
season_start="${1:-1999}"
season_end="${2:-$(date +%Y)}"

if ! [[ "$season_start" =~ ^[0-9]{4}$ && "$season_end" =~ ^[0-9]{4}$ ]]; then
  printf 'Season arguments must be four-digit years.\n' >&2
  exit 2
fi

if (( season_start < 1999 || season_end < season_start )); then
  printf 'Use a start year >= 1999 and an end year >= the start year.\n' >&2
  exit 2
fi

mkdir -p "$external_dir" "$pbp_dir"

clone_if_missing() {
  local repo_url="$1"
  local destination="$2"

  if [[ -d "$destination/.git" ]]; then
    printf 'Using existing checkout: %s\n' "$destination"
    return 0
  fi

  if [[ -e "$destination" ]]; then
    printf 'Destination exists but is not a git checkout: %s\n' "$destination" >&2
    exit 1
  fi

  git clone --depth 1 "$repo_url" "$destination"
}

clone_if_missing \
  "https://github.com/nflverse/fastrmodels.git" \
  "$external_dir/fastrmodels"
clone_if_missing \
  "https://github.com/nflverse/nflfastR.git" \
  "$external_dir/nflfastR"

# Keep the two WP model artifacts and the upstream model-building source in the
# repository itself, so a GitHub clone contains the model without requiring the
# full external checkout. The full checkouts remain available under external/
# for reference and for the nflfastR calculation code.
mkdir -p "$model_dir"
cp "$external_dir/fastrmodels/data/wp_model.rda" "$model_dir/wp_model.rda"
cp "$external_dir/fastrmodels/data/wp_model_spread.rda" "$model_dir/wp_model_spread.rda"
cp "$external_dir/fastrmodels/data-raw/MODELS.R" "$model_dir/MODELS.R"
cp "$external_dir/fastrmodels/LICENSE.md" "$model_dir/UPSTREAM_LICENSE.md"
git -C "$external_dir/fastrmodels" rev-parse HEAD > "$model_dir/UPSTREAM_COMMIT.txt"

download_season() {
  local season="$1"
  local url="https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_${season}.parquet"
  local destination="$pbp_dir/play_by_play_${season}.parquet"
  local partial="$destination.part"
  local http_code

  if [[ -s "$destination" ]]; then
    printf '[%s] already present\n' "$season"
    return 0
  fi

  http_code="$(curl -L -sS -o /dev/null -w '%{http_code}' "$url" || true)"
  if [[ "$http_code" == "404" ]]; then
    printf '[%s] no parquet release yet; skipped\n' "$season"
    return 0
  fi
  if [[ "$http_code" != "200" ]]; then
    printf '[%s] unexpected HTTP status %s\n' "$season" "$http_code" >&2
    return 1
  fi

  printf '[%s] downloading\n' "$season"
  curl --fail --location --retry 3 --retry-delay 2 --continue-at - \
    --output "$partial" "$url"
  mv -f "$partial" "$destination"
  printf '[%s] saved %s\n' "$season" "$destination"
}

batch=()
for season in $(seq "$season_start" "$season_end"); do
  batch+=("$season")
  if (( ${#batch[@]} == parallel_downloads )); then
    for batch_season in "${batch[@]}"; do
      download_season "$batch_season" &
    done
    wait
    batch=()
  fi
done

if (( ${#batch[@]} > 0 )); then
  for batch_season in "${batch[@]}"; do
    download_season "$batch_season" &
  done
  wait
fi

printf '\nDownloaded assets:\n'
find "$external_dir/fastrmodels/data" -maxdepth 1 -type f -name '*wp*' -print | sort
find "$pbp_dir" -maxdepth 1 -type f -name 'play_by_play_*.parquet' -print | sort
