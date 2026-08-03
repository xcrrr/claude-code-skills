#!/usr/bin/env bash
# Generate .claude/briefing.md for a set of repositories and keep it current.
#
# For each git repository given (default: every git repo one level under the
# target directory) this:
#   1. generates .claude/briefing.md with warm-start.py
#   2. adds it to .git/info/exclude, so it never appears in git status
#   3. installs a post-commit hook that regenerates it
#
# Nothing tracked is modified. .git/info/exclude is a local ignore file that is
# not part of the repository, so no .gitignore is touched and no collaborator
# sees a change. Remove everything with --uninstall.
#
# Usage:
#   install-briefings.sh [DIR]            # default: ~/repos
#   install-briefings.sh --uninstall [DIR]
#   install-briefings.sh --single [REPO]  # just this one repository

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WARM="$SCRIPT_DIR/warm-start.py"
MARKER="# claude-code-skills: agent briefing"

[ -f "$WARM" ] || { echo "warm-start.py not found next to this script" >&2; exit 1; }

mode=install
target="$HOME/repos"
case "${1:-}" in
  --uninstall) mode=uninstall; target="${2:-$HOME/repos}" ;;
  --single)    mode=single;    target="${2:-$PWD}" ;;
  "")          ;;
  *)           target="$1" ;;
esac

exclude_line() {  # $1 = repo root
  local ex="$1/.git/info/exclude"
  mkdir -p "$(dirname "$ex")"
  grep -qxF ".claude/briefing.md" "$ex" 2>/dev/null || {
    printf '\n%s\n.claude/briefing.md\n' "$MARKER" >> "$ex"
  }
}

install_hook() {  # $1 = repo root
  local hook="$1/.git/hooks/post-commit"
  if [ -f "$hook" ] && ! grep -q "$MARKER" "$hook" 2>/dev/null; then
    echo "    post-commit hook already exists and is not ours — left alone"
    return
  fi
  cat > "$hook" <<HOOK
#!/usr/bin/env bash
$MARKER
# Regenerates .claude/briefing.md so subagents start with a current map.
# Deliberately silent and non-fatal: a briefing is never worth failing a commit.
{
  root="\$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
  [ -n "\$root" ] || exit 0
  python3 "$WARM" --path "\$root" >/dev/null 2>&1
} || true
exit 0
HOOK
  chmod +x "$hook"
}

remove_from() {  # $1 = repo root
  local hook="$1/.git/hooks/post-commit" ex="$1/.git/info/exclude"
  if [ -f "$hook" ] && grep -q "$MARKER" "$hook" 2>/dev/null; then rm -f "$hook"; fi
  if [ -f "$ex" ]; then
    grep -vxF ".claude/briefing.md" "$ex" 2>/dev/null | grep -vF "$MARKER" > "$ex.tmp" && mv "$ex.tmp" "$ex"
  fi
  rm -f "$1/.claude/briefing.md"
  rmdir "$1/.claude" 2>/dev/null
  echo "  removed: $(basename "$1")"
}

repos=()
if [ "$mode" = single ]; then
  root="$(cd "$target" && git rev-parse --show-toplevel 2>/dev/null)" || {
    echo "Not a git repository: $target" >&2; exit 1; }
  repos=("$root")
else
  for d in "$target"/*/; do
    [ -d "$d/.git" ] && repos+=("${d%/}")
  done
fi

[ ${#repos[@]} -eq 0 ] && { echo "No git repositories under $target"; exit 1; }

if [ "$mode" = uninstall ]; then
  echo "Removing briefings from ${#repos[@]} repositories:"
  for r in "${repos[@]}"; do remove_from "$r"; done
  exit 0
fi

echo "Installing briefings into ${#repos[@]} repositories:"
for r in "${repos[@]}"; do
  name="$(basename "$r")"
  out="$(python3 "$WARM" --path "$r" 2>&1)" || { echo "  $name: FAILED — $out"; continue; }
  size="$(echo "$out" | grep -o '~[0-9]* tokens' | head -1)"
  exclude_line "$r"
  install_hook "$r"
  printf "  %-26s %s\n" "$name" "${size:-generated}"
done

echo
echo "Each repo now has .claude/briefing.md, ignored locally via"
echo ".git/info/exclude, refreshed by a post-commit hook. No tracked file"
echo "was modified. Undo with: $(basename "$0") --uninstall"
