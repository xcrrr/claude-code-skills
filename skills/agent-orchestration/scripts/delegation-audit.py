#!/usr/bin/env python3
"""Audit how much main-conversation context your delegations actually saved.

Claude Code writes every subagent's transcript to
  ~/.claude/projects/<project>/<sessionId>/subagents/agent-<id>.jsonl
including per-message token usage. That is enough to answer the only question
that matters about a delegation: how much material did the agent absorb, and
how many tokens did it charge the main conversation to tell you about it?

    leverage = new tokens processed inside the agent / tokens it returned

A high number means the agent did real reading and handed back a summary — the
delegation paid for itself. A low number means you paid cold-start cost to
learn almost nothing, and the work belonged inline.

Usage:
    delegation-audit.py                 # most recent session in this project
    delegation-audit.py --all           # every session in this project
    delegation-audit.py --project PATH  # a different working directory
    delegation-audit.py --json          # machine-readable

No arguments and no network. Reads only local transcripts.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Thresholds. Deliberately conservative — they should fire on genuine waste,
# not on every imperfect delegation.
LOW_LEVERAGE = 10        # below this, inline would likely have been cheaper
FAT_RETURN = 800         # tokens; above this the return was probably unbounded
TRIVIAL_TOOLS = 2        # a delegation that used this few tools did little


def approx_tokens(text: str) -> int:
    """Rough token count. Good enough for ratios; never quoted as exact."""
    return len(text) // 4


def project_dir(cwd: Path) -> Path:
    """Claude Code encodes the project path by replacing separators with '-'."""
    return Path.home() / ".claude" / "projects" / str(cwd.resolve()).replace("/", "-")


def read_agent(path: Path) -> dict | None:
    new = reread = tools = 0
    last_text = ""
    model = None
    for line in path.read_text(errors="replace").splitlines():
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if rec.get("type") != "assistant":
            continue
        msg = rec.get("message")
        if not isinstance(msg, dict):
            continue
        model = msg.get("model") or model
        usage = msg.get("usage") or {}
        new += (
            usage.get("input_tokens", 0)
            + usage.get("cache_creation_input_tokens", 0)
            + usage.get("output_tokens", 0)
        )
        reread += usage.get("cache_read_input_tokens", 0)
        content = msg.get("content")
        if isinstance(content, list):
            for block in content:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "tool_use":
                    tools += 1
                elif block.get("type") == "text" and block.get("text", "").strip():
                    last_text = block["text"]
    if new == 0 and not last_text:
        return None
    returned = approx_tokens(last_text)
    return {
        "id": path.stem.replace("agent-", "")[:14],
        "model": (model or "?").replace("claude-", "").replace("-20250929", ""),
        "tools": tools,
        "new_tokens": new,
        "cache_reread": reread,
        "returned": returned,
        "leverage": new / returned if returned else float("inf"),
    }


def verdict(a: dict) -> str:
    if a["returned"] == 0:
        return "no text returned — check whether it failed"
    if a["leverage"] < LOW_LEVERAGE and a["tools"] <= TRIVIAL_TOOLS:
        return "trivial: too small to delegate, do inline"
    if a["leverage"] < LOW_LEVERAGE:
        return "low leverage: returned nearly as much as it read"
    if a["returned"] > FAT_RETURN:
        return f"unbounded return ({a['returned']} tok): cap the output format"
    return "ok"


def sessions_for(pdir: Path, every: bool) -> list[Path]:
    if not pdir.is_dir():
        return []
    dirs = [d for d in pdir.iterdir() if d.is_dir() and (d / "subagents").is_dir()]
    dirs.sort(key=lambda d: d.stat().st_mtime, reverse=True)
    return dirs if every else dirs[:1]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--all", action="store_true", help="every session, not just the latest")
    ap.add_argument("--project", default=".", help="working directory of the project")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    pdir = project_dir(Path(args.project))
    sessions = sessions_for(pdir, args.all)
    if not sessions:
        print(f"No subagent transcripts under {pdir}.")
        print("Either this project has spawned no subagents, or the retention")
        print("period (cleanupPeriodDays, 30 by default) has expired.")
        return 1

    agents: list[dict] = []
    for s in sessions:
        for f in sorted((s / "subagents").glob("agent-*.jsonl")):
            a = read_agent(f)
            if a:
                a["session"] = s.name[:8]
                agents.append(a)

    if not agents:
        print("Transcripts found but none contained usable usage data.")
        return 1

    agents.sort(key=lambda a: a["leverage"])

    if args.json:
        json.dump({"agents": agents}, sys.stdout, indent=2)
        print()
        return 0

    total_new = sum(a["new_tokens"] for a in agents)
    total_ret = sum(a["returned"] for a in agents)
    total_reread = sum(a["cache_reread"] for a in agents)

    print()
    print(f"  Delegation audit — {len(agents)} agent(s) across {len(sessions)} session(s)")
    print()
    print(f"  {'agent':<15} {'model':<12} {'tools':>5} {'absorbed':>11} {'returned':>9} {'leverage':>9}")
    print(f"  {'-'*15} {'-'*12} {'-'*5} {'-'*11} {'-'*9} {'-'*9}")
    for a in agents:
        lev = "inf" if a["leverage"] == float("inf") else f"{a['leverage']:.0f}x"
        print(f"  {a['id']:<15} {a['model'][:12]:<12} {a['tools']:>5} "
              f"{a['new_tokens']:>11,} {a['returned']:>9,} {lev:>9}")

    print()
    print(f"  {'TOTAL':<15} {'':<12} {'':>5} {total_new:>11,} {total_ret:>9,} "
          f"{(total_new/total_ret if total_ret else 0):>8.0f}x")
    print()
    print(f"  Main context paid {total_ret:,} tokens for {total_new:,} tokens of material.")
    if total_ret:
        print(f"  Reading that inline would have cost roughly {total_new // max(total_ret,1)}x more context.")

    flagged = [(a, verdict(a)) for a in agents]
    problems = [(a, v) for a, v in flagged if v != "ok"]
    print()
    if problems:
        print("  Worth changing:")
        for a, v in problems:
            print(f"    {a['id']}  {v}")
    else:
        print("  No wasteful delegations found.")

    print()
    print(f"  Note: 'absorbed' counts new input plus output and excludes {total_reread:,}")
    print("  tokens of cache re-reads, which are the same context re-processed across")
    print("  turns. Token counts are approximate (chars/4) — treat the ratios as the")
    print("  signal, not the absolute numbers.")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
