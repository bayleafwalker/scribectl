#!/usr/bin/env bash
set -euo pipefail

# Writer-model bake-off (backlog item 1075).
#
# For each candidate: serve it with vllm-writer-run, fill Scene 01-01 in a
# disposable copy of the fixture vault (openai runner -> the local model),
# then fire the review lanes with the claude runner. What lands per model is
# the draft plus canon+voice reports; the verdict that matters is the
# operator reading the drafts against the Prose Voice Canon — this script
# only makes that reading possible in one sitting.
#
# Usage: bakeoff-writer.sh [model-id ...]   (default: the three candidates)

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CANDIDATES=(
  "jeffcookio/Mistral-Small-3.2-24B-Instruct-2506-awq-sym"
  "gaunernst/gemma-3-27b-it-int4-awq"
  "tacodevs/Cydonia-24B-v4.3-AWQ"
)
[[ $# -gt 0 ]] && CANDIDATES=("$@")

PORT="${VLLM_PORT:-8080}"
BASE_URL="http://127.0.0.1:${PORT}"
HEALTH_TIMEOUT="${BAKEOFF_HEALTH_TIMEOUT:-3600}"  # first run downloads ~15 GB/model
RESULTS="${BAKEOFF_RESULTS:-$REPO/ops/vllm-writer/bakeoff-results/$(date +%Y%m%d-%H%M%S)}"
RUN_BIN="${HOME}/.local/bin/vllm-writer-run"
DISPATCH="$REPO/.venv/bin/scribe-dispatch"

log() { printf '%s [bakeoff] %s\n' "$(date --iso-8601=seconds)" "$*" >&2; }

stop_server() {
  docker stop -t 60 vllm-writer >/dev/null 2>&1 || true
  docker rm -f vllm-writer >/dev/null 2>&1 || true
}
trap stop_server EXIT

mkdir -p "$RESULTS"
log "Results land in $RESULTS"

for model in "${CANDIDATES[@]}"; do
  slug="$(echo "$model" | tr '/' '__')"
  out="$RESULTS/$slug"
  mkdir -p "$out"

  vault_parent="$(mktemp -d)"
  cp -r "$REPO/fixtures/fertile-flames" "$vault_parent/vault"
  export SCRIBECTL_VAULT="$vault_parent/vault"

  log "=== $model ==="
  stop_server
  WRITER_MODEL="$model" "$RUN_BIN" >"$out/server.log" 2>&1 &
  server_pid=$!

  log "Waiting for $BASE_URL/v1/models (timeout ${HEALTH_TIMEOUT}s; cold start includes the download)"
  waited=0
  until curl -sf "$BASE_URL/v1/models" >/dev/null 2>&1; do
    if ! kill -0 "$server_pid" 2>/dev/null; then
      log "FAIL: server exited during startup — tail of $out/server.log:"
      tail -n 20 "$out/server.log" >&2
      echo "$model: SERVER FAILED" >>"$RESULTS/summary.txt"
      continue 2
    fi
    sleep 15; waited=$((waited + 15))
    if (( waited >= HEALTH_TIMEOUT )); then
      log "FAIL: health timeout for $model"
      echo "$model: HEALTH TIMEOUT" >>"$RESULTS/summary.txt"
      stop_server
      continue 2
    fi
  done
  log "Server up after ${waited}s"

  log "Fill pass (openai runner -> $model)"
  "$DISPATCH" run -p "Fertile Flames" --runner openai --base-url "$BASE_URL" --model "$model" \
    >"$out/fill.log" 2>&1 || { log "FAIL: fill pass — see $out/fill.log"; echo "$model: FILL FAILED" >>"$RESULTS/summary.txt"; stop_server; continue; }

  log "Review pass (claude runner)"
  "$DISPATCH" run -p "Fertile Flames" --runner claude \
    >"$out/review.log" 2>&1 || log "WARN: review pass had errors — see $out/review.log"

  proj="$SCRIBECTL_VAULT/Works/Fertile Flames"
  cp -r "$proj/body/drafts" "$out/drafts" 2>/dev/null || true
  cp -r "$proj/reviews" "$out/reviews" 2>/dev/null || true

  verdicts="$(grep -rh '^verdict:' "$out/reviews" 2>/dev/null | tr '\n' ' ' || true)"
  echo "$model: drafts=$(ls "$out/drafts" 2>/dev/null | wc -l) ${verdicts:-no reviews}" >>"$RESULTS/summary.txt"

  stop_server
  rm -rf "$vault_parent"
done

log "Done."
echo
echo "=== bake-off summary ==="
cat "$RESULTS/summary.txt" 2>/dev/null || echo "(nothing ran)"
echo
echo "Read the drafts under $RESULTS/<model>/drafts/ against the Prose Voice Canon."
echo "Set the winner as WRITER_MODEL in ~/.config/vllm/writer.env."
