# Hooks

One deterministic guard. Unlike a skill, a hook is not advisory — the harness
runs it on every matching tool call, so it fires whether or not the model
remembers to care.

The pattern is adapted from [gstack](https://github.com/garrytan/gstack)
(Garry Tan, MIT), specifically its `freeze` skill. This is a clean
reimplementation: no telemetry, no analytics, no `~/.gstack` state, no external
binaries. Bash plus `python3` for JSON parsing.

## `guard-scope.sh`

`PreToolUse` on `Edit|Write|NotebookEdit`. When `~/.claude/edit-scope` holds a
directory path, writes outside that directory are denied.

```bash
echo "$PWD/src" > ~/.claude/edit-scope   # lock
rm ~/.claude/edit-scope                  # release
```

No file means no restriction, so it is inert until you set it and costs
nothing when unused. Useful when running parallel agents that must not stray
outside their assigned area.

## Install

```bash
cp hooks/guard-scope.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/guard-scope.sh
```

Then register in `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Edit|Write|NotebookEdit",
        "hooks": [{ "type": "command", "command": "bash $HOME/.claude/hooks/guard-scope.sh", "timeout": 10 }] }
    ]
  }
}
```

The script exits 0 silently on any internal error, so a broken guard degrades
to no guard rather than blocking your work. Test it before trusting it:

```bash
echo "$HOME/repos/myproject" > ~/.claude/edit-scope
echo '{"tool_name":"Edit","tool_input":{"file_path":"/etc/passwd"}}' \
  | ~/.claude/hooks/guard-scope.sh
rm ~/.claude/edit-scope
```

## A note on confirmation-prompt guards

An earlier version of this directory also shipped a `guard-destructive.sh` that
escalated `rm -rf`, force pushes, production deploys and similar to a
confirmation prompt. It was removed after use.

The reason is worth recording. In `auto` permission mode a classifier already
reviews commands before they run, so the hook mostly added a second prompt on
top of a decision that had already been made — and prompt fatigue is not a
safety feature. A guard that fires constantly trains you to dismiss it, which
leaves you worse off than having no guard at all.

If you want that behavior anyway, keep the trigger list very short and limited
to the genuinely unrecoverable — signing keys, production databases — rather
than every `rm` and every push.
