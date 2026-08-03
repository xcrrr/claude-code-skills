#!/usr/bin/env bash
# Pre-flight guard for destructive and outward-facing Bash commands.
#
# Pattern adapted from gstack's `careful` skill (github.com/garrytan/gstack,
# MIT, Copyright (c) 2026 Garry Tan). Reimplemented here without telemetry,
# analytics, or any ~/.gstack state.
#
# Contract: PreToolUse hook. Reads the tool call as JSON on stdin, prints a
# JSON permission decision on stdout, exits 0. Any internal failure exits 0
# silently so a broken guard can never block real work.

set -uo pipefail

payload="$(cat 2>/dev/null || true)"
[ -z "$payload" ] && exit 0

# Extract the command. python3 is the reliable path; the grep fallback keeps
# the guard alive on a machine without it.
if command -v python3 >/dev/null 2>&1; then
  cmd="$(printf '%s' "$payload" | python3 -c '
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get("tool_input", {}).get("command", ""))
except Exception:
    pass
' 2>/dev/null)"
else
  cmd="$(printf '%s' "$payload" | grep -o '"command"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*:[[:space:]]*"//; s/"$//')"
fi

[ -z "$cmd" ] && exit 0

ask() {
  # permissionDecision "ask" escalates to a real confirmation prompt even when
  # the session is in auto mode. It does not refuse the command.
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"ask","permissionDecisionReason":%s}}\n' \
    "$(printf '%s' "$1" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))' 2>/dev/null || printf '"%s"' "$1")"
  exit 0
}

# --- Catastrophic / unrecoverable -------------------------------------------

case "$cmd" in
  *"rm -rf /"|*"rm -fr /"|*"rm -rf / "*|*"rm -rf ~"|*"rm -rf ~/"|*"rm -rf \$HOME"*|*"rm -rf /*"*|\
  *"rm -rf /etc"*|*"rm -rf /usr"*|*"rm -rf /var"*|*"rm -rf /home"*|*"rm -rf /boot"*)
    ask "Recursive delete targeting a root or home path. This can destroy the system or your entire home directory. Verify the exact target before running." ;;
  *"rm -rf"*|*"rm -fr"*)
    ask "Recursive force delete. Confirm the target path is the one you mean — this is not recoverable through Claude's checkpoints." ;;
esac

# --- Git history rewriting ---------------------------------------------------

case "$cmd" in
  *"push --force"*|*"push -f "*|*"push --force-with-lease"*)
    ask "Force push. This rewrites remote history and can discard a collaborator's commits." ;;
  *"reset --hard"*)
    ask "git reset --hard discards uncommitted work in the working tree." ;;
  *"clean -fd"*|*"clean -fdx"*|*"clean -xfd"*)
    ask "git clean removes untracked files permanently, including anything gitignored when -x is set." ;;
  *"branch -D"*|*"push"*":"*)
    ask "Branch deletion or a remote-ref push. Confirm the branch name." ;;
esac

# --- Outward-facing: publishing, deploying, releasing ------------------------
# These are not destructive locally, but they are visible to other people and
# hard to retract, so they get an explicit confirmation.

case "$cmd" in
  *"vercel --prod"*|*"vercel deploy --prod"*|*"wrangler deploy"*|*"wrangler publish"*)
    ask "Production deploy. Confirm this site is meant to go live now — check that noindex/ALLOW_INDEXING is set the way you intend." ;;
  *"npm publish"*|*"bun publish"*|*"yarn publish"*|*"pnpm publish"*)
    ask "Publishing a package to a public registry. Versions cannot be unpublished freely." ;;
  *"gh release create"*|*"gh repo create"*" --public"*|*"gh repo edit"*"--visibility public"*)
    ask "Creates or exposes something publicly on GitHub. Confirm the contents are meant to be public." ;;
  *"git push"*"--tags"*)
    ask "Pushing tags. Tags are hard to move once others have fetched them." ;;
esac

# --- Databases ---------------------------------------------------------------

shopt -s nocasematch 2>/dev/null
case "$cmd" in
  *"drop table"*|*"drop database"*|*"drop schema"*|*"truncate table"*|*"delete from"*)
    ask "Destructive SQL. Confirm you are pointed at the intended database and have a backup." ;;
esac
shopt -u nocasematch 2>/dev/null

# --- Secrets and signing material -------------------------------------------
# The Android release keystore and .env files are explicitly owner-only in this
# workspace; losing either is unrecoverable.

case "$cmd" in
  *"keystore"*"rm"*|*"rm"*"keystore"*|*"rm"*".jks"*|*"rm"*"keystore.properties"*)
    ask "Touching Android signing material. The release keystore cannot be regenerated — a lost keystore means the app can never be updated under the same identity." ;;
  *">"*".env"|*">"*".env "*|*"rm"*".env"*)
    ask "Overwriting or deleting a .env file. Secrets in it are not recoverable from git." ;;
esac

# --- Remote code execution ---------------------------------------------------

case "$cmd" in
  *"curl"*"|"*"sh"*|*"curl"*"|"*"bash"*|*"wget"*"|"*"sh"*|*"wget"*"|"*"bash"*)
    ask "Piping a downloaded script straight into a shell. Read the script first." ;;
  *"chmod -R 777"*|*"chmod 777"*)
    ask "World-writable permissions. Almost always the wrong fix." ;;
esac

exit 0
