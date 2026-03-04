# Quickstart

## 1) Install system packages (Ubuntu / TUXEDO OS)

```bash
sudo apt update
sudo apt install -y alsa-utils ffmpeg python3-venv wl-clipboard tmux
```

## 2) Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -U pip
python3 -m pip install -r requirements.txt
python3 -m pip install -r requirements-dev.txt
python3 -m pip install -e .
make hooks
```

## 3) Run push-to-talk transcription

```bash
python3 talk_to_codex.py --model small --language auto --copy
# or
python3 -m dialogos --model small --language auto --copy
```

Controls:
- Press `Enter` to start recording
- Press `Enter` to stop
- Transcript appears in terminal and is copied to clipboard

## 4) Diagnostics

```bash
python3 talk_to_codex.py --doctor
```

## 5) Quality gate before changes

```bash
source .venv/bin/activate
make gate
```
