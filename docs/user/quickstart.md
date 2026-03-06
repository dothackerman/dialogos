# Quickstart

## 1) Platform and baseline

Official support target:
- TUXEDO OS 24.04 LTS (Ubuntu noble base)

Best effort target:
- Ubuntu 24.04-compatible Linux environments

Validated RC baseline:
- Python 3.12.3
- tmux 3.4
- Agent CLI (for example Codex CLI or Claude Code)

## 2) Install required system packages

```bash
sudo apt update
sudo apt install -y alsa-utils ffmpeg python3-venv tmux
```

## 3) Install Silicato

### Option A: RC install from PyPI (`0.1.0rc3`)

```bash
pipx install silicato==0.1.0rc3
```

### Option B: install from source checkout

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -U pip
make install-dev
make hooks
```

For maintainer TestPyPI validation steps, see `docs/dev/release-rc.md`.

## 4) Start your agent CLI in tmux

```bash
tmux new -s agent
# run your agent CLI in this tmux session (for example codex or claude)
```

## 5) Verify runtime dependencies

```bash
silicato --doctor
```

## 6) Run Silicato

Normal mode (direct send):

```bash
silicato
```

Preview mode (explicit action before send):

```bash
silicato --preview
# short form:
silicato -p
```

Preview controls:
- `y=send`
- `e=edit`
- `r=retry`
- `s=skip`
- `q=quit`

## 7) Target selection and overrides

```bash
# one-off explicit target
silicato --tmux-target codex:0.1
# short form:
silicato -t codex:0.1

# opt in to env/config target reuse mode
export SILICATO_TMUX_TARGET=codex:0.1
silicato --reuse-target
```

Default resolution order:
1. `--tmux-target`
2. interactive picker

`--reuse-target` resolution order:
1. `--tmux-target`
2. `SILICATO_TMUX_TARGET`
3. remembered config target
4. interactive picker

Target format requirement:
- Use pane-scoped targets only: `session:window.pane` (for example `codex:0.1`) or `%pane_id`.
- Window/session-scoped targets (for example `codex:0`) are rejected to avoid cross-pane collisions.

## 8) Optional model download auth

If Hugging Face warns about anonymous download limits:

```bash
export HF_TOKEN=hf_xxx
```

This token is only used for model downloads.
