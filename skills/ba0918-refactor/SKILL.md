---
name: ba0918-refactor
description: "Refactor existing code the person names — a file, a directory, a symbol, or the last N commits — improving how it reads while keeping its behavior identical, and optionally carrying the same improvement to similar code elsewhere. Edits run only when the person asks to refactor a named scope, only on sites whose behavior a test, type check, or other runnable check can confirm; similar code outside the scope, new characterization tests, and scopes with uncommitted changes are touched only after the person agrees. Use when the user says refactor this, clean this up, tidy this module, make this more readable, simplify this without changing behavior, or fix the similar code too. Not for fixing bugs or changing behavior. 日本語キーワード: リファクタリング 整理して 読みやすく 挙動を変えずに きれいにして 直近Nコミット 似たコードも直して"
---

# Refactor

## Scope

Applies when the person asks to improve the expression of existing code in a scope they name,
without changing what the code does: its inputs and outputs, side effects, error behavior, and
the order in which those happen.

It does not cover:

- Fixing a bug or changing behavior. A bug found here is reported, never fixed (step 7).
- Deciding what good structure is. That is the skill `ba0918-design`; this skill applies such
  judgments to code that already exists, one behavior-preserving step at a time.
- Read-only analysis of a codebase or a cause. That is the skill `ba0918-investigate`.
- A quick tidy-up of the change just written. A built-in diff tidy-up command, where the
  environment provides one, fits that better; this skill is for code the person points at,
  whenever it was written.

## When edits may run

Edit files only when the person has asked to refactor a scope they named. Being loaded as a
candidate, or noticing messy code during other work, is not such a request: mention it and
stop.

Within a requested run, three kinds of change need the person's agreement first, because each
reaches beyond what they pointed at:

- adding a characterization test (a test that pins the current behavior) where no check exists;
- applying an improvement to similar code outside the named scope;
- touching a scope that already has uncommitted changes, which the refactor would mix with.

When agreement cannot be obtained — the run is unattended, or the person is unavailable — do
not make those changes; list them in the report instead.

## Rules

- Change expression only. Inputs, outputs, side effects, error behavior, and ordering stay
  identical.
- Do not change code whose reason for being written that way you cannot state.
- Do not apply a transformation to a site that no runnable check covers.
- Do not fix a bug you find. Report it with a proposed issue; do not file it.
- Do not edit a test's assertions to make it pass. A test whose assertion would have to change
  is evidence of a behavior change: revert the transformation.
- Apply one improvement at a time and run the checks before the next one.
- Do not delete code that looks unused. Report it.
- Finishing with no change is a valid result when the code is already clear.

## Procedure

### 1. Fix the scope

The argument names the scope: a path, a glob, a symbol, or a range of history such as "the
last 5 commits", which expands to the files those commits changed. Quote paths when building
commands. With no argument, propose the files changed by the most recent commit and confirm.

Confirm that every path exists; if the scope cannot be resolved, stop and report why.

Tests inside the scope are not improvement targets. They are the means of checking the
refactor and stay as they are.

Leave out code that is temporary — a prototype, a throwaway script, code marked for removal —
and say so in the report. Effort spent there is wasted, and some code that looks temporary has
become load-bearing, which is one reason unused-looking code is reported rather than deleted.

When the scope is too large to understand in one pass, propose splitting it before reading
further. Read-only understanding of a large scope may be delegated to a subagent; editing stays
with this session.

Check the working tree. If files in the scope have uncommitted changes, ask before going on
(see "When edits may run").

### 2. Understand the code

For each target, establish:

- its responsibility, inputs and outputs, side effects, error behavior, and edge cases;
- who calls it and what it calls;
- why it is written the way it is, from the history of the lines (`git log --follow`,
  `git blame`) and nearby comments — a performance measure, a platform constraint, a past bug
  fix.

Leave out anything you cannot account for and record why: no history to explain it, dynamic
dispatch or reflection that hides callers, a public API or serialized format, generated or
vendored code, tests whose intent cannot be read.

### 3. Secure a check

For each remaining site, name the runnable check that would catch a behavior change: an
existing test, a type check, a build, a lint, or a characterization test.

Where none exists, propose a characterization test. Add it only with the person's agreement,
run it against the unchanged code, and treat it as fixed from then on. Where no check can be
had, the site is held and reported, not applied.

### 4. Choose improvements

If the person named the change ("rename this", "split this function"), that is the candidate.
Otherwise read `references/refactoring-catalog.md` and list candidates from it.

Keep a candidate only if someone new to the code would understand the result faster and more
accurately than the original. Line count is not the measure: a nested one-line conditional is
harder to read than the five-line version it replaced.

Classify each finding:

| Class | Meaning | Goes to |
|---|---|---|
| improve | expression can improve with behavior unchanged | steps 5–6 |
| bug | the value lies in correctness, security, or data loss | report, as a proposed issue |
| held | no runnable check, or performance-sensitive | report, with what the person would need to decide |
| out of scope | temporary, or not understood | report, with the reason |
| already clear | no improvement worth making | nothing |

If nothing is classified as improve, stop and report that the code is already clear, with the
reasons. No check run is required when nothing changed.

Before accepting a candidate that could change evaluation order, call counts, allocation, or
complexity, ask whether the site is performance-sensitive: a hot path, a benchmark target, a
comment recording a measurement. If it is, or you cannot tell, hold it — the simpler version
may be slower, and that needs measuring. A rename or comment change passes regardless.

### 5. Apply one improvement at a time

For each candidate, in turn:

1. Make the edit.
2. Run the checks named in step 3 for that site. A targeted run per improvement plus one full
   run at the end is acceptable on a large suite.
3. If they pass, move on. If they fail, or a test needs a changed assertion, revert this
   improvement and record it as held.

A rename or a move may require tests to follow a changed name or import path. Updating those
references is allowed; the assertions stay exactly as they were.

When one improvement would touch more lines than can be reviewed by hand, use a syntax-aware
rewrite tool if one is available. Textual replacement also rewrites matching text inside
strings and comments, so use it only as a last resort, after securing a revert point, and read
the whole resulting diff.

### 6. Similar code (only when asked)

Run this step when the person asked for similar code to be handled too, or offer it in the
report when an improvement plainly recurs nearby.

Read `references/similar-code.md`, then search for sites where the same improvement applies,
within the scope's language and related directories rather than the whole repository. Read
each site in full and judge it with that reference. Report the results; apply outside the named
scope only after the person agrees to the listed sites, one improvement at a time as in step 5.

### 7. Report

Tell the person:

- what was improved, per improvement: the site, the gist of before and after, and the checks
  run with their result;
- what was held and why, with what the person would need to decide;
- what was left out in steps 1–2, and why;
- similar code found, if step 6 ran: which sites were applied, which await agreement, which
  are uncertain and what would decide them, and which were judged not applicable and why;
- bugs found, each as a proposed issue title and body — the symptom, the location, and how to
  reproduce it if known. Filing it is the person's call;
- code that looks unused, by location, for the person to decide on;
- the evidence listed below.

When nothing changed, say so plainly and give the reasons; do not pad the list with weak
improvements to avoid an empty result.

## Judgment

**A refactor you cannot verify is a behavior change you have not noticed yet.** Refactoring is
safe only because something runnable says the behavior held. Without that, "obviously
equivalent" is a claim with no evidence behind it, which is why an uncovered site is held
rather than applied.

**Understand before you simplify.** Code often looks odd for a reason that is not visible in
the code: an ordering dependency, a workaround for a platform bug, a measured optimization.
Removing it without knowing the reason reintroduces the problem it solved.

**A bug fix hidden in a refactor makes both unreviewable.** A reviewer reading a refactor
checks that nothing changed; a bug fix is a change. Mixed together, neither can be checked, so
the bug goes to the person as a proposed issue.

**Consistency with the surrounding code beats a better style.** A local "improvement" that
breaks the project's conventions makes the codebase harder to read as a whole. Follow the
surrounding idiom.

**A named abstraction is not complexity.** A small function or wrapper that gives a concept a
name, or forms a test boundary, helps understanding. Inlining it to flatten the code usually
makes it worse.

**The scope is what the person agreed to review.** Similar code elsewhere may look identical
and still differ in context. Applying there unasked produces a diff larger than the person
expected and harder to review, which is why it waits for agreement.

**Deletion is the least reversible refactor.** Code that looks unused may be reached through
reflection, configuration, or an external caller, or may be a compatibility shim kept on
purpose. Reporting it costs little; deleting it wrongly can cost a lot.

## Examples

A refactor, and a behavior change passed off as one:

```
Good: nested if/else three levels deep → guard clauses; the order of side effects is unchanged,
      existing tests pass untouched.
Bad:  "simplified" by dropping a try/except that looked redundant; error behavior changed.
```

A worthless wrapper, and a named abstraction:

```
Inline: def get_user(id): return repo.get_user(id)   # adds nothing
Keep:   def is_eligible_for_refund(order): return order.paid and order.age_days < 30
```

A failing test after a transformation:

```
Bad:  change the expected value in the test so it passes again.
Good: revert the transformation and record the site as held.
```

## Evidence

The report carries these, rather than asserting the behavior was kept:

- **Checks**: for each improvement, the check command run and its output, with pass and fail
  counts; and the final full run if the suite was run per improvement.
- **Diff**: `git diff --stat` for the whole refactor.
- **Tests untouched**: `git diff` of test files, showing no changed assertions — only reference
  updates that follow a rename or move, if any.
- **Characterization tests**: for each one added, its run against the unchanged code, passing.
- **Held and excluded sites**: each with the reason, as file and line.
