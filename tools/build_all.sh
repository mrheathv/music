#!/usr/bin/env bash
# Re-render every track from its script and finalize it into the game folders.
# Renders are deterministic (fixed random seeds), so this reproduces the committed OGGs.
# Usage: bash tools/build_all.sh
set -euo pipefail
cd "$(dirname "$0")/.."

render() {  # render <script> <raw name> <output ogg> [ENV=VALUE]
  local script=$1 raw=$2 out=$3
  shift 3
  echo "== $out"
  env "$@" python3 "$script"
  python3 tools/finalize.py "build/$raw" "$out"
}

render necity/scripts/neon_grid.py        neon_grid_raw.wav       necity/tracks/neon_grid.ogg
render necity/scripts/neon_grid_calm.py   neon_grid_calm_raw.wav  necity/tracks/neon_grid_calm.ogg
render necity/scripts/skyline_rising.py   skyline_rising_raw.wav  necity/tracks/skyline_rising.ogg
render necity/scripts/signal_lights.py    signal_lights_raw.wav   necity/tracks/signal_lights.ogg
render necity/scripts/afterglow.py        afterglow_raw.wav       necity/tracks/afterglow.ogg
render necity/scripts/neon_horizon.py     neon_horizon_raw.wav    necity/tracks/neon_horizon.ogg

render alphapp/scripts/golden_hour.py     golden_hour_raw.wav     alphapp/tracks/golden_hour.ogg
for v in bell vibe kalimba flute; do
  render alphapp/scripts/golden_hour_warm.py "golden_hour_warm_${v}_raw.wav" \
         "alphapp/tracks/golden_hour_warm_${v}.ogg" MELODY=$v
done
