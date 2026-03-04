#!/usr/bin/env bash
set -euo pipefail

branch="$(git rev-parse --abbrev-ref HEAD)"

if [[ "$branch" == "HEAD" ]]; then
  echo "Branch validation skipped: detached HEAD."
  exit 0
fi

pattern='^(main|(feat|fix|docs|refactor|test|chore)/[a-z0-9._-]+)$'

if [[ ! "$branch" =~ $pattern ]]; then
  cat <<'EOF'
Invalid branch name.
Allowed:
  main
  feat/<slug>
  fix/<slug>
  docs/<slug>
  refactor/<slug>
  test/<slug>
  chore/<slug>
EOF
  exit 1
fi

echo "Branch name OK: $branch"
