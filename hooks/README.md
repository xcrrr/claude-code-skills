# Hooks

Two deterministic guards. Unlike a skill, a hook is not advisory — the harness
runs it on every matching tool call, so it fires whether or not the model
remembers to care.

Both patterns are adapted from [gstack](https://github.com/garrytan/gstack)
(Garry Tan, MIT) — its `careful` and `freeze` skills. These are clean
reimplementations: no telemetry, no analytics, no `~/.gstack` state, no
external binaries. Bash plus `python3` for JSON parsing.

## `guard-destructive.sh`

`PreToolUse` on `Bash`. Escalates to a confirmation prompt — `permissionDecision: "ask"` —
for commands that are unrecoverable or outward-facing:

- recursive deletes, with a louder message for root/home targets
- `git push --force`, `reset --hard`, `clean -fd`, branch deletion, tag pushes
- production deploys (`vercel --prod`, `wrangler deploy`), package publishes,
  `gh release create`, making a repo public
- destructive SQL (`DROP`, `TRUNCATE`, `DELETE FROM`)
- deleting or overwriting `.env` and Android signing material
- piping `curl`/`wget` straight into a shell, `chmod 777`

It never denies. It asks — which matters in `auto` permission mode, where a
classifier would otherwise approve these silently.

## `guard-scope.sh`

`PreToolUse` on `Edit|Write|NotebookEdit`. When `~/.claude/edit-scope` holds a
directory path, writes outside that directory are denied.

```bash
echo "$PWD/src" > ~/.claude/edit-scope   # lock
rm ~/.claude/edit-scope                  # release
```

No file means no restriction, so it is inert until you set it. Useful when
running parallel agents that must not stray outside their assigned area.

## Install

```bash
cp hooks/guard-*.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/guard-*.sh
```

Then register in `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Bash",
        "hooks": [{ "type": "command", "command": "bash $HOME/.claude/hooks/guard-destructive.sh", "timeout": 10 }] },
      { "matcher": "Edit|Write|NotebookEdit",
        "hooks": [{ "type": "command", "command": "bash $HOME/.claude/hooks/guard-scope.sh", "timeout": 10 }] }
    ]
  }
}
```

Both scripts exit 0 silently on any internal error, so a broken guard degrades
to no guard rather than blocking your work. Test one before trusting it:

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"git push --force"}}' \
  | ~/.claude/hooks/guard-destructive.sh
```
