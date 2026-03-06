# Silicato Spec - UX Defaults and CLI Short Flags

Status: Implemented
Created on: 2026-03-06

## Problem

Current default CLI behavior creates avoidable friction:
1. Normal mode prints transcript text locally even though users already see injected text in tmux.
2. Common options require long-form flags only.
3. Startup target selection defaults to reuse behavior, which is cumbersome for multi-instance workflows.

## Goal

Improve default UX for daily use while preserving explicit compatibility paths.

## Scope

1. In normal mode, do not print transcript text locally.
2. Keep transcript output visible in preview mode.
3. Add short option aliases for common CLI flags.
4. Make interactive tmux picker default at startup when no explicit target is provided.
5. Keep legacy env/config target reuse available via explicit opt-in flag.

## Non-Goals

1. No change to send/edit/retry/skip/quit semantics in preview mode.
2. No change to tmux pane target validation rules.
3. No changes to audio/STT runtime stack.

## Acceptance Criteria

1. `silicato` in normal mode no longer prints `Transcript: ...` lines.
2. `silicato --preview` still shows transcript and interactive confirmation flow.
3. Short flags parse correctly for key options.
4. Default startup behavior opens interactive tmux picker.
5. `--reuse-target` restores env/config fallback behavior.
