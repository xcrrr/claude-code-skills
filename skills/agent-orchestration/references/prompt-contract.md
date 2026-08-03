# The delegation prompt contract

A subagent starts blind. It has its system prompt, `CLAUDE.md`, git status, and
the message you write — nothing else. No conversation history, no files you
read, no skills you loaded, no decisions you already made. `Explore` and `Plan`
don't even get `CLAUDE.md` or git status.

Every delegation prompt therefore carries four parts.

## The four parts

### 1. Objective

State the question or change so it is answerable with zero follow-up. If a
judgment call is required, make it now and state it as a given.

Bad: `Look into the auth stuff.`
Good: `Determine whether token refresh in src/auth/ handles clock skew, and
report the exact code path that would fail if the client clock is 5 minutes
behind the server.`

### 2. Output format

The single most important line. The agent's reply lands in the orchestrator's
context verbatim, so the format *is* the cost.

Recipes:

- `Return a table of file:line — symbol — one-line note. Max 20 rows. No prose.`
- `Return exactly three sections: FINDINGS, EVIDENCE (command + output), OPEN
  QUESTIONS. Under 400 words total.`
- `Return only the names of failing tests and their assertion messages. No
  stack traces, no commentary, no suggested fixes.`
- `Return JSON: {"safe": bool, "reason": str, "sites": [{"file": str, "line":
  int}]}. Nothing outside the JSON.`
- `Return one word: OK or FAIL, followed by at most two sentences if FAIL.`

If you don't specify, you get prose, and prose is the expensive default.

### 3. Tools and sources

Point at the right places and rule out the wrong ones. This is where you spend
the agent's effort budget.

`Search src/ and tests/ only. Ignore vendor/, node_modules/, and anything
under build/. Prefer git log -S over reading whole files. Use rg, not find.`

### 4. Boundaries

What is out of scope, and — when running a fleet — who owns what. Explicit
division of labour is the documented fix for agents duplicating each other's
searches and leaving gaps between them.

`You own the database layer only. Another agent covers the HTTP handlers and a
third covers migrations — do not read those directories. Do not propose fixes;
locating is the whole job.`

## Full example — one worker in a fleet of three

```
Objective: Report every place the application writes user personal data to
disk outside the approved store. "Personal data" means email, full name,
address, or phone. Treat src/storage/vault.ts as the approved store — writes
that go through it are fine.

Scope: You own src/services/ and src/api/ only. A second agent covers
src/workers/, a third covers src/jobs/. Do not read outside your two
directories.

Method: Grep for fs.write, createWriteStream, JSON.stringify into a file, and
logger calls that interpolate a variable. Read only the enclosing function for
each hit, not the whole file.

Output: A table — file:line | what is written | approved store? (yes/no).
Max 25 rows, ordered by file. No prose, no suggested fixes, no summary
paragraph. If you find nothing, return exactly: NO WRITES FOUND.
```

## Before/after

| Weak | Strong |
|---|---|
| `Find the bug.` | `A user reports login fails after session timeout. Reproduce by reading the token refresh path in src/auth/. Return the file:line where the failure originates and the one-sentence reason. Do not fix it.` |
| `Review my changes.` | `Review the diff on this branch against PLAN.md. Report only gaps that break correctness or a stated requirement — not style. Return one line per gap: file:line — what's missing. If none, return NO GAPS.` |
| `Research how X works.` | `Answer: how does the app decide a request is safe to forward to a third party? Read src/services/egressGate.ts and its callers. Return the decision rule as a numbered list, then the exact function that enforces it. Under 200 words.` |
| `Update all the API calls.` | `In services/api/client.py only, replace every requests.get call with the session.get helper defined at line 40. Preserve timeouts. Run pytest tests/test_client.py and report pass/fail. Return: files changed, test result, nothing else.` |

## Prompting an agent to be thorough vs fast

Effort frontmatter and the `effort` parameter are the real dial, but the prompt
reinforces it:

- Fast: `This is a targeted lookup. Stop as soon as you have the answer. Do not
  survey the codebase.`
- Thorough: `Be exhaustive. Check every call site, including tests and scripts.
  Before returning, re-read your findings and remove anything you did not
  verify by reading actual code.`

## Making a reviewer honest

Reviewers told to find problems will find them. Constrain:

`Flag only issues that cause incorrect behavior or violate a requirement listed
in PLAN.md. Do not report style, naming, or hypothetical future problems. For
each finding give a concrete failure scenario: specific inputs → wrong output.
If you cannot state one, do not report it.`

For high-stakes claims, run several verifiers with *different lenses*
(correctness, security, does-it-actually-reproduce) rather than several
identical ones — diversity catches failure modes redundancy cannot.
