#!/usr/bin/env bash
# install_skills.sh — install all skills under ./skills/ into ~/.claude/skills/
#
# Usage:
#   ./install_skills.sh              # install (default)
#   ./install_skills.sh --uninstall  # remove any skill this repo defines
#   ./install_skills.sh --dry-run    # show what would happen without doing it
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_SRC="$REPO_DIR/skills"
SKILLS_DEST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"

MODE="install"
DRY_RUN=0

for arg in "$@"; do
  case "$arg" in
    --uninstall) MODE="uninstall" ;;
    --dry-run)   DRY_RUN=1 ;;
    -h|--help)
      sed -n '2,10p' "$0"
      exit 0
      ;;
    *) echo "unknown arg: $arg" >&2; exit 2 ;;
  esac
done

run() {
  if [[ "$DRY_RUN" -eq 1 ]]; then
    printf 'DRY-RUN: %s\n' "$*"
  else
    "$@"
  fi
}

if [[ ! -d "$SKILLS_SRC" ]]; then
  echo "no skills/ dir at $SKILLS_SRC — nothing to do" >&2
  exit 1
fi

mkdir -p "$SKILLS_DEST"

SKILL_NAMES=()
while IFS= read -r -d '' skill_dir; do
  SKILL_NAMES+=("$(basename "$skill_dir")")
done < <(find "$SKILLS_SRC" -mindepth 1 -maxdepth 1 -type d -print0)

if [[ "${#SKILL_NAMES[@]}" -eq 0 ]]; then
  echo "no skills discovered under $SKILLS_SRC" >&2
  exit 1
fi

case "$MODE" in
  install)
    for name in "${SKILL_NAMES[@]}"; do
      src="$SKILLS_SRC/$name"
      dest="$SKILLS_DEST/$name"
      if [[ ! -f "$src/SKILL.md" ]]; then
        echo "  skip $name — no SKILL.md" >&2
        continue
      fi
      run rm -rf "$dest"
      run mkdir -p "$dest"
      run cp -r "$src/." "$dest/"
      echo "  installed $name -> $dest"
    done
    echo
    echo "done. restart Claude Code to pick up the new skills."
    ;;
  uninstall)
    for name in "${SKILL_NAMES[@]}"; do
      dest="$SKILLS_DEST/$name"
      if [[ -d "$dest" ]]; then
        run rm -rf "$dest"
        echo "  removed $name"
      else
        echo "  skip $name — not present at $dest"
      fi
    done
    ;;
esac
