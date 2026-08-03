#!/usr/bin/env bash
# Edit-scope lock: when a scope is set, refuse writes outside one directory.
#
# Pattern adapted from gstack's `freeze` skill (github.com/garrytan/gstack,
# MIT, Copyright (c) 2026 Garry Tan). Reimplemented without gstack's path
# helper or state directory.
#
# State: a single line in ~/.claude/edit-scope holding an absolute directory.
# No file means no restriction, so the guard is inert until you set it.
#
#   Set:    echo "$PWD/src" > ~/.claude/edit-scope
#   Clear:  rm ~/.claude/edit-scope
#
# Contract: PreToolUse hook on Edit|Write|NotebookEdit. Exits 0 with a JSON
# deny decision when a path falls outside the scope; exits 0 silently
# otherwise, including on any internal failure.

set -uo pipefail

SCOPE_FILE="${HOME}/.claude/edit-scope"
[ -f "$SCOPE_FILE" ] || exit 0

scope="$(head -1 "$SCOPE_FILE" 2>/dev/null | tr -d '\r\n')"
[ -z "$scope" ] && exit 0

# Normalize the scope to an absolute path with no trailing slash.
scope="${scope/#\~/$HOME}"
scope="$(cd "$scope" 2>/dev/null && pwd -P)" || exit 0
scope="${scope%/}"

payload="$(cat 2>/dev/null || true)"
[ -z "$payload" ] && exit 0

command -v python3 >/dev/null 2>&1 || exit 0

target="$(printf '%s' "$payload" | python3 -c '
import sys, json
try:
    d = json.load(sys.stdin)
    ti = d.get("tool_input", {})
    print(ti.get("file_path") or ti.get("notebook_path") or "")
except Exception:
    pass
' 2>/dev/null)"

[ -z "$target" ] && exit 0

# Resolve the target against its nearest existing parent, so a not-yet-created
# file still resolves to a real directory rather than failing open.
tdir="$(dirname "$target")"
while [ ! -d "$tdir" ] && [ "$tdir" != "/" ] && [ -n "$tdir" ]; do
  tdir="$(dirname "$tdir")"
done
tdir="$(cd "$tdir" 2>/dev/null && pwd -P)" || exit 0
resolved="${tdir%/}/$(basename "$target")"

case "$resolved" in
  "$scope"/*|"$scope")
    exit 0 ;;
esac

reason="Edit scope is locked to ${scope} — ${resolved} is outside it. Finish the work inside the scope, or clear the lock with: rm ~/.claude/edit-scope"

printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":%s}}\n' \
  "$(printf '%s' "$reason" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))')"
exit 0
