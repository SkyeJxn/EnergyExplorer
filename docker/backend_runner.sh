#!/bin/sh
set -eu

# Defaults: wait 3-4 hours between fetch runs.
MIN_SLEEP_SECONDS="${FETCH_MIN_SLEEP_SECONDS:-10800}"
MAX_SLEEP_SECONDS="${FETCH_MAX_SLEEP_SECONDS:-14400}"

if [ "$MIN_SLEEP_SECONDS" -gt "$MAX_SLEEP_SECONDS" ]; then
  echo "FETCH_MIN_SLEEP_SECONDS must be <= FETCH_MAX_SLEEP_SECONDS" >&2
  exit 1
fi

while true; do
  echo "[backend] Starting fetch run at $(date -u +%Y-%m-%dT%H:%M:%SZ)"

  # Never stop the loop on fetch errors; run again after the next interval.
  if python app/fetch_handler.py -q; then
    echo "[backend] Fetch run finished successfully"
  else
    rc=$?
    echo "[backend] Fetch run failed with exit code $rc"
  fi

  SLEEP_SECONDS=$(python -c "import random; print(random.randint(${MIN_SLEEP_SECONDS}, ${MAX_SLEEP_SECONDS}))")
  echo "[backend] Sleeping for ${SLEEP_SECONDS}s before next run"
  sleep "$SLEEP_SECONDS"
done
