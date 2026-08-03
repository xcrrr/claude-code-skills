---
name: preflight
description: >
  Run the verification gate before calling work done or deploying: type check,
  build, lint, tests, and the traps that commonly hide in scaffolded projects.
  Load before saying a change is finished, before any deploy, and whenever
  asked to "check it works", "verify", "is it ready", or "ship it".
when_to_use: >
  Finishing a change in any repo, preparing a deploy, or reporting that work is
  complete.
---

# Preflight

Nothing is done on the strength of looking done. Run the gate, show the
evidence, then say what happened.

## The gate

Run in this order and stop at the first failure — a type error makes the build
and lint output noise.

```bash
npx tsc --noEmit          # or: bun run typecheck
npm run build             # or: bun run build / vite build
npm run lint              # or: bun run lint
npm test                  # if the project has a suite
```

Detect the runner from the repo rather than assuming: `bun.lock` or
`bunfig.toml` means `bun`, `pnpm-lock.yaml` means `pnpm`, `package-lock.json`
means `npm`. For Python, look for `pyproject.toml` and use `pytest`. If
`.claude/briefing.md` exists it already lists the real commands.

Report the actual result. "Build passed" without the exit line is not evidence.

## Traps worth checking first

**Lint that hangs.** A scaffolded `eslint.config.js` often omits the build
output directory from `ignores`. Lint then crawls thousands of generated files
and an eight-second run becomes several minutes. If lint hangs, check this
before anything else:

```js
{ ignores: ['dist', '.vercel', '.next', '.output', 'node_modules'] }
```

Because it comes from the template, every project scaffolded the same way
inherits it — fix it in the repo rather than waiting it out.

**Two lockfiles.** `bun.lock` alongside `package-lock.json` means two
dependency graphs that can drift. Report it; do not silently delete one.

**Undeclared transitive dependencies.** A module that resolves only because a
package manager hoisted it will break on a clean install. If something is
imported but absent from the manifest, say so rather than letting it pass.

## Before any deploy

Deploying is outward-facing and hard to retract. Confirm all four:

1. The gate above passes.
2. **Indexing and visibility are intentional.** If the project is held behind a
   `noindex` or a preview flag, do not lift it to "make the deploy work" —
   that is a launch decision, not a build step.
3. The target project is the intended one. Projects sharing a scaffold look
   alike, and deploy CLIs remember the last one.
4. Nothing fabricated ships: no invented statistics, testimonials, credentials,
   or client logos.

Point 4 is a correctness requirement, not a style preference.

## Content parity, when rebuilding an existing site

When a rebuild is meant to preserve existing content, verify phrase by phrase
rather than by impression: take distinctive sentences from the live page and
confirm each appears in the rebuild. Commit that check as a script instead of
re-deriving it per project.

Report parity as a count and a list of misses, never as "content matches".

## Native and mobile

Use the project's own preflight scripts if it has them — they usually encode
which gaps block distribution and which are acceptable in development. Do not
invent a parallel checklist.

**Nothing is verified on-device until it has run on the device.** A green build
is not a demonstration. Say which of the two you have.

Signing material — keystores, provisioning profiles, `*.properties` files
holding credentials — is owner-only and often unrecoverable. Never move,
regenerate, or delete it.

## Reporting

State the commands you ran, their results, and what remains unverified. If a
step was skipped, say which and why. A gate reported as passing when it was
never run is worse than no gate.
