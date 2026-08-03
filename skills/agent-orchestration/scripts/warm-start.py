#!/usr/bin/env python3
"""Generate a briefing that removes a subagent's orientation cost.

THE PROBLEM

A subagent starts blind. Before it can do the work you asked for, it has to
discover where things live: what stack this is, which directory holds what,
how to build and test, what the entry points are. That discovery costs ten to
thirty tool calls, and it is pure waste for two reasons:

  1. Every agent in a fleet re-derives the SAME map, in parallel, separately.
  2. None of it needs a language model. Where files live is a fact you can
     compute.

THE FIX

Compute the map once, deterministically, and hand it to every agent as a file
they read first. Orientation collapses from ~15 tool calls to one Read.

Three properties make this work rather than just move the cost around:

  * Deterministic. No LLM builds it, so it is free and reproducible.
  * Byte-stable. Everything is sorted, so regenerating an unchanged repo
    produces an identical file — which keeps it prompt-cache friendly across
    agents instead of invalidating on every run.
  * Small. Hard-capped, because a briefing that costs more than the search it
    replaces is not a fix.

Usage:
    warm-start.py                  # write .claude/briefing.md for this repo
    warm-start.py --path REPO
    warm-start.py --stdout         # print instead of writing
    warm-start.py --max-tokens N   # budget, default 2000

Then tell agents, once, in their system prompt:
    "If .claude/briefing.md exists, read it before searching. It is your map."
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "site-packages", "dist", "build",
    ".next", ".output", ".vercel", "__pycache__", ".pytest_cache", ".turbo",
    "coverage", ".cache", "target", "vendor", ".gradle", ".idea", ".claude",
}
CODE_EXT = {
    ".ts": "TypeScript", ".tsx": "TypeScript", ".js": "JavaScript",
    ".jsx": "JavaScript", ".py": "Python", ".go": "Go", ".rs": "Rust",
    ".rb": "Ruby", ".java": "Java", ".kt": "Kotlin", ".swift": "Swift",
    ".php": "PHP", ".cs": "C#", ".vue": "Vue", ".svelte": "Svelte",
}


def walk(root: Path):
    """Yield code files, skipping vendored and generated trees."""
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.suffix in CODE_EXT:
            yield p


def detect_stack(root: Path) -> list[str]:
    out = []
    pkg = root / "package.json"
    if pkg.is_file():
        try:
            data = json.loads(pkg.read_text())
        except Exception:
            data = {}
        deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
        markers = [
            ("next", "Next.js"), ("react", "React"), ("vue", "Vue"),
            ("svelte", "Svelte"), ("@tanstack/react-router", "TanStack Router"),
            ("expo", "Expo / React Native"), ("react-native", "React Native"),
            ("vite", "Vite"), ("tailwindcss", "Tailwind"), ("express", "Express"),
            ("fastify", "Fastify"), ("jest", "Jest"), ("vitest", "Vitest"),
        ]
        found = [label for key, label in markers if key in deps]
        if found:
            out.append("JS/TS: " + ", ".join(sorted(found)))
        pm = "npm"
        if (root / "bun.lock").is_file() or (root / "bunfig.toml").is_file():
            pm = "bun"
        elif (root / "pnpm-lock.yaml").is_file():
            pm = "pnpm"
        elif (root / "yarn.lock").is_file():
            pm = "yarn"
        out.append(f"package manager: {pm}")
    if (root / "pyproject.toml").is_file():
        txt = (root / "pyproject.toml").read_text(errors="replace")
        fw = [f for f in ("fastapi", "django", "flask", "pydantic") if f in txt.lower()]
        out.append("Python" + (": " + ", ".join(sorted(fw)) if fw else ""))
    for f, label in (("go.mod", "Go"), ("Cargo.toml", "Rust"), ("Gemfile", "Ruby")):
        if (root / f).is_file():
            out.append(label)
    return out


def detect_commands(root: Path) -> list[tuple[str, str]]:
    cmds: list[tuple[str, str]] = []
    pkg = root / "package.json"
    if pkg.is_file():
        try:
            scripts = json.loads(pkg.read_text()).get("scripts", {})
        except Exception:
            scripts = {}
        runner = "bun run" if (root / "bun.lock").is_file() else "npm run"
        for key in ("typecheck", "build", "test", "lint", "dev", "preflight"):
            for name, body in sorted(scripts.items()):
                if name == key or name.startswith(key + ":"):
                    cmds.append((f"{runner} {name}", body[:60]))
                    break
    if (root / "pyproject.toml").is_file():
        cmds.append(("pytest", "test suite"))
    if (root / "Makefile").is_file():
        for line in (root / "Makefile").read_text(errors="replace").splitlines():
            m = re.match(r"^([a-zA-Z][\w-]*):(?!=)", line)
            if m and m.group(1) not in ("PHONY",):
                cmds.append((f"make {m.group(1)}", ""))
            if len(cmds) > 12:
                break
    return cmds[:12]


def dir_map(root: Path, files: list[Path]) -> list[tuple[str, int, str]]:
    """Second-level directory map: path, file count, dominant language."""
    buckets: dict[str, list[Path]] = {}
    for f in files:
        rel = f.relative_to(root)
        parts = rel.parts[:-1]
        key = "/".join(parts[:2]) if parts else "."
        buckets.setdefault(key, []).append(f)
    rows = []
    for key in sorted(buckets):
        group = buckets[key]
        lang = Counter(CODE_EXT.get(p.suffix, "?") for p in group).most_common(1)[0][0]
        rows.append((key, len(group), lang))
    rows.sort(key=lambda r: (-r[1], r[0]))
    return rows


def entry_points(root: Path, files: list[Path]) -> list[str]:
    names = {"main", "index", "app", "server", "cli", "__main__", "_app", "root"}
    out = []
    for f in files:
        if f.stem in names and len(f.relative_to(root).parts) <= 3:
            out.append(str(f.relative_to(root)))
    return sorted(out)[:10]


def gotchas(root: Path) -> list[str]:
    g = []
    if (root / "bun.lock").is_file() and (root / "package-lock.json").is_file():
        g.append("Two lockfiles present (bun.lock + package-lock.json) — dependency graphs can drift.")
    for cfg in ("eslint.config.js", "eslint.config.mjs", ".eslintrc.json"):
        p = root / cfg
        if p.is_file():
            txt = p.read_text(errors="replace")
            missing = [d for d in (".vercel", "dist", ".next", ".output")
                       if (root / d).exists() and d not in txt]
            if missing:
                g.append(f"{cfg} does not ignore {', '.join(missing)} — lint will crawl build output and hang.")
            break
    if (root / ".env").is_file():
        g.append(".env exists locally and is not in git — never print or commit its contents.")
    return g


def git_facts(root: Path) -> list[str]:
    def run(*a):
        try:
            return subprocess.run(a, cwd=root, capture_output=True, text=True,
                                  timeout=5).stdout.strip()
        except Exception:
            return ""
    out = []
    br = run("git", "branch", "--show-current")
    if br:
        out.append(f"branch: {br}")
    return out


def build(root: Path, max_tokens: int) -> str:
    files = list(walk(root))
    L: list[str] = []
    L.append(f"# Repository briefing — {root.name}")
    L.append("")
    L.append("Generated map of this repository. Read this before searching: it")
    L.append("answers where things live, so you do not have to grep for it.")
    L.append("Regenerate with `warm-start.py` when the structure changes.")
    L.append("")

    stack = detect_stack(root)
    if stack:
        L.append("## Stack")
        L.extend(f"- {s}" for s in stack)
        L.append("")

    cmds = detect_commands(root)
    if cmds:
        L.append("## Commands")
        for c, desc in cmds:
            L.append(f"- `{c}`" + (f" — {desc}" if desc else ""))
        L.append("")

    rows = dir_map(root, files)
    if rows:
        L.append(f"## Layout ({len(files)} source files)")
        for path, n, lang in rows[:22]:
            L.append(f"- `{path}/` — {n} files, {lang}")
        if len(rows) > 22:
            L.append(f"- (+{len(rows)-22} smaller directories)")
        L.append("")

    eps = entry_points(root, files)
    if eps:
        L.append("## Entry points")
        L.extend(f"- `{e}`" for e in eps)
        L.append("")

    g = gotchas(root)
    if g:
        L.append("## Known traps")
        L.extend(f"- {x}" for x in g)
        L.append("")

    gf = git_facts(root)
    if gf:
        L.append("## Git")
        L.extend(f"- {x}" for x in gf)
        L.append("")

    L.append("## Excluded from this map")
    L.append("- " + ", ".join(sorted(SKIP_DIRS)))
    L.append("")
    L.append("Anything not listed above is genuinely absent or vendored. If you")
    L.append("cannot find something here, search — but search narrowly.")

    text = "\n".join(L) + "\n"
    if len(text) // 4 > max_tokens:
        keep = max_tokens * 4
        text = text[:keep].rsplit("\n", 1)[0] + "\n\n(briefing truncated to fit budget)\n"
    return text


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--path", default=".")
    ap.add_argument("--stdout", action="store_true")
    ap.add_argument("--max-tokens", type=int, default=2000)
    args = ap.parse_args()

    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"Not a directory: {root}", file=sys.stderr)
        return 1

    text = build(root, args.max_tokens)

    if args.stdout:
        print(text)
        return 0

    out = root / ".claude" / "briefing.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    previous = out.read_text() if out.is_file() else None
    out.write_text(text)
    status = "unchanged" if previous == text else ("updated" if previous else "created")
    print(f"{status}: {out}  (~{len(text)//4} tokens)")
    if status == "unchanged":
        print("Byte-identical to the previous run — stays prompt-cache friendly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
