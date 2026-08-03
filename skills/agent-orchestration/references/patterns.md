# Orchestration patterns

Pick the shape that matches the work. Each entry states what it is for, how to
run it, and when it stops being worth it.

---

## 1. Parallel scout

**For:** a broad question where one search angle won't find everything.

Spawn 3–5 read-only agents in a **single message**, each attacking a different
angle — definitions, callers, tests, config, git history. Aggregate yourself.

Angles that don't overlap:
- by container (this directory / that directory)
- by content (this symbol / that error string)
- by entity (this model / that service)
- by time (`git log -S`, recent changes)

**Stops being worth it when:** the angles overlap. Two agents grepping the same
symbol in the same tree return the same rows twice and you pay for both.

---

## 2. Locate → act → verify

**For:** the standard "fix something in a codebase you haven't mapped" job.
The most-used pattern; treat it as the default.

1. One cheap read-only agent locates the sites. Output: `file:line` table.
2. You pick the sites. Hand **exact paths** to a worker.
3. A fresh reviewer audits the resulting diff.

Never skip step 1 and hand a worker a vague location — it burns its budget
searching and returns half a job.

---

## 3. Pipeline over a work-list

**For:** N independent items each needing the same multi-stage treatment
(migrate a file, audit an endpoint, triage a failing test).

Scout inline first to discover the list, then run each item through its stages
independently. Do not synchronize the stages: item A can be in stage 3 while
item B is in stage 1. Wall-clock is the slowest single item, not the sum of
slowest-per-stage.

Only put a barrier between stages when stage N genuinely needs *all* of stage
N−1 at once — deduplication across the full result set, an early exit if the
count is zero, or a prompt that compares findings against each other. "I need
to flatten the list first" is not a barrier; do that inside a stage.

---

## 4. Adversarial verify

**For:** a finding or a change whose wrongness would be expensive.

Spawn verifiers whose job is to **refute**, not confirm. Prompt them to default
to "refuted" when uncertain. Kill the finding if a majority refute it.

For anything with more than one failure mode, give each verifier a distinct
lens (correctness / security / does-it-reproduce) instead of running three
identical skeptics.

**Cost note:** this is the most expensive pattern per unit of output. Reserve
it for claims you would act on.

---

## 5. Writer / reviewer

**For:** implementation you want checked without your own bias leaking in.

The implementing agent finishes; a *fresh* agent sees only the diff and the
criteria — not the reasoning that produced the change — and reports gaps. The
implementer then fixes and re-reviews.

Fresh context is the entire point. A reviewer that watched the code being
written will rationalize it.

---

## 6. Fan-out migration

**For:** the same mechanical change across many files.

1. Produce the file list.
2. Test the transform prompt on 2–3 files yourself. Refine until clean.
3. Fan out one agent per file (or per small batch), each with the *refined*
   prompt and a hard scope of its own files.
4. Verify with a build or test run, not by reading diffs.

Use `isolation: "worktree"` only if the agents would otherwise write to the
same files. It costs setup time and disk per agent.

---

## 7. Loop until dry

**For:** discovery of unknown size — bugs, edge cases, dead code, leaks.

Keep spawning finders until K consecutive rounds return nothing new.
Deduplicate against everything **seen**, not everything **confirmed** —
otherwise rejected findings resurface every round and the loop never converges.

A fixed "find 10 bugs" counter misses the tail; a dry-round counter doesn't.

---

## 8. Completeness critic

**For:** the end of a research or audit task.

One final agent asks: what's missing? Which search angle was never run, which
claim was never verified, which source was never read? Its answer is the next
round of work, or your evidence that there isn't one.

---

## Choosing between them

| Situation | Pattern |
|---|---|
| Don't know where the code is | Parallel scout, then locate→act→verify |
| Know where it is, one change | Inline. No agent. |
| Same change, many files | Fan-out migration |
| Multi-stage work over a list | Pipeline |
| Result would be costly if wrong | Adversarial verify |
| Just wrote something risky | Writer/reviewer |
| Unknown number of problems | Loop until dry |
| Think you're done | Completeness critic |

## Composition

These stack. A real audit is often: scout (find the surface) → pipeline (one
finder per area) → dedup inline → adversarial verify (per finding) →
completeness critic. Run the phases in sequence and read each result before
choosing the next — staying in the loop between phases is what keeps a large
fan-out from producing confident nonsense.

## Sequencing rule

Scout inline, then fan out. You do not need to know the shape of the work
before the *task* — only before the *orchestration step*. Discovering the
work-list yourself and then pipelining over it beats guessing the list up front.
