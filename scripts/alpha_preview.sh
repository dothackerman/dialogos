#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -x ".venv/bin/python3" ]]; then
  PYTHON=".venv/bin/python3"
else
  PYTHON="python3"
fi

NO_RUN=0
FORWARD_ARGS=()
for arg in "$@"; do
  if [[ "$arg" == "--no-run" ]]; then
    NO_RUN=1
  else
    FORWARD_ARGS+=("$arg")
  fi
done

ALPHA_MODEL="${DIALOGOS_ALPHA_MODEL:-small}"
ALPHA_DEVICE="${DIALOGOS_ALPHA_DEVICE:-cuda}"
ALPHA_COMPUTE_TYPE="${DIALOGOS_ALPHA_COMPUTE_TYPE:-float16}"
ALPHA_LANGUAGE="${DIALOGOS_ALPHA_LANGUAGE:-auto}"

if [[ -n "${DIALOGOS_ALPHA_HF_TOKEN:-}" && -z "${HF_TOKEN:-}" ]]; then
  export HF_TOKEN="$DIALOGOS_ALPHA_HF_TOKEN"
fi

MISSING=()
for binary in tmux arecord; do
  if ! command -v "$binary" >/dev/null 2>&1; then
    MISSING+=("$binary")
  fi
done

if [[ ${#MISSING[@]} -gt 0 ]]; then
  echo "Missing required binaries: ${MISSING[*]}" >&2
  echo "Install on Ubuntu/TUXEDO with: sudo apt install -y tmux alsa-utils ffmpeg" >&2
  exit 1
fi

if ! "$PYTHON" -c 'import dialogos' >/dev/null 2>&1; then
  echo "Dialogos package is not installed in the active environment." >&2
  echo "Run: make install-dev" >&2
  exit 1
fi

CONFIG_PATH="$($PYTHON - <<'PY'
from dialogos.config import default_config_path
print(default_config_path())
PY
)"

LOG_PATH="$($PYTHON - <<'PY'
from dialogos.logging_jsonl import default_log_path
print(default_log_path())
PY
)"

echo "== Dialogos Alpha Preview =="
echo "Project root: $ROOT_DIR"
echo "Python: $PYTHON"
echo "Config path: $CONFIG_PATH"
echo "Log path: $LOG_PATH"
echo "Target resolution order: --tmux-target -> DIALOGOS_TMUX_TARGET -> remembered config -> picker"
echo "Alpha default profile: model=$ALPHA_MODEL device=$ALPHA_DEVICE compute_type=$ALPHA_COMPUTE_TYPE language=$ALPHA_LANGUAGE"
echo "(Dialogos auto-falls back to CPU int8 if CUDA runtime is unavailable.)"

if [[ -n "${HF_TOKEN:-}" ]]; then
  echo "HF Hub auth: HF_TOKEN detected (authenticated model downloads)."
else
  echo "HF Hub auth: no HF_TOKEN set (public models still work; downloads may be slower/rate-limited)."
  echo "Set once per shell with: export HF_TOKEN=hf_xxx"
fi

echo
echo "Running diagnostics (dialogos --doctor)..."
"$PYTHON" -m dialogos --doctor

echo
HAS_TMUX_SESSION=0
if tmux list-panes -a >/dev/null 2>&1; then
  HAS_TMUX_SESSION=1
  echo "tmux session detected."
else
  echo "No active tmux session detected."
  echo "Start one with: tmux new -s codex"
  echo "Then start Codex in that tmux session."
fi

if [[ "$NO_RUN" -eq 1 ]]; then
  echo
  echo "Preview checks complete (--no-run)."
  exit 0
fi

if [[ "$HAS_TMUX_SESSION" -eq 0 ]]; then
  echo
  echo "Alpha preview stopped before launch because no tmux session is running."
  echo "This is expected on first run. After creating a tmux session, rerun: make alpha-preview"
  exit 0
fi

echo
echo "Launching Dialogos with alpha defaults (override by passing your own args):"
echo "  $PYTHON -m dialogos --model $ALPHA_MODEL --device $ALPHA_DEVICE --compute-type $ALPHA_COMPUTE_TYPE --language $ALPHA_LANGUAGE ${FORWARD_ARGS[*]:-}"

exec "$PYTHON" -m dialogos \
  --model "$ALPHA_MODEL" \
  --device "$ALPHA_DEVICE" \
  --compute-type "$ALPHA_COMPUTE_TYPE" \
  --language "$ALPHA_LANGUAGE" \
  "${FORWARD_ARGS[@]}"
