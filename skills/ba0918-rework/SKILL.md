---
name: ba0918-rework
description: "Diagnose a scope of code the person names — a file, a directory, a symbol, or the last N commits — for bugs, design problems, performance problems, memory leaks, security problems, and mismatches with the written specification, then fix what it finds one item at a time, verifying each fix with tests and committing each as its own commit on a dedicated branch in a separate worktree. Unlike ba0918-refactor, it allows fixes that change behavior: it declares what changes and tests both what changes and what must not. Edits run only when the person names a scope and asks for it to be fixed; a request only to find or list problems is review or investigation, and problem code noticed during other work is pointed out, not fixed. Use when the user says rework this, find and fix the problems in this, diagnose and fix this directory, fix everything wrong with this module, or clean up the bugs in the last N commits. 日本語キーワード: 手直し 問題を見つけて直して 診断して直して まとめて直して 直近Nコミットを直して rework"
---

# Rework

## Scope

Applies when the person names a scope and asks for its problems to be fixed. The skill
diagnoses the scope, fixes each problem it finds — including fixes that change behavior — one
at a time, verifies each fix with tests, and commits each fix as its own commit on a dedicated
branch.

It does not cover:

- Diagnosis only. A request to find or list problems without fixing them is a review or an
  investigation, not this skill.
- Improving how code reads while keeping its behavior identical. That is the skill
  `ba0918-refactor`. Design problems fixed here are structural changes made to remove a
  problem, not small readability transformations.
- Merging, pushing, filing issues, or deleting the worktree. The person decides these after
  reading the report.
- Fixing anything outside the named scope, or running a flow to get agreement for doing so.
  The one exception is a specification document outside the scope that is fixed as part of an
  item whose code was decided to be right (see Rules).

**The top priority is not to add questions to the person.** When people are asked too often,
they approve without reading, and asking stops meaning anything. What can be decided from
measurement or from evidence inside the repository is decided here and acted on. In place of
up-front confirmation, two safety nets remain:

- Every fix is its own commit on a dedicated branch. A fix the person dislikes is undone by
  reverting that commit.
- The report carries the evidence behind each decision and the measured results.

### Terms

- **Specification**: what is written inside the repository — specification documents, the
  README, API documentation, promises written in docstrings or in types, and test names.
  Nothing outside the repository counts, and neither does what the code "obviously should" do
  without a written source.
- **Contract change**: a fix that changes an interface, the appearance of a user interface, or
  the design of stored data. It includes changing the shape of a public API, removing a public
  API, and rejecting input that the specification used to accept. It does not mean every change
  that could break something; an internal bug fix is not a contract change.
- **Ask item**: an item the person is asked about — a contract change, or an item whose correct
  behavior cannot be decided from evidence inside the repository. Nothing else is asked.
- **Spec test**: a test that states how a behavior should be, written from evidence (the
  specification, the callers, the history). One written for a behavior the item changes is
  seen failing before the fix. A scaffold test promoted because it agrees with the evidence is
  also a spec test; it pins a behavior that does not change, so it has no failing run. Spec
  tests are committed.
- **Scaffold test**: a test that temporarily pins current behavior where no test protects the
  behavior that must not change, to catch an undeclared change during a fix. It is not
  committed, unless it is promoted to a spec test.

### Inputs

| Input | Required | Meaning |
|---|---|---|
| Scope | yes | A file, a directory, a symbol, or "the last N commits" (expanded to the files those commits changed) |
| Perspectives | no | Which of the six perspectives to look at (for example, security only). Default: all six |
| Advance permission | no | Permission to proceed on ask items without asking (see Rules) |

If the scope cannot be resolved — a path does not exist, a symbol cannot be found — change
nothing and return the reason.

If the scope is too large to hold in mind at once, propose a split and stop. Stopping partway
through a scope leaves it unclear what was fixed and what was not. Draw no fixed line such as a
line count: while diagnosing, if you judge before finishing the files in scope that you can no
longer retain what you have read, stop and write that reason into the split proposal. There is
no upper limit on the number of items fixed.

When the scope is large, the read-only diagnosis may be handed to an agent running in a
separate context. Editing files always stays with the session that was invoked.

## When edits may run

Edit files only when the person has named a scope and asked for it to be fixed. Do not edit in
these cases:

- The person asked only to find or list problems ("find the problems in this", "list what is
  wrong"). That is the job of a review or an investigation; answer without changing files or
  creating a branch.
- You noticed problematic code while doing other work. Point it out and stop.

## Rules

### What to ask and what to decide

- Ask the person only about ask items: (1) contract changes, and (2) items whose correct
  behavior cannot be decided from evidence inside the repository.
- Fix every other behavior change without asking, and state the evidence. Evidence is the
  specification (see Terms), what the callers expect, the tests, and the history of the
  change.
- When the code and the specification disagree, decide which is right if the evidence settles
  it. An item becomes kind (2) only when the sources of evidence contradict each other and
  nothing says which one takes precedence. When the code is decided to be right, fix the
  specification document as part of the same item, even when that document is outside the
  scope, and say so in the report. This is the only edit allowed outside the scope: a document
  left wrong keeps the mismatch and lets the same problem come back.
- A security fix that rejects input is not a contract change when that input was never valid
  under the specification (an injection string, a value outside the declared type's range). It
  is a contract change when the specification accepted that input.
- A design fix that changes the shape of a public API, and the removal of a public API, are
  contract changes.
- Ask all ask items once, together, after every other item has been fixed. Give each one what
  would change, the evidence, and your recommendation. When the answers come, fix the items
  right away, in the same run.
- An item that depends on an ask item (see the fix order) waits for that answer and goes last.
  Once answered, fix the base item, then the dependent one. If the answer is "do not fix",
  fix the dependent item in a way that leaves the base unchanged if you can; otherwise hold
  it.
- Advance permission comes in two forms: per kind of contract change (interface, user interface
  appearance, data design), or "everything as recommended". Proceed on the ask items it covers
  as recommended, without asking. "Everything as recommended" also covers items whose correct
  behavior the evidence could not decide.
- In a run where no one can answer — an unattended run, or the caller says so — do not fix the
  ask items that advance permission does not cover. Report them with your recommendation. Hold
  the items that depend on them too, and report the dependency.

### Tests

- For each behavior you change, write a spec test first and see it fail before the fix. It is
  part of that item's commit.
- Where no existing test protects a behavior that must not change, write a scaffold test that
  pins the current behavior, and use it only to watch for undeclared changes during the fix.
  Do not commit it; delete it when the item is done. If a scaffold test agrees with the
  evidence of the specification, promote it to a spec test, include it in that item's commit,
  and say so in the report.
- Change an existing test's expected value only where it covers the change you declared. If an
  expected value outside the declared change would have to change, treat it as an unintended
  change: discard the item's uncommitted changes and hold it. Updating names or import paths
  in tests to follow a rename or a move is not a change of expected value and is allowed.
- If a fix to code that affects behavior can be covered by neither a spec test nor a scaffold
  test, do not fix it; hold it. This does not apply to an item that only fixes a specification
  document, which is verified by comparing the document with the code, nor to a deletion, which
  is verified by the checks for deletion. Report that verification.

### Items that need measurement

- Performance and memory fixes leave results unchanged, so passing tests do not show they
  worked. Compare before and after: the number of queries, a timing, the trend of memory use
  over repetitions. You may build a temporary means of measurement for this; like a scaffold
  test, it is never committed. If you cannot compare, hold the item.
- Changing how a user interface looks is a contract change, so fix it only after an answer or
  advance permission. Then capture the screen before and after and compare them, to confirm
  that the only visible change is the declared one. Show the captures in the report; do not
  wait for the person to confirm them. If there is no way to capture the screen, hold the item.

## Procedure

### 1. Fix the scope

Resolve the scope the person named. "The last N commits" expands to the files those commits
changed. If the scope cannot be resolved, change nothing and return the reason (see Inputs).

If the original working tree has uncommitted changes, do not ask about them and do not touch
them. They are outside the diagnosis: read the files in scope as committed at `HEAD` (for
example `git show HEAD:<path>`), and say in the report that the uncommitted changes were not
diagnosed.

### 2. Diagnose (read only)

Diagnosis only reads. It creates no branch and changes no file.

Look at the scope under each perspective the person asked for — all six by default. Before
looking under a perspective, read its guide; when the perspectives are narrowed, read only the
guides for the ones being looked at:

| Perspective | Guide |
|---|---|
| Bugs | `references/bugs.md` |
| Design problems (mixed responsibilities, dependencies pointing the wrong way) | `references/design.md` |
| Performance problems (N+1 queries and similar) | `references/performance.md` |
| Memory leaks | `references/memory-leaks.md` |
| Security problems | `references/security.md` |
| Mismatches with the specification | `references/spec-mismatch.md` |

Each guide lists typical signs of the problem and the typical ways a fix leaks a behavior
change beyond what was declared.

When the scope is large, this read-only diagnosis may be handed to an agent in a separate
context; the findings come back to this session, which does all the editing. If, before
finishing the files in scope, you judge that you can no longer retain what you have read, stop
and propose a split with that reason (see Inputs).

For each item, record its perspective, its location, the evidence, whether it is an ask item,
and whether it is data destruction — an item that, left unfixed, loses or corrupts stored
data. Data destruction is an attribute any item can carry, not a perspective.

When you find the same problem outside the scope, do not fix it. Record its location for the
report, as a proposed issue. Fixing it would make the diff larger than the person expected to
review; they can call this skill again with that scope.

An item inside the scope that cannot be fixed without changing callers outside the scope is
held and reported. The one edit allowed outside the scope is a specification document fixed
as part of an item whose code was decided to be right (see Rules).

If there is nothing to fix, skip to the report: no branch or worktree is created.

### 3. Create the branch and the worktree

Only now, with at least one item to fix, create a new branch `rework/<timestamp>` in a new
worktree made from `HEAD`. Place the worktree next to the repository, in the same parent
directory, named `<repository name>-rework-<timestamp>`. Use one timestamp for both names, in
a form valid in a branch name, such as `20260925-143012`:

```
git worktree add -b rework/20260925-143012 ../myrepo-rework-20260925-143012 HEAD
```

Do not place the worktree in a temporary directory: it is left in place for the person after
the run, and a temporary directory may be cleaned away.

Do all further work inside the new worktree. Never touch the original working tree, during the
run or after it: do not switch its branch, do not stash its changes, do not commit to its
branch.

Do not merge or push the branch, and do not remove the worktree. The run ends with the branch
name and the worktree location in the report.

### 4. Install and take the baseline

A new worktree has no installed dependencies and no build output. Run the project's install
steps there, then run the project's full test suite once. This run is the baseline: record the
command, the output, and the pass and fail counts, and note every test that already fails.
Tests failing at the baseline are not a reason to hold an item.

A **new failure**, from here on, means a test that passed at the baseline and now fails.

If the full test suite still cannot be run after installing, fix nothing. Report the reason
and stop, leaving the empty branch and the worktree in place.

### 5. Order the items

If one item's fix rewrites the code another item's fix would change, the first is the base:
fix it first. Otherwise, fix in order of importance:

1. data destruction and security problems;
2. bugs;
3. mismatches with the specification;
4. performance problems and memory leaks;
5. design problems.

Ask items are not fixed in this pass; they wait for step 7, along with the items that depend
on them.

### 6. Fix the other items one at a time

For each item that is not an ask item, in order:

1. Declare what will change. If nothing observable changes, declare that nothing changes.
2. If the item changes behavior, write the spec test and see it fail. An item declared to
   change nothing — a design, performance, or memory fix — gets no failing spec test. Where
   needed, write scaffold tests (see Rules).
3. For a performance or memory item, take the measurement before the fix; for a user
   interface item, capture the screen before the fix (see Items that need measurement).
4. Make the fix.
5. Run the tests that cover the files this item changed, and the project's checks such as a
   type check or a build. If you cannot narrow the tests to those files, run the full suite.
   For an item measured or captured in 3, take the same measurement or capture again and
   compare.
6. If they pass, first delete the scaffold tests that were not promoted and any temporary
   measurement code, so that neither is ever committed. Then commit this item alone as one
   commit. Follow the project's commit message conventions.
7. If there is a new failure outside the declared change, discard this item's uncommitted
   changes and delete its scaffold tests, hold the item, and record which test failed and why.
   Move on to the next item.

After each item, re-check whether the remaining items still hold. An item that another fix
removed is recorded as resolved by that fix, not fixed again.

**Deletion.** Unused code may be deleted when you have confirmed it cannot be reached: a
search for its references finds none; nothing reaches it dynamically (a name built from a
string, reflection, configuration, a plugin registry); and it is not a public API. Removing a
public API is a contract change and an ask item. Code you cannot fully confirm is not deleted;
report it, as a proposed issue. Record what you checked for each deletion; that record is the
deletion's verification.

### 7. Ask the ask items together, then fix them

When every other item is done, fix the ask items that advance permission covers as
recommended, without asking, with the same steps as step 6. Ask the ask items that advance
permission does not cover, all at once (see Rules), and fix the answered items with the same
steps as step 6. Base items go before the items that depend on them. In a run where no one can
answer, leave the ask items that advance permission does not cover unfixed, together with the
items that depend on them, and carry them to the report with your recommendation.

### 8. Run the full suite again

Run the full test suite once more in the worktree. If there is a new failure:

1. Find the commit that caused it by bisecting this branch's commits, from the commit the
   branch started at (good) to the branch tip (bad), with `git bisect`. Once it is found, end
   the bisect with `git bisect reset` so that the worktree is back on the branch tip.
2. Revert that commit together with the later commits that depend on it (those that rewrite
   code it changed), newest first, with `git revert`. Hold every item whose commit was reverted.
3. Run the full suite again. If a new failure remains, repeat from 1.

The original commits and their reverts both stay in the history.

### 9. Report

Report every category below. Write "none" for a category with nothing in it rather than leaving
it out.

- **Fixed items**, each with: its perspective; what changed; the evidence; its spec test; the
  measurements before and after (performance, memory, user interface captures); its commit.
- **Ask items**: what was asked and the answer. In a run where no one could answer, list them
  with your recommendation. An item the answer decided not to fix also goes into the proposed
  issues.
- **Held items**: the reason, and what fixing them would need.
- **Proposed issues**, each as a title and a body: items not fixed, the same problem found
  outside the scope (with its location), and code whose deletion could not be confirmed.
  Filing them is the person's decision; do not file them.
- **Items resolved by another fix**, naming that fix.
- **Scaffold tests**: each by name, and whether it was deleted or promoted to a spec test.
- **Branch and worktree**: the branch name and the worktree location, if they were created.
- **Full test runs** at the baseline and at the end: the command, the output, and the pass and
  fail counts.

Also say whether the original working tree had uncommitted changes that were outside the
diagnosis.

When no problem was found, or every item ended up held, that is a correct result: report it as
it is. Say that no branch was created, or that the branch was left empty. Do not add items that
are not real problems to fill the report.

With the report and the branch, the person decides whether to take the branch in, which
commits to revert, and which proposed issues to file.

## Judgment

**Every question spends the person's attention.** When most fixes wait for approval, people
stop reading and approve everything, and the one question that mattered gets the same glance.
That is why only ask items are asked, and why the rest are decided from evidence and made safe
by one commit per item and a report that shows the evidence.

**Ask once, at the end.** Stopping at each ask item leaves the run half done while waiting, and
spreads the person's attention over many interruptions. Fixing everything else first also means
the questions arrive with the rest of the work already settled, so each answer can be acted on
at once.

**A contract is what others rely on without reading the code.** Callers outside the scope,
users, and stored data depend on interfaces, what a screen looks like, and the shape of data.
A change there cannot be judged from inside the repository alone, which is why it is asked
about. A wrong result that its own callers never wanted is not a contract; fixing it is the
point of this skill.

**A test written after the code only records the code.** It pins what the code does now, right
or wrong, so keeping it would present the current behavior as the specification. A spec test is
written from evidence before the fix and fails first; that failure is what shows it tests the
change. Scaffold tests exist only to catch undeclared changes during a fix, so they go when the
item is done.

**Results that do not change need a measurement.** A performance or memory fix passes the same
tests as the code it replaced. Without numbers from before and after, "faster" or "no longer
leaks" is a claim with nothing behind it.

**A separate worktree removes the need to ask about the working tree.** The person's
uncommitted work and current branch stay exactly as they were, so there is nothing to confirm
before starting, and the fixes never mix with work in progress.

**The scope is the diff the person agreed to read.** The same problem elsewhere may sit in a
different context, and fixing it would grow the diff past what was expected, so it is reported
instead.

**An expected value that must change outside the declaration is a finding.** It means the fix
changed something it did not say it would. Editing the expectation to pass would hide exactly
the change the declaration exists to expose.

## Examples

Deciding or asking:

```
Decide: a function crashes on an empty list; every caller expects an empty result. Fix it,
        citing the callers, with a spec test that fails first.
Ask:    fixing a problem needs a new required parameter on a public function. Record it as an
        ask item and ask after everything else is fixed, with what changes, the evidence,
        and a recommendation.
Bad:    asking "may I fix this?" for every internal bug, or stopping to ask at each ask item.
```

A test after a fix:

```
Bad:  write the test against the fixed code and commit it as the specification.
Good: write the test from the callers' expectations, see it fail, then fix.
```

Deletion and the scope:

```
Good: delete a private function with no references, no dynamic lookup, no configuration entry;
      report the three checks.
Bad:  delete a function because a search finds no references, when handlers are looked up by a
      name built from a string.
Bad:  the same injection flaw exists in a file outside the scope; fix it there too.
Good: report its location as a proposed issue and leave it unchanged.
```

## Evidence

The report carries these, rather than asserting that the fixes are right:

- **Full test runs**: the baseline and the final run, each with the command, the output, and
  the pass and fail counts; tests already failing at the baseline are listed.
- **Spec tests**: for each changed behavior, the test's failing output from before the fix and
  its passing output after.
- **Measurements**: for performance and memory items, the numbers before and after; for user
  interface items, the captures before and after.
- **Commits**: one per item, listed with its item; reverted commits and their reverts, if the
  final run found a new failure.
- **Deletions**: for each, the reference search, the dynamic-reach check, and the public-API
  check.

What is left behind, and what is not:

- The branch and the worktree stay until the person removes them. This skill never deletes
  them.
- Scaffold tests and temporary measurement code live only in the worktree while their item is
  in progress. They are never committed.
